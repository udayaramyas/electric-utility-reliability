"""Build a self-contained browser preview from the prepared EIA state CSV."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
with (ROOT / "data" / "state_totals.csv").open(newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

payload = [{
    "state": r["state"],
    "with": float(r["saidi_with_med_minutes"]),
    "without": float(r["saidi_without_med_minutes"]),
    "customers": float(r["customer_count_any_standard"]),
} for r in rows]
data = json.dumps(payload, separators=(",", ":"))
top = sorted(payload, key=lambda r: r["with"], reverse=True)[:12]
max_value = max(r["with"] for r in top) * 1.12
bars = []
for i, row in enumerate(top):
    y = 102 + i * 36
    bars.append(
        f'<text x="118" y="{y+13}" text-anchor="end" class="state">{row["state"]}</text>'
        f'<rect x="136" y="{y}" width="{row["with"]/max_value*690:.1f}" height="13" rx="4" fill="#087e8b"><title>{row["state"]}: {row["with"]} minutes, with MED</title></rect>'
        f'<rect x="136" y="{y+16}" width="{row["without"]/max_value*690:.1f}" height="13" rx="4" fill="#f0a43a"><title>{row["state"]}: {row["without"]} minutes, without MED</title></rect>'
    )
svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 590" role="img" aria-labelledby="title desc">
<title id="title">Top 12 state SAIDI values with and without major event days</title><desc id="desc">Horizontal bar chart comparing EIA 2025 state reliability values, in minutes per customer-year.</desc>
<style>text{font-family:Arial,sans-serif;fill:#182634}.title{font-size:23px;font-weight:700}.sub{font-size:13px;fill:#52616b}.state{font-size:13px}.legend{font-size:12px;fill:#52616b}.foot{font-size:11px;fill:#667782}</style>
<rect width="1000" height="590" rx="16" fill="#fff"/><text x="36" y="42" class="title">Reported interruption duration by state</text><text x="36" y="66" class="sub">Top 12 SAIDI values · EIA Form 861 · 2025 · minutes per customer-year</text>
<rect x="750" y="52" width="10" height="10" rx="3" fill="#087e8b"/><text x="766" y="61" class="legend">With MED</text><rect x="855" y="52" width="10" height="10" rx="3" fill="#f0a43a"/><text x="871" y="61" class="legend">Without MED</text>
'''+''.join(bars)+'''<text x="36" y="565" class="foot">State summary values use EIA's “Any Standard” methodology. State comparisons are not customer-weighted national rates.</text></svg>'''
page = r'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Electric Reliability | EIA 861</title>
<style>
:root{font-family:Inter,Segoe UI,Arial,sans-serif;color:#182634;background:#f3f6f8}*{box-sizing:border-box}body{margin:0}.wrap{max-width:1120px;margin:auto;padding:32px 22px}.eyebrow{color:#087e8b;text-transform:uppercase;letter-spacing:.12em;font-size:12px;font-weight:700}h1{font-size:30px;margin:7px 0}.sub{color:#52616b;margin:0 0 24px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.card,.panel{background:white;border:1px solid #e1e8ec;border-radius:12px;padding:18px;box-shadow:0 3px 14px #1735480a}.label{font-size:12px;color:#657680}.value{font-size:27px;font-weight:700;margin-top:5px}.unit{font-size:12px;color:#657680}.panel{margin-top:16px}.head{display:flex;justify-content:space-between;gap:12px;align-items:center}h2{font-size:17px;margin:0 0 10px}select{border:1px solid #ced9df;border-radius:7px;padding:8px;background:white}svg{width:100%;height:auto;display:block}.legend{font-size:12px;color:#52616b;display:flex;gap:16px}.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px}.note{font-size:12px;color:#667782;line-height:1.5;margin-top:15px}.source{border-top:1px solid #e6ecef;padding-top:12px}@media(max-width:700px){.grid{grid-template-columns:1fr}.wrap{padding:20px 14px}}
</style><body><main class="wrap"><div class="eyebrow">U.S. Electric Utility Reliability · EIA Form 861 · 2025</div><h1>How do major event days change reported reliability?</h1><p class="sub">State summaries compare SAIDI with and without major event days (MED). Each bar is a state/DC aggregate.</p>
<section class="grid"><div class="card"><div class="label">States / District of Columbia</div><div class="value" id="n">—</div><div class="unit">EIA state summary records</div></div><div class="card"><div class="label">Mean SAIDI, with MED</div><div class="value" id="avg1">—</div><div class="unit">minutes per customer-year</div></div><div class="card"><div class="label">Mean SAIDI, without MED</div><div class="value" id="avg2">—</div><div class="unit">minutes per customer-year</div></div></section>
<section class="panel"><div class="head"><h2>State comparison · SAIDI</h2><select id="sort"><option value="with">Sort by with MED</option><option value="without">Sort by without MED</option><option value="state">Sort by state</option></select></div><div class="legend"><span><i class="dot" style="background:#007c91"></i>With MED</span><span><i class="dot" style="background:#f0a43a"></i>Without MED</span></div><svg id="chart" viewBox="0 0 1000 650" role="img" aria-label="Horizontal bar comparison of SAIDI by state"></svg><p class="note">SAIDI is the System Average Interruption Duration Index. State summaries use EIA's “Any Standard” methodology. This is an unweighted comparison of reported state values, not a customer-weighted national rate; reporting coverage and methods vary.</p></section>
<p class="note source">Source: U.S. Energy Information Administration, Form EIA-861, 2025 final data. This self-contained preview is a browser prototype for the planned Power BI report, not a .pbix file.</p></main>
<script>const rows=__DATA__;const fmt=n=>Math.round(n).toLocaleString();document.querySelector('#n').textContent=rows.length;document.querySelector('#avg1').textContent=fmt(rows.reduce((s,r)=>s+r.with,0)/rows.length);document.querySelector('#avg2').textContent=fmt(rows.reduce((s,r)=>s+r.without,0)/rows.length);function draw(){let key=document.querySelector('#sort').value;let a=[...rows].sort((x,y)=>key==='state'?x.state.localeCompare(y.state):y[key]-x[key]);let max=Math.max(...a.map(x=>x.with))*1.05;let svg=document.querySelector('#chart'),h=650,rowH=11.8,left=55,barW=850;svg.innerHTML='';a.forEach((r,i)=>{let y=10+i*rowH, x1=left+r.with/max*barW, x2=left+r.without/max*barW;svg.insertAdjacentHTML('beforeend',`<text x="${left-8}" y="${y+8}" text-anchor="end" font-size="10" fill="#42545e">${r.state}</text><rect x="${left}" y="${y}" width="${r.with/max*barW}" height="4.5" rx="2" fill="#007c91"><title>${r.state}: ${r.with} min with MED</title></rect><rect x="${left}" y="${y+5}" width="${r.without/max*barW}" height="4.5" rx="2" fill="#f0a43a"><title>${r.state}: ${r.without} min without MED</title></rect>`)});}document.querySelector('#sort').addEventListener('change',draw);draw();</script></body></html>'''.replace("__DATA__", data)
(ROOT / "outputs").mkdir(exist_ok=True)
(ROOT / "outputs" / "reliability_preview.html").write_text(page, encoding="utf-8")
(ROOT / "outputs" / "reliability_preview.svg").write_text(svg, encoding="utf-8")
print(f"Wrote outputs/reliability_preview.html with {len(rows)} state/DC records")
