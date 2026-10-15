# Jarvis Foundation P01 — Bridge-Native Design

Date: 2026-10-15
Scope: Approach A bridge-native. Build + connect to self + open in Opera GX.
User autonomy: ASAP, autonomous without asking (granted 2026-10-15).

## 1. Intended outcome (agreed)
- 3D knowledge galaxy of own notes in Opera GX pinned tab.
- Keyless brain: extractive /chat answers immediately + live upgrade from this session.
- Connection to self = live agent bridge (inbox/outbox files + HTTP endpoints).
- Hosting = local server + open in Opera GX + pin. Existing :8767 tunnel untouched.
- What user said vs assumptions: user chose P01 slice, live bridge, open+pin, no Anthropic key. Assumed: notes source = teams/ + captures/; stdlib only; 127.0.0.1:4700 per pack.

## 2. Constraints
- Python 3.12 stdlib only, no npm, no build step. Viewer single HTML + pinned CDN 3d-force-graph.
- Server binds 127.0.0.1:4700, serves ONLY viewer/. config.json in project root, never served.
- Node numeric id = index in nodes array. ~700-char excerpts. Links on title mention or [[wikilink]].
- No API keys in chat. config.json placeholder bridge-mode.
- Opera GX installed; Chrome absent (use Opera GX Chromium for speech).

## 3. Success criteria
- http://127.0.0.1:4700/ loads galaxy with N>0 nodes from teams/ reports.
- POST /chat returns {"answer","nodes"} well-formed + appends bridge inbox record.
- GET /bridge/next + POST /bridge/answer roundtrip works; viewer swaps live answer.
- config.json not reachable from browser. Served files match disk.
- start_jarvis.bat launches server + opens Opera GX; user pins tab.

## 4. Architecture
```
pixel-startup/my-jarvis/
  build.py          # indexer -> viewer/graph-data.js
  server.py         # 127.0.0.1:4700, viewer/ only + /chat + /bridge/*
  preflight.py      # P01 live checks
  config.json       # {"mode":"bridge","model":"live-agent-bridge"}
  bridge/
    inbox.jsonl     # /chat requests awaiting live answer
    outbox.jsonl    # live answers by session
  viewer/
    index.html      # galaxy + input bar + bridge poll
    graph-data.js   # const GRAPH = {nodes:[{id,label,group,excerpt}],links:[...]}
  notes/
    captures/       # future /remember + teardown notes
  start_jarvis.bat  # launch server + Opera GX
```
Notes source: ../teams/**/*.md (10 reports) + notes/captures/*.md.

## 5. Data flow
1. build.py scans .md, id=index, excerpt ~700 chars, links via title-mention/wikilink.
2. Viewer loads GRAPH, renders 3d-force-graph, click flies camera + side panel.
3. /chat: keyword overlap (title-weighted) top-6 -> extractive answer + nodes[] -> append inbox.jsonl {qid,question,nodes,ts}.
4. This session polls GET /bridge/next, answers via POST /bridge/answer {qid,answer}.
5. Viewer polls outbox, swaps extractive with live answer, flies camera to top node (<4 nodes) else lights cluster.

## 6. Error handling
- No graph-data.js -> viewer empty state, preflight fail.
- Zero notes -> N=0 fail loudly.
- Bridge offline -> extractive answer stands, inbox queued.
- config.json request -> 404. Only viewer/ file types served. Request body capped.

## 7. Testing (preflight.py)
Checks with tick/cross, summary "N pass, N fail", non-zero exit on fail:
1. Server up + viewer served. 2. Graph loads N>0. 3. /chat well-formed. 4. Bridge inbox->answer roundtrip (test record removed). 5. Served files match disk. 6. config.json not reachable.

## 8. Opera GX hosting
- start_jarvis.bat: start server, open opera.exe http://127.0.0.1:4700/.
- User pins tab. Mic/speech tested in Opera GX (Chromium). ?mute=1 supported later.
- No public tunnel for Jarvis in P01 (stays loopback).

## 9. Out of scope (later prompts)
Voice routes, butler persona, /remember, REA kit, phone/Telegram, tunnel hotline, security armor pass.
