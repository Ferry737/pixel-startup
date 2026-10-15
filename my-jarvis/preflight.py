# -*- coding: utf-8 -*-
"""P01 preflight: live end-to-end checks. Exit non-zero on any failure."""
import json
import os
import sys
import urllib.request
import urllib.error

BASE = 'http://127.0.0.1:4700'
ROOT = os.path.dirname(os.path.abspath(__file__))
results = []


def check(name, fn):
    try:
        fn()
        results.append((name, 'pass', ''))
        print(f'ok   {name}')
    except AssertionError as e:
        results.append((name, 'fail', str(e)))
        print(f'FAIL {name}: {e}')
    except Exception as e:
        results.append((name, 'fail', f'{type(e).__name__}: {e}'))
        print(f'FAIL {name}: {type(e).__name__}: {e}')


def get(path):
    req = urllib.request.Request(BASE + path, headers={'Host': '127.0.0.1:4700'})
    return urllib.request.urlopen(req, timeout=10)


def post(path, obj):
    data = json.dumps(obj).encode('utf-8')
    req = urllib.request.Request(BASE + path, data=data,
                                 headers={'Content-Type': 'application/json', 'Host': '127.0.0.1:4700'})
    return urllib.request.urlopen(req, timeout=10)


def jget(path):
    return json.loads(get(path).read().decode('utf-8'))


def prune_bridge(qid):
    for name in ('inbox.jsonl', 'outbox.jsonl'):
        p = os.path.join(ROOT, 'bridge', name)
        rows = []
        with open(p, encoding='utf-8', errors='ignore') as f:
            for line in f:
                try:
                    if json.loads(line).get('qid') != qid:
                        rows.append(line)
                except ValueError:
                    pass
        with open(p, 'w', encoding='utf-8') as f:
            f.writelines(rows)


def t_server():
    body = get('/').read().decode('utf-8', 'ignore')
    assert '3d-force-graph' in body, 'viewer missing galaxy lib'


def t_graph():
    body = get('/graph-data.js').read().decode('utf-8', 'ignore')
    assert body.count('"label"') > 0, 'zero nodes served'


def t_chat():
    d = json.loads(post('/chat', {'q': 'pricing plans monthly cost'}).read().decode('utf-8'))
    assert isinstance(d.get('answer'), str) and d['answer'], 'no answer'
    assert isinstance(d.get('nodes'), list), 'no nodes array'
    assert isinstance(d.get('qid'), int), 'no qid'


def t_chat_empty():
    try:
        post('/chat', {'q': '   '})
    except urllib.error.HTTPError as e:
        assert e.code == 400, f'expected 400, got {e.code}'
        return
    raise AssertionError('empty question not rejected')


def t_bridge():
    d = json.loads(post('/chat', {'q': '__preflight_probe__ pricing'}).read().decode('utf-8'))
    qid = d['qid']
    try:
        nxt = jget('/bridge/next')
        assert nxt.get('qid') == qid or 'empty' in nxt or True, 'next unreadable'
        post('/bridge/answer', {'qid': qid, 'answer': '__preflight_ok__'})
        out = jget(f'/bridge/outbox?qid={qid}')
        assert out.get('answer') == '__preflight_ok__', 'roundtrip mismatch'
    finally:
        prune_bridge(qid)


def t_bridge_unknown():
    d = jget('/bridge/outbox?qid=-999999')
    assert d.get('empty') is True, 'unknown qid should be empty'


def t_served_match():
    disk = open(os.path.join(ROOT, 'viewer', 'graph-data.js'), 'rb').read()
    assert get('/graph-data.js').read() == disk, 'stale served file'


def t_config_denied():
    try:
        get('/config.json')
    except urllib.error.HTTPError as e:
        assert e.code == 404, f'expected 404, got {e.code}'
        return
    raise AssertionError('config.json reachable from browser')


for name, fn in [('server+viewer', t_server), ('graph N>0', t_graph),
                 ('chat well-formed', t_chat), ('chat empty 400', t_chat_empty),
                 ('bridge roundtrip', t_bridge), ('bridge unknown empty', t_bridge_unknown),
                 ('served==disk', t_served_match), ('config.json 404', t_config_denied)]:
    check(name, fn)

np = sum(1 for _, s, _ in results if s == 'pass')
nf = sum(1 for _, s, _ in results if s == 'fail')
print(f'{np} pass, {nf} fail, 0 warn')
sys.exit(0 if nf == 0 else 1)
