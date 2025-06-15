import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def generate_index(
    model_path: str,
    phrases: list[str],
    labels: list[str],
    index_path: str = "error_category.index",
    mapping_path: str = "cat_mapping.json",
    normalize: bool = True,
):
    """
    Builds and saves:
      • a FAISS index of your seed-phrase embeddings
      • a JSON file mapping phrases → labels
    
    Args:
      model_path: path or name for SentenceTransformer
      phrases: list of example error‐text strings
      labels:  same length list of category names
      index_path:  where to write the faiss index
      mapping_path: where to write the JSON mapping
      normalize: if True, embeddings are L2‐normalized and
                 index uses IndexFlatIP (cosine sim)
                 else uses raw IndexFlatL2.
    """
    # 1) load model & encode
    model = SentenceTransformer(model_path)
    embeddings = model.encode(phrases, normalize_embeddings=normalize)
    embeddings = embeddings.astype("float32")

    # 2) build index
    d = embeddings.shape[1]
    if normalize:
        idx = faiss.IndexFlatIP(d)
    else:
        idx = faiss.IndexFlatL2(d)
    idx.add(embeddings)

    # 3) write index & mapping
    faiss.write_index(idx, index_path)
    with open(mapping_path, "w") as f:
        json.dump({"phrases": phrases, "labels": labels}, f, indent=2)

    print(f"✅ Index saved to {index_path}")
    print(f"✅ Mapping saved to {mapping_path}", end="\n\n")


def categorize_query(
    query: str,
    model_path: str,
    index_path: str = "error_category.index",
    mapping_path: str = "cat_mapping.json",
    top_k: int = 1,
    threshold: float = 0.7,
    normalize: bool = True,
) -> str:
    """
    Loads index + mapping, then returns the best‐match label for `query`,
    or "UNKNOWN" if similarity/distance is below threshold.
    """
    # 1) load model, index, mapping
    model = SentenceTransformer(model_path)
    idx = faiss.read_index(index_path)
    with open(mapping_path) as f:
        m = json.load(f)
    labels = m["labels"]

    # 2) encode & (optionally) normalize
    q_emb = model.encode([query], normalize_embeddings=normalize).astype("float32")

    # 3) search
    D, I = idx.search(q_emb, top_k)
    score = float(D[0][0])
    best_idx = int(I[0][0])

    # 4) interpret
    if normalize:
        # D is inner‐product (cosine) in [-1..1]
        return labels[best_idx] if score >= threshold else "UNKNOWN"
    else:
        # D is squared L2 distance (lower is closer)
        return labels[best_idx] if score <= threshold else "UNKNOWN"


if __name__ == "__main__":
    # ←— your “seed” phrases & categories
    PHRASES = [
        "YCG.USD fail to load in ref data",
        "Curve not found",
    ]
    LABELS = [
        "REF DATA",
        "MARKET DATA",
    ]
    MODEL = "/Users/zkyop9e/Desktop/projects/optimus-pro/tutorial/hfweights"

    # 1) build index & mapping
    generate_index(
        model_path=MODEL,
        phrases=PHRASES,
        labels=LABELS,
        index_path="error_category.index",
        mapping_path="cat_mapping.json",
        normalize=True,
    )

    # 2) test some queries
    for q in [
        "I keep getting “YCG.USD failed to load” in my ref data pipeline",
        "why does the curve never show up?",
        "completely unrelated question"
    ]:
        cat = categorize_query(
            query=q,
            model_path=MODEL,
            index_path="error_category.index",
            mapping_path="cat_mapping.json",
            top_k=1,
            threshold=0.6,
            normalize=True,
        )
        print(f"> {q}\n→ {cat}\n")