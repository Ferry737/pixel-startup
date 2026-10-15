# -*- coding: utf-8 -*-
"""Indexer: scan markdown notes -> viewer/graph-data.js (stdlib only)."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
NOTES_DIRS = [
    os.path.join(ROOT, '..', 'teams'),
    os.path.join(ROOT, 'notes'),
]
OUT = os.path.join(ROOT, 'viewer', 'graph-data.js')
MAX_BYTES = 500 * 1024


def iter_md(dirs):
    for d in dirs:
        d = os.path.normpath(d)
        if not os.path.isdir(d):
            continue
        for base, _subs, files in os.walk(d):
            for f in sorted(files):
                if f.lower().endswith('.md'):
                    yield os.path.join(base, f)


def excerpt_of(text, n=700):
    t = re.sub(r'\s+', ' ', text.strip())
    return t[:n]


def build_index(notes_dirs=None):
    paths = list(iter_md(notes_dirs or NOTES_DIRS))
    nodes, texts = [], []
    for i, p in enumerate(paths):
        try:
            if os.path.getsize(p) > MAX_BYTES:
                print(f'skip (too big): {p}')
                continue
        except OSError as e:
            print(f'skip (stat fail): {p}: {e}')
            continue
        try:
            with open(p, encoding='utf-8', errors='ignore') as f:
                text = f.read()
        except OSError as e:
            print(f'skip (read fail): {p}: {e}')
            continue
        label = os.path.splitext(os.path.basename(p))[0]
        group = os.path.basename(os.path.dirname(p))
        nodes.append({
            'id': len(nodes),
            'label': label,
            'group': group,
            'excerpt': excerpt_of(text),
            'path': os.path.relpath(p, ROOT).replace(os.sep, '/'),
        })
        texts.append(text)
    links, seen = [], set()
    titles = [n['label'].lower() for n in nodes]
    wikis = [set(m.lower() for m in re.findall(r'\[\[([^\]]+)\]\]', t)) for t in texts]
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            hit = False
            if len(titles[i]) > 2 and titles[i] in texts[j].lower():
                hit = True
            elif len(titles[j]) > 2 and titles[j] in texts[i].lower():
                hit = True
            elif wikis[i] & wikis[j]:
                hit = True
            if hit:
                key = (i, j)
                if key not in seen:
                    seen.add(key)
                    links.append({'source': i, 'target': j})
    return {'nodes': nodes, 'links': links}


def main():
    graph = build_index()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('const GRAPH = ')
        json.dump(graph, f, ensure_ascii=False)
        f.write(';\n')
    print(f"indexed nodes={len(graph['nodes'])} links={len(graph['links'])} -> {OUT}")
    return 0 if graph['nodes'] else 1


if __name__ == '__main__':
    sys.exit(main())
