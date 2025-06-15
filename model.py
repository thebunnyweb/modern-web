import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

# 1. Load your embedding model
model = SentenceTransformer("/Users/zkyop9e/Desktop/projects/optimus-pro/tutorial/hfweights")

# 2. Load the FAISS index and the mapping file you dumped
index = faiss.read_index("error_category.index")

with open("/Users/zkyop9e/Library/Application Support/JetBrains/PyCharmCE2023.2/scratches/cat.json") as f:
    mapping = json.load(f)
phrases = mapping["phrases"]   # ["YCG.USD fail to load in ref data", "Curve not found"]
labels  = mapping["labels"]    # ["REF DATA", "MARKET DATA"]

# 3. (Opt) Normalize the index to use cosine-similarity instead of raw L2 distances
#    — this usually gives more intuitive “similarity” scores between texts
#    Note: if you do this, you’ll need to rebuild the index once:
#
#    embeddings = model.encode(phrases, normalize_embeddings=True)
#    index = faiss.IndexFlatIP(embeddings.shape[1])
#    index.add(embeddings)
#    faiss.write_index(index, "error_category.index")
#
#    And load with IndexFlatIP instead of your L2 index.

def categorize(query: str, top_k: int = 1, threshold: float = 0.6) -> str:
    """
    Encode `query`, find nearest seed phrase in the index,
    and return its label if similarity > threshold, else "UNKNOWN".
    """
    # 1) encode (and normalize if you rebuilt with IP)
    q_emb = model.encode([query], normalize_embeddings=True)

    # 2) search
    D, I = index.search(np.array(q_emb), top_k)
    # D = similarity scores (if IP) or squared distances (if L2)
    # I = indices of the nearest phrases

    # if using cosine similarity (IndexFlatIP), D will be in [-1..1], higher is better
    best_score = D[0][0]
    best_idx   = I[0][0]

    # 3) decide if it’s close enough
    if best_score >= threshold:
        return labels[best_idx]
    else:
        return "UNKNOWN"

# ——— example:
for q in [
    "I keep getting “YCG.USD failed to load” in my ref data pipeline",
    "why does the curve never show up?"
]:
    print(q, "→", categorize(q))