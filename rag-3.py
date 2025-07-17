#!/usr/bin/env python
"""
redis_vector_search.py
Quick one-off semantic search against a RediSearch HNSW index.

Example:
    python redis_vector_search.py \
        --query "how do I reset my password?" \
        --host localhost --port 6379 --index doc_index --top-k 5
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

import numpy as np
import redis
from redis.commands.search.query import Query
from redis.commands.search.util import vec_to_blob
from sentence_transformers import SentenceTransformer


def embed(texts: List[str], model_name: str, device: str = "cpu"):
    """Return float32 numpy vectors for the given texts."""
    model = SentenceTransformer(model_name, device=device)
    return model.encode(texts, dtype=np.float32, show_progress_bar=False)


def main() -> None:
    p = argparse.ArgumentParser(description="One-off semantic search in Redis")
    p.add_argument("--query", required=True, help="Natural-language search query")
    p.add_argument("--host", default="localhost")
    p.add_argument("--port", type=int, default=6379)
    p.add_argument("--password", default=None)
    p.add_argument("--index", "--index-name", dest="index_name", default="doc_index")
    p.add_argument("--top-k", type=int, default=5)
    p.add_argument("--model", default="thenlper/gte-small",
                   help="Sentence-Transformers model ID "
                        "(use the same one that produced your stored vectors!)")
    p.add_argument("--device", default="cpu", help="cuda:0, mps, etc.")
    p.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = p.parse_args()

    # ── Connect ────────────────────────────────────────────────────────────────
    r = redis.Redis(host=args.host, port=args.port, password=args.password)
    try:
        r.ping()
    except redis.AuthenticationError:
        sys.exit("❌  Authentication failed: wrong password?")
    except redis.ConnectionError:
        sys.exit("❌  Could not reach Redis at "
                 f"{args.host}:{args.port}")

    # ── Embed the query ────────────────────────────────────────────────────────
    q_vec = embed([args.query], model_name=args.model, device=args.device)[0]

    # ── KNN search ────────────────────────────────────────────────────────────
    query = (
        Query("*=>[KNN $K @vec $BLOB]")
        .return_fields("text", "__vec_score")
        .sort_by("__vec_score")
        .dialect(2)
    )
    params = {"K": args.top_k, "BLOB": vec_to_blob(q_vec)}
    res = r.ft(args.index_name).search(query, query_params=params)

    # ── Display results ────────────────────────────────────────────────────────
    hits = []
    for rank, doc in enumerate(res.docs, 1):
        score = 1.0 - float(doc.__dict__.get("__vec_score", 1.0))
        hits.append(
            {
                "rank": rank,
                "redis_id": doc.id,
                "score": round(score, 4),
                "text": doc.text,
            }
        )

    if args.pretty:
        print(json.dumps(hits, indent=2, ensure_ascii=False))
    else:
        for h in hits:
            print(f"[{h['rank']}] score={h['score']:.4f}  id={h['redis_id']}\n"
                  f"    {h['text']}\n")

    if not hits:
        print("(no hits)")


if __name__ == "__main__":
    main()