# Jarvis Foundation P01 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build bridge-native Jarvis P01 galaxy + keyless brain + live bridge, opened in Opera GX.

**Architecture:** stdlib-only Python server on 127.0.0.1:4700 serving a single-page 3d-force-graph viewer; build.py indexes teams/ md into graph-data.js; /chat answers extractively + queues live-bridge records.

**Tech Stack:** Python 3.12 stdlib (http.server), vanilla JS + 3d-force-graph pinned CDN, Opera GX (Chromium), Cloudflare tunnel untouched on :8767.

**Spec:** docs/superpowers/specs/2026-10-15-jarvis-foundation-design.md

## Global Constraints
- Python standard library only, no npm, no build step.
- Server binds 127.0.0.1:4700 and serves ONLY my-jarvis/viewer/.
- config.json lives in my-jarvis/ root, never served, placeholder bridge-mode.
- Node id = index in nodes array; excerpt ~700 chars; links on title-mention or [[wikilink]].
- Never paste API keys; none required for P01.
- Opera GX binary: C:\Users\ghola\AppData\Local\Programs\Opera GX\opera.exe.

## Review Focus
- Empty teams/ or missing .md still renders empty galaxy with 0-node notice, never crashes.
- Non-UTF8 or huge .md files are skipped with warning, never abort the index.
- /chat with empty query returns 400 JSON, never 500.
- Direct GET /config.json returns 404, never the file.
- Bridge outbox poll with unknown qid returns empty, never stale чужой answer.

---

### Task 1: Indexer build.py + graph data

**Files:**
- Create: `my-jarvis/build.py`
- Create (generated): `my-jarvis/viewer/graph-data.js`
- Test: `my-jarvis/preflight.py` (graph checks added in Task 4; this task verifies via build output)

**Interfaces:**
- Consumes: `../teams/**/*.md`, `notes/captures/*.md` (may not exist yet)
- Produces: `const GRAPH = {nodes:[{id,label,group,excerpt}],links:[{source,target}]}` in `viewer/graph-data.js`; `build_index(notes_dirs) -> dict` returning node/link counts.

- [ ] **Step 1: Write failing probe** — create `my-jarvis/build.py` stub that exits non-zero; run `python my-jarvis/build.py` and confirm it fails with missing index.
- [ ] **Step 2: Run probe to verify it fails**

Run: `python my-jarvis/build.py`
Expected: FAIL (no graph-data.js written)

- [ ] **Step 3: Implement `build_index()` in `my-jarvis/build.py`** — scan .md (utf-8, errors=ignore, skip >500KB), label from filename stem, group from parent folder, excerpt first ~700 chars, id=index, links on title-mention (case-insensitive substring) or [[wikilink]] match; write `viewer/graph-data.js` with `const GRAPH = ...;`.
- [ ] **Step 4: Run build and verify output**

Run: `python my-jarvis/build.py`
Expected: PASS, prints `nodes=N links=M` with N>=10 from teams/ reports, file exists.

- [ ] **Step 5: Commit**

```bash
git add my-jarvis/build.py my-jarvis/viewer/graph-data.js
git commit -m "feat: Jarvis P01 indexer build.py with teams graph"
```

### Task 2: Viewer galaxy index.html

**Files:**
- Create: `my-jarvis/viewer/index.html`
- Uses: `my-jarvis/viewer/graph-data.js` from Task 1

**Interfaces:**
- Consumes: global `GRAPH` ({nodes,links})
- Produces: galaxy render + `askJarvis(text)` POST /chat + bridge outbox poll + `focusNodes(nodes[])` (single fly vs cluster light vs hold still on smalltalk).

- [ ] **Step 1: Write failing check** — fetch viewer file list; confirm `my-jarvis/viewer/index.html` missing.
- [ ] **Step 2: Run check to verify it fails**

Run: `python -c "import pathlib; assert pathlib.Path('my-jarvis/viewer/index.html').exists()"`
Expected: FAIL (AssertionError)

- [ ] **Step 3: Implement `my-jarvis/viewer/index.html`** — black starfield, 3d-force-graph pinned exact CDN version, color by group, idle rotation, click fly + neighbours + side panel excerpt, bottom input bar calling `askJarvis()`, status line (listening/thinking/speaking hooks for later), `?mute=1` honored in speak stub.
- [ ] **Step 4: Verify file + graph wire**

Run: `python -c "import pathlib; t=pathlib.Path('my-jarvis/viewer/index.html').read_text(encoding='utf-8'); assert 'GRAPH' in t and 'askJarvis' in t and '3d-force-graph' in t; print('viewer ok')"`
Expected: PASS `viewer ok`

- [ ] **Step 5: Commit**

```bash
git add my-jarvis/viewer/index.html
git commit -m "feat: Jarvis P01 galaxy viewer with chat input"
```

### Task 3: Server + keyless brain + live bridge

**Files:**
- Create: `my-jarvis/server.py`
- Create: `my-jarvis/config.json`
- Create: `my-jarvis/bridge/inbox.jsonl` (empty), `my-jarvis/bridge/outbox.jsonl` (empty)
- Test: Task 4 preflight exercises endpoints.

**Interfaces:**
- Consumes: `viewer/` files, `GRAPH` node count, `bridge/*.jsonl`
- Produces: `GET /` viewer; `POST /chat {q} -> {answer,nodes[],qid}`; `GET /bridge/next -> {qid,question,nodes} | {empty:true}`; `POST /bridge/answer {qid,answer} -> {ok:true}`; `GET /health -> {ok,nodes}`.

- [ ] **Step 1: Write failing check** — `Invoke-WebRequest http://127.0.0.1:4700/` must fail (connection refused) before server exists.
- [ ] **Step 2: Run check to verify it fails**

Run: `python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:4700/', timeout=3)"`
Expected: FAIL (URLError refused)

- [ ] **Step 3: Implement `server.py`** — http.server bound 127.0.0.1:4700, serves viewer/ only (known types .html/.js/.css/.json/.png), 404 for /config.json and unknown paths, 1MB body cap; POST /chat scores keyword overlap title-weighted top-6 from indexed excerpts, extractive answer (top excerpt sentences, admits gap when score 0), appends `{qid,question,nodes,ts}` to bridge/inbox.jsonl; bridge endpoints append/read jsonl with file locks via atomic append.
- [ ] **Step 4: Start server, verify endpoints**

Run: `python my-jarvis/server.py` (background) then `python -c "import urllib.request,json; print(urllib.request.urlopen('http://127.0.0.1:4700/health',timeout=5).read()[:200])"`
Expected: PASS `{"ok": true, "nodes": N}` N>0

- [ ] **Step 5: Commit**

```bash
git add my-jarvis/server.py my-jarvis/config.json my-jarvis/bridge/.gitkeep
git commit -m "feat: Jarvis P01 server with keyless chat and live bridge"
```

### Task 4: Preflight + Opera GX launch + verify

**Files:**
- Create: `my-jarvis/preflight.py`
- Create: `my-jarvis/start_jarvis.bat`

**Interfaces:**
- Consumes: server :4700, graph-data.js, bridge endpoints.
- Produces: preflight summary `N pass, N fail`; Opera GX pinned-tab workflow.

- [ ] **Step 1: Write failing check** — `python my-jarvis/preflight.py` must fail (file missing).
- [ ] **Step 2: Run check to verify it fails**

Run: `python my-jarvis/preflight.py`
Expected: FAIL (file not found)

- [ ] **Step 3: Implement `preflight.py` + `start_jarvis.bat`** — checks: server up, graph N>0, /chat well-formed (answer+nodes array), /chat empty query returns 400 JSON, bridge roundtrip with test qid then cleanup, bridge unknown qid returns empty, served-file matches disk (compare bytes), config.json returns 404; bat starts server + opens Opera GX to http://127.0.0.1:4700/.
- [ ] **Step 4: Run preflight, fix until clean**

Run: `python my-jarvis/preflight.py`
Expected: PASS summary `8 pass, 0 fail`

- [ ] **Step 5: Launch Opera GX + commit**

Run: `my-jarvis/start_jarvis.bat` then confirm galaxy renders; `git add my-jarvis/preflight.py my-jarvis/start_jarvis.bat; git commit -m "feat: Jarvis P01 preflight and Opera GX launcher"`
