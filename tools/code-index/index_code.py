#!/usr/bin/env python3
import argparse
import os
import sys
import time
from pathlib import Path
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


DEFAULT_EXTS = {
    '.js', '.ts', '.tsx', '.jsx', '.vue', '.json', '.md', '.mdx', '.css', '.scss',
    '.py', '.go', '.rs', '.java', '.kt', '.c', '.h', '.cpp', '.hpp', '.cs',
    '.yml', '.yaml', '.toml', '.ini', '.sh', '.bash', '.zsh', '.env', '.rb', '.php'
}


def iter_files(root: Path, include_exts: set) -> List[Path]:
    for p in root.rglob('*'):
        if not p.is_file():
            continue
        if p.name.startswith('.'):
            continue
        if p.suffix.lower() in include_exts:
            yield p


def chunk_text(text: str, max_len: int = 800, overlap: int = 120) -> List[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i+max_len]
        if not chunk:
            break
        chunks.append(' '.join(chunk))
        i += max_len - overlap
    return chunks


def main():
    ap = argparse.ArgumentParser(description='Index codebase into Qdrant using sentence-transformers embeddings.')
    ap.add_argument('--root', default='.', help='Root directory to index')
    ap.add_argument('--qdrant', default='http://localhost:6333', help='Qdrant endpoint')
    ap.add_argument('--collection', default='code-context', help='Qdrant collection')
    ap.add_argument('--model', default='all-MiniLM-L6-v2', help='SentenceTransformer model name')
    ap.add_argument('--exts', default='', help='Comma-separated extensions to include (overrides defaults)')
    ap.add_argument('--recreate', action='store_true', help='Recreate collection')
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f'Root not found: {root}', file=sys.stderr)
        sys.exit(1)

    include_exts = set(e.strip().lower() for e in args.exts.split(',') if e.strip()) if args.exts else DEFAULT_EXTS

    print(f'Loading embedding model: {args.model}')
    embed = SentenceTransformer(args.model)
    dim = embed.get_sentence_embedding_dimension()

    client = QdrantClient(url=args.qdrant)
    if args.recreate:
        try:
            client.delete_collection(args.collection)
        except Exception:
            pass
    try:
        client.get_collection(args.collection)
    except Exception:
        client.recreate_collection(
            collection_name=args.collection,
            vectors_config=qm.VectorParams(size=dim, distance=qm.Distance.COSINE)
        )

    points = []
    pid = 0
    files = list(iter_files(root, include_exts))
    for fp in tqdm(files, desc='Indexing files'):
        try:
            text = fp.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        chunks = chunk_text(text)
        if not chunks:
            continue
        vectors = embed.encode(chunks, show_progress_bar=False, normalize_embeddings=True)
        for idx, vec in enumerate(vectors):
            points.append(qm.PointStruct(
                id=pid,
                vector=vec.tolist(),
                payload={
                    'file': str(fp.relative_to(root)),
                    'chunk': idx,
                    'text': chunks[idx]
                }
            ))
            pid += 1
        if len(points) >= 256:
            client.upsert(args.collection, points=points)
            points = []

    if points:
        client.upsert(args.collection, points=points)

    print('Index complete.')


if __name__ == '__main__':
    main()

