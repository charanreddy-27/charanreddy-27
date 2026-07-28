# Profile maintenance

Notes for the parts of this profile that need a human. Nothing here is visible on
the profile page itself.

## 1. Actions permissions (one-time, required for the snake)

Repo **Settings** → sidebar **Actions** → **General** → **Workflow permissions** →
**Read and write permissions** → Save.

This is the *repository's* settings, not your account settings. The URL should be
`github.com/charanreddy-27/charanreddy-27/settings/actions`.

Without it, `contribution-snake.yml` cannot push to the `output` branch.

## 2. First snake run

`.github/workflows/contribution-snake.yml` writes two SVGs to the `output` branch:

| File | Used by |
|---|---|
| `github-snake-dark.svg` | dark theme |
| `github-snake.svg` | light theme |

It runs on push to `main`, every 12 hours, and on demand
(**Actions** → *Generate contribution snake* → **Run workflow**).

The README's Contributions block renders as a broken image until that first run
goes green — the files don't exist before then.

> The old `snake.yml` and `pacman.yml` both pushed to the same `output` branch
> using `crazy-max/ghaction-github-pages`, which *replaces* the branch contents.
> They overwrote each other on every run. They've been replaced by the single
> workflow above.

## 3. Self-hosting the stats cards

The two `github-readme-stats.vercel.app` URLs in the README point at the shared
public instance. It's used by thousands of people and regularly returns
**"API rate limit exceeded"** instead of a card. Self-hosting gives you a private
rate limit. One-time, ~20 minutes.

1. **Create a token** — `github.com/settings/tokens` → *Tokens (classic)* →
   *Generate new token (classic)*. Note: `readme-stats`. Expiration: no expiration.
   Scope: tick **repo**. Copy it immediately; GitHub shows it once.
   Treat it like a password — it only ever goes into Vercel's environment-variable
   field. Never into a chat, a commit, or a public repo.
2. **Fork** `anuraghazra/github-readme-stats`.
3. **Vercel** → sign up with GitHub → Hobby (free) → *Add New… → Project* → import
   the fork. Leave every build setting alone.
4. Add environment variable `PAT_1` = your token. Deploy.
5. Verify: `https://<your-instance>.vercel.app/api?username=charanreddy-27&show_icons=true`
   should render a card.
6. In `README.md`, replace both `github-readme-stats.vercel.app` hostnames with
   your instance. The query strings stay as they are.

If a deploy fails mentioning `maxDuration`, set it to `10` in `vercel.json` — the
free tier caps there.

### Why `hide_rank=true`

The letter grade is weighted heavily toward stars and followers, so newer accounts
sit near "C" no matter how much they ship. It measures repo popularity, not work.

## 4. When something "doesn't change"

Almost always CDN cache, not a bug. Diagnose in this order:

1. **Check the file.** Open the raw URL with `?v=999` appended to bypass cache,
   view source, search for the hex colour you set. If it's there, generation
   worked and only the display is stale.
2. **Check your theme.** Dark-mode assets only render in dark mode.
3. **Check the Action ran.** Actions tab — is the newest run green and timestamped
   *after* your edit? If not, *Run workflow*.
4. **Wait.** GitHub's CDN expires on its own, minutes to a few hours.
   `Ctrl+Shift+R` clears your browser, not their servers.

## 5. Known constraints

- Scheduled Actions pause after ~60 days of repo inactivity. The snake freezes
  until you push or click *Enable workflow*.
- Stats totals won't match GitHub's own numbers exactly — different date windows
  and cache lag. A gap of a few contributions is normal.
- Top-languages reflects code volume, not skill. A template's CSS can dominate;
  exclude repos with `&exclude_repo=` if it misrepresents you.
- The banner SVGs in `assets/` can't contain working links — GitHub strips anchors
  from rendered SVG. Clickable links have to be badges in the README.
- Shields.io renders the LinkedIn glyph only on its brand blue `#0A66C2`. On any
  custom colour the logo silently vanishes and only the word remains, which is why
  that one badge doesn't match the rest of the palette.
