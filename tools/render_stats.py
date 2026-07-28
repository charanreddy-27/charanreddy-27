#!/usr/bin/env python3
"""Generate the GitHub stats card, self-hosted inside this repo's own Actions run.

Why this exists instead of github-readme-stats / streak-stats:

  Those are single shared instances used by many thousands of profiles. When
  their token budget is exhausted the card renders "API rate limit exceeded"
  instead of your numbers — which is exactly what was happening here. The usual
  fix is to fork and self-host on Vercel, which needs a personal access token
  and a hosting account.

  This does the same job with neither. It runs inside the profile repo's own
  workflow, authenticates with the automatically-provided GITHUB_TOKEN, and
  commits finished SVGs. No third-party service sits between the profile and
  the data, and the rate limit is this repo's alone.

Every network call degrades gracefully: if a source fails, the affected tiles
are dropped and the rest of the card still renders. A partial card beats a
broken image.
"""
import json, os, re, sys, pathlib, datetime, urllib.request, urllib.error

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from palettes import get

USER = os.environ.get("PROFILE_USER", "charanreddy-27")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
API = "https://api.github.com"

W, H = 1180, 300
MONO = "ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace"
SANS = "-apple-system,BlinkMacSystemFont,Segoe UI,Noto Sans,Helvetica,Arial,sans-serif"


# --------------------------------------------------------------------------- io
def _req(url, data=None, headers=None):
    h = {"User-Agent": f"{USER}-profile-card", "Accept": "application/vnd.github+json"}
    if TOKEN:
        h["Authorization"] = "Bearer " + TOKEN
    h.update(headers or {})
    r = urllib.request.Request(url, data=data, headers=h)
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.load(resp)


def rest(path):
    return _req(API + path)


def graphql(query, variables):
    return _req(API + "/graphql",
                data=json.dumps({"query": query, "variables": variables}).encode(),
                headers={"Content-Type": "application/json"})


def warn(stage, e):
    print(f"  ! {stage} failed: {type(e).__name__}: {e}", file=sys.stderr)


# ----------------------------------------------------------------- data sources
def fetch_profile():
    u = rest(f"/users/{USER}")
    return {"followers": u.get("followers", 0),
            "public_repos": u.get("public_repos", 0),
            "created": u.get("created_at", "")[:4]}


def fetch_repos():
    """All owned, non-fork repos, with aggregated language bytes."""
    repos, page = [], 1
    while page <= 5:
        batch = rest(f"/users/{USER}/repos?per_page=100&type=owner&page={page}")
        if not batch:
            break
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    own = [r for r in repos if not r.get("fork")]
    langs = {}
    for r in own:
        try:
            for name, size in rest(f"/repos/{r['full_name']}/languages").items():
                langs[name] = langs.get(name, 0) + size
        except Exception as e:
            warn(f"languages for {r['full_name']}", e)
    return {"stars": sum(r.get("stargazers_count", 0) for r in own),
            "forks": sum(r.get("forks_count", 0) for r in own),
            "repos": len(own),
            "langs": langs}


CAL_Q = """query($l:String!){user(login:$l){
  contributionsCollection{
    totalCommitContributions
    totalPullRequestContributions
    totalIssueContributions
    contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}
  }}}"""


def fetch_calendar():
    """Contribution days, newest last. GraphQL first, public HTML as fallback."""
    try:
        d = graphql(CAL_Q, {"l": USER})
        if d.get("errors"):
            raise RuntimeError(d["errors"][0].get("message", "graphql error"))
        cc = d["data"]["user"]["contributionsCollection"]
        cal = cc["contributionCalendar"]
        days = [(x["date"], x["contributionCount"])
                for wk in cal["weeks"] for x in wk["contributionDays"]]
        return {"days": days, "total": cal["totalContributions"],
                "commits": cc["totalCommitContributions"],
                "prs": cc["totalPullRequestContributions"],
                "issues": cc["totalIssueContributions"]}
    except Exception as e:
        warn("graphql calendar", e)

    try:  # public contributions fragment — no auth required
        req = urllib.request.Request(
            f"https://github.com/users/{USER}/contributions",
            headers={"User-Agent": f"{USER}-profile-card"})
        html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
        days = [(m.group(2), int(m.group(1)))
                for m in re.finditer(
                    r'data-count="(\d+)"[^>]*data-date="(\d{4}-\d\d-\d\d)"', html)]
        if not days:
            days = [(m.group(1), int(m.group(2)))
                    for m in re.finditer(
                        r'data-date="(\d{4}-\d\d-\d\d)"[^>]*data-level="(\d)"', html)]
        days.sort()
        return {"days": days, "total": sum(c for _, c in days),
                "commits": None, "prs": None, "issues": None}
    except Exception as e:
        warn("html calendar", e)
    return None


def streaks(days):
    """(current, longest). Today counts as alive only if it already has activity."""
    if not days:
        return None, None
    longest = run = 0
    for _, c in days:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)
    cur = 0
    for i in range(len(days) - 1, -1, -1):
        if days[i][1] > 0:
            cur += 1
        elif i == len(days) - 1:
            continue  # today being empty doesn't break a streak yet
        else:
            break
    return cur, longest


# -------------------------------------------------------------------- rendering
def human(n):
    if n is None:
        return "—"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M".replace(".0M", "M")
    if n >= 1_000:
        return f"{n/1_000:.1f}k".replace(".0k", "k")
    return str(n)


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(data, pal, mode):
    c = get(pal, mode)
    # Rank reads through weight, not hue: the biggest language gets the full
    # accent and each rung below steps down in opacity. A multi-hue ramp made
    # the largest bar the dullest, which fought the ordering.
    ramp_op = [1.0, 0.78, 0.58, 0.42, 0.30]
    o = []
    a = o.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
      f'fill="none" role="img" aria-label="GitHub statistics for {USER}">')
    a(f'<title>GitHub statistics for {USER}</title>')
    a('<defs>')
    a(f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
      f'<stop offset="0" stop-color="{c["bg"]}"/><stop offset=".55" stop-color="{c["panel"]}"/>'
      f'<stop offset="1" stop-color="{c["bg"]}"/></linearGradient>')
    a('</defs>')
    a(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="url(#bg)" '
      f'stroke="{c["line"]}" stroke-width="1"/>')

    # header
    a(f'<text x="40" y="46" font-family="{SANS}" font-size="17" font-weight="700" '
      f'fill="{c["text"]}">GitHub activity</text>')
    a(f'<text x="{W-40}" y="46" text-anchor="end" font-family="{MONO}" font-size="11" '
      f'fill="{c["dim"]}">generated {datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d} · self-hosted</text>')
    a(f'<line x1="40" y1="64" x2="{W-40}" y2="64" stroke="{c["line"]}" stroke-width="1"/>')

    # ---- stat tiles (left) ----
    tiles = [
        ("Contributions", human(data.get("total")), "past year"),
        ("Current streak", human(data.get("cur")), "days"),
        ("Longest streak", human(data.get("longest")), "days"),
        ("Stars earned", human(data.get("stars")), "own repos"),
        ("Public repos", human(data.get("repos")), "non-fork"),
        ("Followers", human(data.get("followers")), f"since {data.get('created','')}"),
    ]
    x0, y0, dx, dy = 40, 108, 196, 96
    for i, (label, value, sub) in enumerate(tiles):
        x, y = x0 + (i % 3) * dx, y0 + (i // 3) * dy
        a(f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="30" font-weight="700" '
          f'fill="{c["accent"] if i < 3 else c["text"]}">{esc(value)}</text>')
        a(f'<text x="{x}" y="{y+20}" font-family="{SANS}" font-size="12.5" '
          f'fill="{c["muted"]}">{esc(label)}</text>')
        a(f'<text x="{x}" y="{y+37}" font-family="{MONO}" font-size="10" letter-spacing=".6" '
          f'fill="{c["dim"]}">{esc(sub).upper()}</text>')

    # ---- language bars (right) ----
    lx = 664
    a(f'<line x1="{lx-32}" y1="88" x2="{lx-32}" y2="{H-40}" stroke="{c["line"]}" stroke-width="1"/>')
    a(f'<text x="{lx}" y="106" font-family="{SANS}" font-size="13" font-weight="600" '
      f'fill="{c["text"]}">Language mix</text>')
    a(f'<text x="{W-40}" y="106" text-anchor="end" font-family="{MONO}" font-size="10" '
      f'letter-spacing=".6" fill="{c["dim"]}">BY BYTES, OWN REPOS</text>')

    langs = data.get("langs") or {}
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]
    total_bytes = sum(langs.values()) or 1
    if top:
        bw = W - 40 - lx          # full bar track width
        for i, (name, size) in enumerate(top):
            pct = 100 * size / total_bytes
            y = 136 + i * 30
            a(f'<text x="{lx}" y="{y}" font-family="{SANS}" font-size="12.5" '
              f'fill="{c["text"]}" opacity=".92">{esc(name)}</text>')
            a(f'<text x="{W-40}" y="{y}" text-anchor="end" font-family="{MONO}" font-size="11.5" '
              f'fill="{c["muted"]}">{pct:.1f}%</text>')
            a(f'<rect x="{lx}" y="{y+7}" width="{bw}" height="6" rx="3" fill="{c["line"]}"/>')
            a(f'<rect x="{lx}" y="{y+7}" width="{max(3, bw*pct/100):.1f}" height="6" rx="3" '
              f'fill="{c["accent"]}" opacity="{ramp_op[min(i, len(ramp_op)-1)]}"/>')
    else:
        a(f'<text x="{lx}" y="150" font-family="{SANS}" font-size="12.5" '
          f'fill="{c["dim"]}">Language data unavailable this run.</text>')

    a('</svg>')
    return "\n".join(o)


# ------------------------------------------------------------------------- main
def collect(mock=False):
    if mock:
        return {"total": 1284, "cur": 17, "longest": 63, "stars": 42, "repos": 28,
                "followers": 91, "created": "2021",
                "langs": {"Python": 5_200_000, "TypeScript": 3_100_000,
                          "JavaScript": 1_400_000, "C++": 620_000, "HTML": 410_000,
                          "CSS": 180_000}}
    d = {}
    for stage, fn in (("profile", fetch_profile), ("repos", fetch_repos)):
        try:
            d.update(fn())
        except Exception as e:
            warn(stage, e)
    cal = fetch_calendar()
    if cal:
        d["total"] = cal["total"]
        d["cur"], d["longest"] = streaks(cal["days"])
    return d


if __name__ == "__main__":
    args = sys.argv[1:]
    mock = "--mock" in args
    args = [x for x in args if x != "--mock"]
    pal = args[0] if args else os.environ.get("PROFILE_PALETTE", "ember")
    outdir = pathlib.Path(args[1] if len(args) > 1 else "dist")
    outdir.mkdir(parents=True, exist_ok=True)

    data = collect(mock)
    print(f"data: { {k: v for k, v in data.items() if k != 'langs'} }")
    if not mock and not data.get("total") and not data.get("langs"):
        # Nothing at all came back — fail loudly so the workflow doesn't publish
        # an empty card over a previously good one.
        sys.exit("no data could be fetched from any source; refusing to publish")
    for mode in ("dark", "light"):
        p = outdir / f"stats-{mode}.svg"
        p.write_text(build(data, pal, mode))
        print(f"{p}  {p.stat().st_size/1024:.1f} KB")
