#!/usr/bin/env python3
"""
Error-Category Classifier via SentenceEmbeddings + FAISS

Usage:
  # 1) Initial build from a CSV of labeled errors:
  python error_cat.py --mode build --data_file errors.csv

  # 2) Classify new errors (one per line) in plain text:
  python error_cat.py --mode classify --input_file to_classify.txt

  # 3) Add more labeled examples without rebuilding everything:
  #    each line in new_examples.txt is ERROR_TEXT|CATEGORY
  python error_cat.py --mode update --input_file new_examples.txt
"""

import os
import argparse
import pickle

import numpy as np
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer
from collections import Counter

# defaults for persistence
INDEX_PATH   = "error_index.faiss"
MAPPING_PATH = "id_to_label.pkl"
EMB_MODEL    = "all-MiniLM-L6-v2"    # your MiniLM model of choice

def build_index(texts, labels, model):
    # embed + normalize
    emb = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    faiss.normalize_L2(emb)
    dim = emb.shape[1]

    # flat index with inner-product = cosine similarity on normalized vectors
    index = faiss.IndexFlatIP(dim)
    index.add(emb)

    return index, list(labels)

def save_index(idx, path):      faiss.write_index(idx, path)
def load_index(path):           return faiss.read_index(path)
def save_mapping(m, path):
    with open(path, "wb") as f: pickle.dump(m, f)
def load_mapping(path):
    with open(path, "rb") as f: return pickle.load(f)

def update_index(new_texts, new_labels, index, mapping, model):
    emb = model.encode(new_texts, show_progress_bar=False, convert_to_numpy=True)
    faiss.normalize_L2(emb)
    index.add(emb)
    mapping.extend(new_labels)
    return index, mapping

def classify(texts, index, mapping, model, top_k=5):
    emb = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    faiss.normalize_L2(emb)
    D, I = index.search(emb, top_k)

    preds = []
    for neigh_ids in I:
        neigh_labels = [mapping[i] for i in neigh_ids]
        most_common = Counter(neigh_labels).most_common(1)[0][0]
        preds.append((most_common, neigh_labels))
    return preds

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode",       choices=["build","classify","update"], required=True)
    p.add_argument("--data_file",  help="CSV with columns: text,label")
    p.add_argument("--input_file", help="For classify: one error per line; for update: ERROR|LABEL per line")
    p.add_argument("--index_path", default=INDEX_PATH)
    p.add_argument("--mapping_path", default=MAPPING_PATH)
    p.add_argument("--top_k",      type=int, default=5)
    args = p.parse_args()

    model = SentenceTransformer(EMB_MODEL)

    if args.mode == "build":
        if not args.data_file:
            raise ValueError("--data_file is required in build mode")
        df = pd.read_csv(args.data_file)
        texts  = df["text"].astype(str).tolist()
        labels = df["label"].astype(str).tolist()

        index, mapping = build_index(texts, labels, model)
        save_index(index,   args.index_path)
        save_mapping(mapping, args.mapping_path)
        print(f"[build] Indexed {len(texts)} examples → {args.index_path}, {args.mapping_path}")

    elif args.mode == "classify":
        if not args.input_file:
            raise ValueError("--input_file is required in classify mode")
        if not os.path.exists(args.index_path) or not os.path.exists(args.mapping_path):
            raise ValueError("Index or mapping not found; run build first")

        index   = load_index(args.index_path)
        mapping = load_mapping(args.mapping_path)

        with open(args.input_file) as f:
            inputs = [line.strip() for line in f if line.strip()]

        preds = classify(inputs, index, mapping, model, args.top_k)
        for text, (cat, neighs) in zip(inputs, preds):
            print("►", text)
            print("  Predicted:", cat)
            print("  Neighbors:", neighs)
            print()

    elif args.mode == "update":
        if not args.input_file:
            raise ValueError("--input_file is required in update mode")
        if not os.path.exists(args.index_path) or not os.path.exists(args.mapping_path):
            raise ValueError("Index or mapping not found; run build first")

        index   = load_index(args.index_path)
        mapping = load_mapping(args.mapping_path)

        examples = []
        for line in open(args.input_file):
            if "|" not in line: continue
            txt, lbl = line.strip().split("|", 1)
            examples.append((txt.strip(), lbl.strip()))
        if not examples:
            print("[update] no valid lines found in update file"); return

        texts, labels = zip(*examples)
        index, mapping = update_index(texts, labels, index, mapping, model)
        save_index(index, args.index_path)
        save_mapping(mapping, args.mapping_path)
        print(f"[update] Added {len(texts)} new examples to index.")

if __name__ == "__main__":
    main()