#!/usr/bin/env python3
"""
CHUNK MAP — a year of real GitHub contributions rendered as placed blocks.
Quiet days are dirt; busy days become grass, emerald and diamond ore.
Pure SVG, pixel-snapped. No JS, no external assets.

Usage:  python3 scripts/gen_arcade.py <username> [out.svg]
Needs:  GH_TOKEN / GITHUB_TOKEN in env (GraphQL contributions API).
"""
import json, os, subprocess, sys, xml.dom.minidom
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mc import *

ROWS = 7
# 0 dirt · 1 coarse grass · 2 grass · 3 emerald · 4 diamond
TIER = [("#6b4423", "#54341b", None),
        ("#8a7b3f", "#6d612f", None),
        (GRASS_T, GRASS_S, None),
        ("#9c9c9c", "#7b7b7b", EMERALD),
        ("#9c9c9c", "#7b7b7b", DIAMOND)]
NAMES = ["DIRT", "COARSE DIRT", "GRASS BLOCK", "EMERALD ORE", "DIAMOND ORE"]
MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]


def fetch(user):
    q = """{ user(login: "%s") { contributionsCollection { contributionCalendar {
        totalContributions
        weeks { firstDay contributionDays { contributionCount date weekday } } } } } }""" % user
    out = subprocess.run(["gh","api","graphql","-f","query="+q],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def lvl(c, peak):
    if c <= 0: return 0
    q = c / peak if peak else 1
    return 4 if q > .5 else 3 if q > .25 else 2 if q > .1 else 1


def build(cal, user):
    uid   = "k"
    weeks = cal["weeks"]; cols = len(weeks); total = cal["totalContributions"]
    day, dates = {}, {}
    for c, wk in enumerate(weeks):
        for d in wk["contributionDays"]:
            day[(c, int(d["weekday"]))]   = d["contributionCount"]
            dates[(c, int(d["weekday"]))] = d["date"]
    peak   = max(day.values()) if day else 0
    active = sum(1 for v in day.values() if v > 0)
    seq = [day[(c,r)] for c in range(cols) for r in range(ROWS) if (c,r) in day]
    best = run = 0
    for v in seq:
        run = run + 1 if v > 0 else 0
        best = max(best, run)

    B, GAP = 18, 2
    P      = B + GAP
    gw     = cols*P - GAP
    X0     = (W - gw)//2
    Y0     = 148
    H      = Y0 + ROWS*P + 150

    cells, counts = [], [0]*5
    for c in range(cols):
        for r in range(ROWS):
            if (c,r) not in day: continue
            n  = day[(c,r)]
            L  = lvl(n, peak)
            counts[L] += 1
            top, side, ore = TIER[L]
            x, y = X0 + c*P, Y0 + r*P
            g = block(x, y, B, top, side, ore)
            if L >= 3:
                g = (f'<g class="or{uid}" style="animation-delay:{(c*0.07+r*0.11)%2.8:.2f}s">{g}</g>')
            cells.append(f'{g}<rect x="{x}" y="{y}" width="{B}" height="{B}" fill="#0000"><title>{dates[(c,r)]}: {n}</title></rect>')

    months, seen = [], None
    for c, wk in enumerate(weeks):
        m = int(wk["firstDay"][5:7])
        if m != seen and c < cols-1:
            months.append(text(MONTHS[m-1], X0 + c*P, Y0-22, 2, "#c8c8c8"))
            seen = m

    legend, lx = "", X0
    for i in range(5):
        legend += block(lx, H-118, 16, TIER[i][0], TIER[i][1], TIER[i][2])
        legend += text(NAMES[i], lx+22, H-114, 2, "#d0d0d0")
        lx += 26 + text_w(NAMES[i], 2) + 26

    stats = [("BLOCKS PLACED", total), ("DAYS MINED", active),
             ("BEST DAY", peak), ("LONGEST RUN", best)]
    st, sx = "", X0
    for k, v in stats:
        st += text(k, sx, H-84, 2, "#a8a8a8")
        st += text(str(v), sx, H-62, 4, GOLD, True, GOLD_SH)
        sx += 300

    body = (f'<rect width="{W}" height="{H}" fill="#2e2e2e"/>'
            f'<rect width="{W}" height="{H}" fill="url(#st{uid})" opacity=".55"/>'
            + bevel(X0-24, 56, gw+48, H-96, "#3c3c3c", "#565656", "#1e1e1e", 5)
            + text("CHUNK MAP", X0, 82, 4, GOLD, True, GOLD_SH)
            + text(f"{weeks[0]['firstDay']} TO {weeks[-1]['contributionDays'][-1]['date']}",
                   X0+gw, 86, 2, "#b4b4b4", True, None, "end")
            + "".join(months) + "".join(cells) + legend + st)

    defs = f'''
    <pattern id="st{uid}" width="32" height="32" patternUnits="userSpaceOnUse">
      <rect width="32" height="32" fill="#7f7f7f"/><rect x="0" y="0" width="16" height="16" fill="#8b8b8b"/>
      <rect x="16" y="16" width="16" height="16" fill="#737373"/><rect x="8" y="18" width="8" height="8" fill="#6b6b6b"/>
    </pattern>'''
    css = f'''
    @keyframes or{uid} {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.62 }} }}
    .or{uid} {{ animation:or{uid} 2.8s ease-in-out infinite }}'''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="Chunk map — {total} blocks placed" shape-rendering="crispEdges">'
            f'<defs>{defs}<style><![CDATA[{css}]]></style></defs>{body}</svg>')


if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "Tanvir-Rafi03"
    out  = sys.argv[2] if len(sys.argv) > 2 else "assets/02-chunkmap.svg"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w").write(build(fetch(user), user))
    xml.dom.minidom.parse(out)
    print(f"wrote {out} ({os.path.getsize(out):,} bytes)")
