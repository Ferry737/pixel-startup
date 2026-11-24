<div align="center">

# JavabFast · جواب‌سریع

**An AI assistant that auto-answers Instagram DMs for small Iranian shops — so a one-person business never misses a customer at 2 a.m.**
This repo is the **agent team workspace**: where the build is split into teams, each team reports, and a live dashboard shows who is doing what.

[![Python](https://img.shields.io/badge/Python-dashboard%20builder-3776AB?style=for-the-badge&logo=python&logoColor=white)](./build_dashboard.py)
[![Agents](https://img.shields.io/badge/Agent%20teams-multi--team-00d4aa?style=for-the-badge)](./agents.json)
[![Status](https://img.shields.io/badge/status-team%20workspace%20%C2%B7%20bot%20in%20progress-ffb454?style=for-the-badge)](#-status)
[![Lang](https://img.shields.io/badge/FA-EN-RTL%20dashboard-blue?style=for-the-badge)](./dashboard.html)

[Dashboard](./dashboard.html) · [Agents map](./agents-map.html) · [Teams](./teams) · [How it works](#-how-it-works)

</div>

---

<div dir="rtl" align="right">

##" این چیست؟

**جواب‌سریع** یک دستیار هوش مصنوعی است که به دایرکت اینستاگرام فروشگاه‌های کوچک به‌طور خودکار جواب می‌دهد. این مخزن، **دفتر کار تیم‌ها** است: هر تیم یک پوشه دارد، گزارش کارش را می‌نویسد، و یک داشبورد زنده وضعیت همه را نشان می‌دهد.

</div>

## 🧩 What it does

| | |
|---|---|
| 📬 **Never miss a DM** | Shoppers on Instagram expect an answer in minutes. JavabFast replies instantly, in Persian, with the shop's own tone. |
| 👥 **Team-based build** | Work is split across AI agent teams. Each team writes `teams/<team>/report.md` — what it did, what it found, what's next. |
| 🗺 **Agents map** | `agents.json` is the single source of truth for every agent and team; `agents-map.html` renders it. |
| 📊 **Live dashboard** | `python build_dashboard.py` → `dashboard.html` — a Persian (RTL) office view of every team's latest report. |
| 🔌 **Probe** | `probe.txt` — quick liveness check for the Instagram-side integration. |

## 🏗 How it works

```
 Instagram DM ──▶ JavabFast assistant ──▶ reply  (shop's tone, Persian)
                        │
                        ▼
        ┌───────────────────────────────────────���
        │  Agent teams (this repo)              │
        │  teams/<team>/report.md  ── every run  │
        └──────────────────┬────────────────────┘
                           │  python build_dashboard.py
                           ▼
                 dashboard.html  (RTL office view)
                 agents-map.html (who exists, who does what)
```

## 🚀 Build the dashboard

```bash
python build_dashboard.py
# open dashboard.html

# point it at a running office:
PIXEL_OFFICE_URL=http://127.0.0.1:3100/ python build_dashboard.py
```

## 📁 Repository layout

```
pixel-startup/
├── agents.json            ← every agent & team (source of truth)
├── agents-map.html        ← visual map of agents.json
├── build_dashboard.py     ← reads teams/*/report.md → dashboard.html
├── dashboard.html         ← Persian RTL team office
├── teams/<team>/report.md ← one report per team per run
├── probe.txt              ← integration liveness probe
└── CLAUDE.md              ← how the agents should work in this repo
```

## 📊 Status

**Team workspace is live; the assistant itself is in progress.** This repository contains the coordination layer (teams, reports, dashboard, agent map). The Instagram-facing bot runtime is being built by the teams and is not in this repo yet.

---

<div align="center">
<sub>Built by <a href="https://github.com/Ferry737">Ferry</a></sub><br>
<sub dir="rtl">جواب سریع، مشتری راحت.</sub>
</div>
