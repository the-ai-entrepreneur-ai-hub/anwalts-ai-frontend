#!/usr/bin/env python3
import argparse
from typing import List
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models as qm


def main():
    ap = argparse.ArgumentParser(description='Query code index in Qdrant by natural language')
    ap.add_argument('--qdrant', default='http://localhost:6333')
    ap.add_argument('--collection', default='code-context')
    ap.add_argument('--model', default='all-MiniLM-L6-v2')
    ap.add_argument('--topk', type=int, default=8)
    ap.add_argument('--q', required=True, help='query text')
    args = ap.parse_args()

    embed = SentenceTransformer(args.model)
    vec = embed.encode([args.q], normalize_embeddings=True)[0].tolist()
    client = QdrantClient(url=args.qdrant)
    res = client.search(collection_name=args.collection, query_vector=vec, limit=args.topk, with_payload=True)
    for r in res:
        path = r.payload.get('file')
        chunk = r.payload.get('chunk')
        text = r.payload.get('text')
        score = r.score
        print(f"score={score:.4f}  file={path}  chunk={chunk}\n{text}\n")

if __name__ == '__main__':
    main()

