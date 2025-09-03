from sentence_transformers import SentenceTransformer
from transformers import AutoModel
import os, re

def load_sentence_transformer(path, **kwargs):
    kwargs.pop("from_tf", None)
    try:
        return SentenceTransformer(path, **kwargs)
    except OSError as e:
        if re.search(r"no file named pytorch_model\.bin", str(e), re.I):
            pt = AutoModel.from_pretrained(path, from_tf=True)
            pt.save_pretrained(path)
            return SentenceTransformer(path, **kwargs)
        raise

# usage
model = load_sentence_transformer("/app/weights", from_tf=True)