# -*- coding: utf-8 -*-
"""Build Persian RTL dashboard for the 5-team pixel-agents startup run."""
import glob, html, json, os, re, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
TRANSCRIPTS = os.path.expanduser(r'~/.claude/projects/C--Users-ghola-pixel-startup')
OFFICE_URL = os.getenv('PIXEL_OFFICE_URL', 'http://127.0.0.1:3100/')

TEAMS = [
    ('1-product',    'محصول و استراتژی', [('سارا', 'تحقیق بازار'), ('امیر', 'طراحی MVP')]),
    ('2-engineering','مهندسی',          [('نگار', 'معماری'), ('رضا', 'داده و API')]),
    ('3-growth',     'رشد و بازاریابی', [('مینا', 'کانال‌های رشد'), ('حسین', 'کپی‌رایتینگ')]),
    ('4-finance',    'مالی',             [('لیلا', 'قیمت‌گذاری'), ('بهرام', 'مدل هزینه')]),
    ('5-ops',        'پشتیبانی و عملیات',[('پریسا', 'پشتیبانی'), ('کاوه', 'عملیات')]),
]

def md_to_html(text):
    out, in_list = [], False
    for line in text.splitlines():
        s = line.strip()
        if not s:
            if in_list: out.append('</ul>'); in_list = False
            continue
        s = html.escape(s)
        s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
        if s.startswith('###'):  s = f'<h4>{s[4:]}</h4>'
        elif s.startswith('##'): s = f'<h3>{s[3:]}</h3>'
        elif s.startswith('#'):  s = f'<h3>{s[2:]}</h3>'
        elif s.startswith(('- ', '* ', '• ')):
            if not in_list: out.append('<ul>'); in_list = True
            out.append(f'<li>{s[2:]}</li>')
        else:
            if in_list: out.append('</ul>'); in_list = False
            out.append(f'<p>{s}</p>')
    if in_list: out.append('</ul>')
    return '\n'.join(out)

# --- stats from real transcripts ---
sessions = task_calls = 0
for f in glob.glob(os.path.join(TRANSCRIPTS, '*.jsonl')):
    mt = os.path.getmtime(f)
    if datetime.datetime.fromtimestamp(mt) > datetime.datetime.now() - datetime.timedelta(hours=2):
        sessions += 1
        try:
            task_calls += open(f, encoding='utf-8', errors='ignore').read().count('"name":"Agent"')
        except OSError:
            pass

cards = []
for slug, name, emps in TEAMS:
    p = os.path.join(ROOT, 'teams', slug, 'report.md')
    body = open(p, encoding='utf-8').read() if os.path.exists(p) else '<p dir="rtl">(گزارش هنوز نوشته نشده)</p>'
    staff = ''.join(f'<span class="emp">{html.escape(e)} · {html.escape(r)}</span>' for e, r in emps)
    cards.append(f'''
    <section class="card">
      <div class="card-head">
        <div>
          <h2>{html.escape(name)}</h2>
          <div class="emps">{staff}</div>
        </div>
        <span class="team-no">{slug.split('-')[0]}</span>
      </div>
      <details open><summary>گزارش تیم</summary><div class="report">{md_to_html(body)}</div></details>
    </section>''')

now = datetime.datetime.now().strftime('%H:%M — %Y/%m/%d')
doc = f'''<!DOCTYPE html>
<html lang="fa" dir="rtl"><head><meta charset="utf-8">
<title>جواب‌سریع — دفتر تیم‌های هوش مصنوعی</title>
<style>
  :root {{ --bg:#f4f3f7; --card:#ffffff; --accent:#a78bdb; --accent-dark:#7c6aa8; --text:#3a3546; --muted:#8a849a; }}
  * {{ box-sizing:border-box; margin:0; }}
  body {{ background:var(--bg); color:var(--text); font-family:'Vazirmatn','Segoe UI',Tahoma,sans-serif; padding:28px 20px; line-height:1.9; }}
  .wrap {{ max-width:1000px; margin:0 auto; }}
  header {{ display:flex; flex-wrap:wrap; gap:14px; align-items:center; justify-content:space-between; margin-bottom:22px; }}
  h1 {{ font-size:26px; color:var(--accent-dark); }}
  .sub {{ color:var(--muted); font-size:14px; }}
  .btn {{ background:var(--accent); color:#fff; text-decoration:none; padding:9px 18px; border-radius:10px; font-size:14px; }}
  .stats {{ display:flex; gap:10px; flex-wrap:wrap; margin-bottom:22px; }}
  .stat {{ background:var(--card); border:1px solid #e7e2f0; border-radius:12px; padding:10px 18px; font-size:14px; }}
  .stat b {{ color:var(--accent-dark); font-size:18px; }}
  .card {{ background:var(--card); border:1px solid #e7e2f0; border-radius:14px; padding:20px 22px; margin-bottom:16px; }}
  .card-head {{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px; }}
  .card h2 {{ font-size:18px; color:var(--accent-dark); margin-bottom:6px; }}
  .team-no {{ background:#efeaf7; color:var(--accent-dark); border-radius:10px; width:34px; height:34px; display:flex; align-items:center; justify-content:center; font-weight:bold; }}
  .emps {{ display:flex; gap:6px; flex-wrap:wrap; margin-bottom:6px; }}
  .emp {{ background:#f6f3fb; border:1px solid #e7e2f0; border-radius:999px; padding:2px 12px; font-size:12.5px; color:var(--muted); }}
  details summary {{ cursor:pointer; color:var(--accent-dark); font-size:14px; margin:4px 0; }}
  .report {{ font-size:14.5px; }}
  .report h3 {{ font-size:15.5px; color:var(--accent-dark); margin:12px 0 4px; }}
  .report h4 {{ font-size:14px; margin:10px 0 2px; }}
  .report ul {{ padding-right:20px; }}
  footer {{ color:var(--muted); font-size:12.5px; margin-top:18px; text-align:center; }}
</style></head><body><div class="wrap">
<header>
  <div><h1>استارتاپ جواب‌سریع 🏢</h1>
  <div class="sub">۵ تیم عاملِ هوش مصنوعی — دفتر پیکسلی زنده در Pixel Agents</div></div>
  <a class="btn" href="{OFFICE_URL}" target="_blank">ورود به دفتر پیکسلی</a>
</header>
<div class="stats">
  <div class="stat"><b>5</b> تیم</div>
  <div class="stat"><b>10</b> کارمند عامل</div>
  <div class="stat"><b>{sessions}</b> نشست عامل Claude</div>
  <div class="stat"><b>{task_calls}</b> فراخوانی ساب‌ایجنت</div>
</div>
{''.join(cards)}
<footer>ساخته‌شده توسط Hermes Agent — {now} — گزارش‌ها نوشتهٔ واقعی همان عامل‌ها هستند (بدون دست‌کاری).</footer>
</div></body></html>'''

out_path = os.path.join(ROOT, 'dashboard.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(doc)
print('dashboard written:', out_path, f'({len(doc)//1024} KB, sessions={sessions}, task_calls={task_calls})')
