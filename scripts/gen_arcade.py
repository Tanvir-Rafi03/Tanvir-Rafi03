#!/usr/bin/env python3
"""
NO. 03 — ONE YEAR
A year of real GitHub contributions typeset as an editorial data spread:
precise squares in a vermilion tint ramp on paper stock, with a slow scan
travelling across the field. Pure SVG. No JS, no external assets.

Usage:  python3 scripts/gen_arcade.py <username> [out.svg]
Needs:  GH_TOKEN / GITHUB_TOKEN in env (GraphQL contributions API).
"""
import json, os, subprocess, sys, xml.dom.minidom
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import *

ROWS  = 7
CELL, GAP = 15.0, 4.5
PITCH = CELL + GAP
Y0    = 214
RAMP  = ["#e2ddd0", "#f4c0af", "#ef9070", "#ec5c33", "#e8330a"]
MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]


def fetch(user):
    q = """{ user(login: "%s") { contributionsCollection { contributionCalendar {
        totalContributions
        weeks { firstDay contributionDays { contributionCount date weekday } } } } } }""" % user
    out = subprocess.run(["gh","api","graphql","-f","query="+q],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def level(c, peak):
    if c <= 0: return 0
    q = c / peak if peak else 1
    return 4 if q > .5 else 3 if q > .25 else 2 if q > .1 else 1


def build(cal, user):
    uid   = "c"
    weeks = cal["weeks"]; cols = len(weeks); total = cal["totalContributions"]
    day, dates = {}, {}
    for c, wk in enumerate(weeks):
        for d in wk["contributionDays"]:
            day[(c, int(d["weekday"]))]   = d["contributionCount"]
            dates[(c, int(d["weekday"]))] = d["date"]
    peak   = max(day.values()) if day else 0
    active = sum(1 for v in day.values() if v > 0)
    seq  = [day[(c,r)] for c in range(cols) for r in range(ROWS) if (c,r) in day]
    best = run = 0
    for v in seq:
        run = run + 1 if v > 0 else 0
        best = max(best, run)

    span  = W - MARGIN*2
    pitch = (span + GAP) / cols
    cw    = pitch - GAP

    cells = []
    for c in range(cols):
        for r in range(ROWS):
            if (c,r) not in day: continue
            n  = day[(c,r)]
            lv = level(n, peak)
            x  = MARGIN + c*pitch
            y  = Y0 + r*PITCH
            ph = (c*0.055 + r*0.09) % 4.5
            anim = (f'<animate attributeName="opacity" values="1;.55;1" keyTimes="0;.5;1" '
                    f'dur="4.5s" begin="{ph:.2f}s" repeatCount="indefinite"/>') if lv else ''
            cells.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cw:.1f}" height="{CELL}" '
                         f'fill="{RAMP[lv]}" opacity="1">{anim}<title>{dates[(c,r)]}: {n}</title></rect>')

    months, seen = [], None
    for c, wk in enumerate(weeks):
        m = int(wk["firstDay"][5:7])
        if m != seen and c < cols-1:
            months.append(label(uid, MARGIN + c*pitch, Y0-16, MONTHS[m-1], INK35, 8.5))
            seen = m

    H = Y0 + ROWS*PITCH + 132
    stats = [("CONTRIBUTIONS", total), ("ACTIVE DAYS", active),
             ("BUSIEST DAY", peak), ("LONGEST RUN", best)]
    stat_svg = ""
    for i,(k,v) in enumerate(stats):
        x = grid(i*1.62)
        stat_svg += (rule(x, H-96, x + COL*1.35)
                     + label(uid, x, H-76, k)
                     + f'<text class="d{uid}" x="{x}" y="{H-46}" font-size="30" font-weight="700" '
                       f'letter-spacing="-1.4" fill="{INK}">{v}</text>')

    gw = span
    body = f'''
  {label(uid, MARGIN, 46, "THE RECORD", RED)}
  {label(uid, W-MARGIN, 46, "NO. 02", INK35, anchor="end")}
  <text class="d{uid}" x="{MARGIN-4}" y="118" font-size="62" font-weight="800" letter-spacing="-3" fill="{INK}">One year of work</text>
  <text class="d{uid}" x="{W-MARGIN}" y="118" font-size="62" font-weight="800" letter-spacing="-3" fill="{RED}" text-anchor="end">{total}</text>
  {rule(MARGIN, 150, W-MARGIN, INK, 2)}
  {label(uid, MARGIN, 176, f"{weeks[0]['firstDay']} — {weeks[-1]['contributionDays'][-1]['date']}", INK35)}
  {"".join(months)}
  {"".join(cells)}
  <g clip-path="url(#gf{uid})">
    <rect class="scan{uid}" x="0" y="{Y0-6}" width="150" height="{ROWS*PITCH+6}" fill="url(#sc{uid})"/>
  </g>
  {rule(MARGIN, Y0 + ROWS*PITCH + 22, W-MARGIN)}
  {stat_svg}
  {rule(MARGIN, H-24, W-MARGIN, INK, 2)}'''

    xd = f'''
  <linearGradient id="sc{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{INK}" stop-opacity="0"/>
    <stop offset="50%" stop-color="{INK}" stop-opacity=".10"/>
    <stop offset="100%" stop-color="{INK}" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="gf{uid}"><rect x="{MARGIN}" y="{Y0-6}" width="{gw}" height="{ROWS*PITCH+6}"/></clipPath>'''
    xc = f'''
    @keyframes scan{uid} {{ 0% {{ transform:translateX({MARGIN-160}px) }} 100% {{ transform:translateX({MARGIN+gw+20}px) }} }}
    .scan{uid} {{ animation:scan{uid} 7s cubic-bezier(.45,0,.25,1) infinite }}'''
    return panel(uid, H, body, xd, xc)


if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "Tanvir-Rafi03"
    out  = sys.argv[2] if len(sys.argv) > 2 else "assets/02-record.svg"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w").write(build(fetch(user), user))
    xml.dom.minidom.parse(out)
    print(f"wrote {out} ({os.path.getsize(out):,} bytes)")
