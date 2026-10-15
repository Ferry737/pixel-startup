# -*- coding: utf-8 -*-
"""Jarvis P01 server: viewer + keyless brain + live agent bridge (stdlib only)."""
import json
import os
import re
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
VIEWER = os.path.join(ROOT, 'viewer')
BRIDGE = os.path.join(ROOT, 'bridge')
INBOX = os.path.join(BRIDGE, 'inbox.jsonl')
OUTBOX = os.path.join(BRIDGE, 'outbox.jsonl')
BODY_CAP = 64 * 1024
MIME = {'.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
        '.css': 'text/css; charset=utf-8', '.json': 'application/json',
        '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml'}

import build as indexer

INDEX = indexer.build_index()
_qid = [int(time.time() * 1000)]


def tokens(s):
    return [w for w in re.findall(r'[a-z0-9\u00c0-\u024f\u0370-\u03ff\u0400-\u04ff\u0590-\u05ff\u0600-\u06ff\u4e00-\u9fff]+', s.lower()) if len(w) > 2]


def score_notes(query):
    qt = tokens(query)
    if not qt:
        return []
    scored = []
    for n in INDEX['nodes']:
        title_t = set(tokens(n['label'].replace('-', ' ').replace('_', ' ')))
        body_t = tokens(n['excerpt'])
        body_set = set(body_t)
        s = sum(3 for w in qt if w in title_t) + sum(1 for w in qt if w in body_set)
        if s > 0:
            scored.append((s, n['id']))
    scored.sort(reverse=True)
    return [i for _, i in scored[:6]]


def extractive(query, ids):
    if not ids:
        return "My notes don't cover that yet — try asking about the startup reports."
    top = INDEX['nodes'][ids[0]]
    text = top['excerpt']
    sents = re.split(r'(?<=[.!?])\s+', text)
    short = ' '.join(sents[:2])[:400]
    if len(ids) == 1:
        return f"From '{top['label']}': {short}"
    return f"From '{top['label']}' and {len(ids) - 1} more: {short}"


def read_jsonl(path):
    rows = []
    if os.path.exists(path):
        with open(path, encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        rows.append(json.loads(line))
                    except ValueError:
                        pass
    return rows


class Handler(BaseHTTPRequestHandler):
    server_version = 'JarvisP01/1.0'

    def log_message(self, *a):
        pass

    def _host_ok(self):
        host = (self.headers.get('Host') or '').split(':')[0].lower()
        return host in ('127.0.0.1', 'localhost', '')

    def _send(self, code, body, ctype='application/json'):
        data = body if isinstance(body, bytes) else body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(data)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def do_GET(self):
        if not self._host_ok():
            return self._json(403, {'error': 'foreign host refused'})
        path = self.path.split('?', 1)[0]
        if path == '/health':
            return self._json(200, {'ok': True, 'nodes': len(INDEX['nodes'])})
        if path == '/bridge/next':
            answered = {r.get('qid') for r in read_jsonl(OUTBOX)}
            for r in read_jsonl(INBOX):
                if r.get('qid') not in answered:
                    return self._json(200, r)
            return self._json(200, {'empty': True})
        if path.startswith('/bridge/outbox'):
            qid = None
            if 'qid=' in self.path:
                m = re.search(r'qid=([^&]+)', self.path)
                qid = int(m.group(1)) if m and m.group(1).lstrip('-').isdigit() else m.group(1) if m else None
            for r in read_jsonl(OUTBOX):
                if r.get('qid') == qid:
                    return self._json(200, r)
            return self._json(200, {'empty': True})
        if path in ('/', '/index.html'):
            fp = os.path.join(VIEWER, 'index.html')
        elif path in ('/graph-data.js', '/viewer/graph-data.js'):
            fp = os.path.join(VIEWER, 'graph-data.js')
        else:
            return self._json(404, {'error': 'not found'})
        if not os.path.isfile(fp):
            return self._json(404, {'error': 'not found'})
        with open(fp, 'rb') as f:
            disk = f.read()
        self._send(200, disk, MIME.get('.html' if fp.endswith('.html') else '.js'))

    def do_POST(self):
        if not self._host_ok():
            return self._json(403, {'error': 'foreign host refused'})
        length = int(self.headers.get('Content-Length') or 0)
        if length > BODY_CAP or length <= 0:
            return self._json(413 if length > BODY_CAP else 400, {'error': 'bad body'})
        raw = self.rfile.read(length)
        try:
            body = json.loads(raw.decode('utf-8'))
        except ValueError:
            return self._json(400, {'error': 'bad json'})
        if self.path == '/chat':
            q = (body.get('q') or '').strip()
            if not q:
                return self._json(400, {'error': 'empty question'})
            ids = score_notes(q)
            _qid[0] += 1
            qid = _qid[0]
            os.makedirs(BRIDGE, exist_ok=True)
            with open(INBOX, 'a', encoding='utf-8') as f:
                f.write(json.dumps({'qid': qid, 'question': q, 'nodes': ids, 'ts': time.time()}, ensure_ascii=False) + '\n')
            return self._json(200, {'answer': extractive(q, ids), 'nodes': ids, 'qid': qid})
        if self.path == '/bridge/answer':
            if 'qid' not in body or 'answer' not in body:
                return self._json(400, {'error': 'qid and answer required'})
            os.makedirs(BRIDGE, exist_ok=True)
            with open(OUTBOX, 'a', encoding='utf-8') as f:
                f.write(json.dumps({'qid': body['qid'], 'answer': body['answer'], 'ts': time.time()}, ensure_ascii=False) + '\n')
            return self._json(200, {'ok': True})
        return self._json(404, {'error': 'not found'})


def main():
    os.makedirs(BRIDGE, exist_ok=True)
    for p in (INBOX, OUTBOX):
        if not os.path.exists(p):
            open(p, 'a', encoding='utf-8').close()
    srv = HTTPServer(('127.0.0.1', 4700), Handler)
    print(f'jarvis P01 on http://127.0.0.1:4700/ nodes={len(INDEX["nodes"])}')
    srv.serve_forever()


if __name__ == '__main__':
    main()
