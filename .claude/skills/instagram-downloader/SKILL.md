# instagram-downloader

A self-contained skill for pulling media off Instagram and saving it to disk. It
**classifies the request, runs the safety/scope gates, routes to the right tool, and
verifies the result.** Everything needed is in this one file — no external references.

The skill does not scrape Instagram by hand. It orchestrates three battle-tested
command-line downloaders, each chosen for what it does best:

| Tool | Best at | Install |
|------|---------|---------|
| **gallery-dl** | the default for everything: posts, reels, carousels, whole profiles, stories, highlights, tagged/saved | `pip install gallery-dl` |
| **yt-dlp** | a single reel/video at the highest quality (best audio+video muxing) | `pip install yt-dlp` |
| **instaloader** | full profile archives with metadata, story highlights, original-resolution profile pics | `pip install instaloader` |
| **Playwright** (fallback) | a stubborn single post/reel where the CLI tools hit a login wall — opens the page in a mobile-emulated browser and sniffs the `.mp4` from network traffic | `npx playwright install chromium` |

"Download with the default tool" means **gallery-dl** unless the decision tree points
elsewhere. **Never invent flags or endpoints** — use the command cookbook below.

---

## Step 0 — Responsible-use gate (quick, always)

This tool fetches other people's content, so a one-line sanity check protects the user.
Proceed when **any** of these is true, and you can assume it unless something looks off:

- The content is the user's own, or they have permission to download it.
- It is public content the user wants for personal/offline use, research, or archiving.
- It is content they plan to legitimately reuse and will credit/license appropriately.

Gently pause and ask only if the request looks aimed at impersonation, harassment, or
republishing someone's content as the user's own. Don't lecture; one clarifying question is
enough. Bulk-scraping many accounts or evading blocks is out of scope — say so plainly and
offer the legitimate single-target path instead.

## Step 1 — Classify the input

Match exactly what the user gave you to a row. The URL shape tells you the media type.
Strip query strings (`?igshid=…`, `?utm_source=…`) first — they're tracking junk and
occasionally break tools.

| Input | Media type | Auth needed? |
|-------|-----------|--------------|
| `instagram.com/p/<code>/` | feed post — single image, video, **or carousel** (up to 20 slides) | no (unless private) |
| `instagram.com/reel/<code>/` or `/reels/` | reel (short video) | no (unless private) |
| `instagram.com/tv/<code>/` | IGTV / long video | no (unless private) |
| `instagram.com/stories/<user>/<id>/` | a story | **yes** |
| `instagram.com/stories/highlights/<id>/` | a story highlight | **yes** |
| `instagram.com/<user>/saved/` | the user's own saved posts | **yes** (only your own) |
| `instagram.com/explore/tags/<tag>/` | a hashtag feed | bulk; scope gate + heavy rate-limit risk |
| `instagram.com/<username>/` or `@username` or bare `username` | a **whole profile** | no for public; yes for private |
| "their profile picture" / "avatar" / "pfp" | profile picture at full res | no (unless private) |
| `l.instagram.com/…` / `instagr.am/…` | redirect / short link | resolve with `curl -sIL <url>`, then reclassify |

The **shortcode** is the alphanumeric ID after `/p/`, `/reel/`, or `/tv/` — it uniquely
identifies the media and is the filename most tools default to.

## Step 2 — Auth gate (only when the table above says "yes")

Stories, highlights, private accounts, and your own saved posts require a logged-in session.
The skill never asks for a password — it borrows cookies from a browser the user is already
logged into:

- Default: `--cookies-from-browser firefox` (or `chrome`, `chromium`, `safari`, `edge`,
  `brave`, `opera`, `vivaldi`). gallery-dl and yt-dlp both support this flag; instaloader
  uses session login (see cookbook).
- Tell the user which browser you'll read cookies from and that they must be logged into
  Instagram there. If you don't know, ask once.
- If the content is public, **skip this** — adding cookies unnecessarily can raise the
  rate-limit risk.
- On macOS, Chrome cookie extraction may require granting the terminal keychain access the
  first time; if it fails, use `firefox` or a cookies.txt file.

**Security:** never print, log, or commit cookie files or session files. A leaked Instagram
session is a full account takeover.

## Step 3 — Scope gate (only for whole-profile / hashtag requests)

Downloading one post is cheap and needs no confirmation — just do it. Downloading an entire
profile can be hundreds of files and can get the user rate-limited or temporarily blocked,
so **confirm scope before a bulk pull**:

1. State what you're about to fetch ("all posts + reels from @account — could be N items").
2. Offer to narrow: posts only, reels only, last N items, or since a date.
3. Mention large pulls are paced to avoid rate limits and can take a while.
4. Wait for a yes before firing.

For a single URL there is no scope gate.

## Step 4 — Tooling check

Confirm the tool you need is installed (`gallery-dl --version`, etc.); install with
`pip install <tool>` if missing. If pip reports an **externally-managed environment**
(common on recent macOS/Linux), use `pipx install <tool>` or a virtualenv instead of
fighting the system Python. `ffmpeg` is recommended — yt-dlp uses it to mux best-quality
video+audio (`brew install ffmpeg` / `apt install ffmpeg`).

Keep tools current. Instagram changes its internals often; an outdated tool is the #1 cause
of "it just stopped working." `pip install -U gallery-dl yt-dlp instaloader` before assuming
a bug is unfixable.

## Step 5 — Decision tree: which tool?

| Goal | Tool | Why |
|------|------|-----|
| Any post, carousel, story, highlight, profile, tagged/saved | **gallery-dl** | broadest; handles multi-image carousels and login-gated media cleanly |
| One reel/video, want the best possible quality | **yt-dlp** | superior format selection + audio/video muxing for single videos |
| Full profile archive **with captions/metadata** as JSON sidecars | **instaloader** | writes rich per-post metadata; built for archiving |
| Profile picture at original resolution | **instaloader** (`--profile-pic-only`) or gallery-dl | both expose the full-res avatar |
| A single post/reel where **both gallery-dl and yt-dlp fail** on a public URL (login wall / parser break) | **Playwright** (mobile emulation) | renders the page like a phone and captures the real `.mp4` URL from network traffic — last resort, single items only |

If gallery-dl fails on a specific item (e.g. a stubborn reel), fall back to yt-dlp for that
item rather than abandoning the whole job. If **both** CLI tools fail on a public single
item, use the Playwright mobile fallback (cookbook below). Note what worked in your summary.

## Step 6 — Output layout

Save into a predictable tree so files are findable and re-runs don't clobber. Configure the
tool's output directory (`-D` / `-P` / `--dirname-pattern`) rather than moving files after.
If the user names a destination, honor it.

```
downloads/instagram/<username>/
├── posts/      feed posts & carousels
├── reels/      reels & video
├── stories/    stories & highlights (dated)
└── profile/    profile picture
```

Use Instagram's native filenames where the tool provides them — they encode the shortcode
and date.

## Step 7 — Verify & report

1. List what landed (counts by type, total size). For a carousel, confirm **all** slides
   came down, not just the first — a common silent failure.
2. Spot-check that videos have both audio and video and aren't 0 bytes.
3. Open the folder (`open` macOS / `xdg-open` Linux / `explorer` Windows) and give the path.
4. On failure, consult the troubleshooting table below before retrying — most failures are
   auth, rate-limit, or a login wall, and blindly re-running won't fix them.

## Execution checklist

1. Responsible-use gate (Step 0) — proceed unless something looks off.
2. Classify the input (Step 1) → media type + auth need.
3. If auth is needed, set up `--cookies-from-browser` (Step 2).
4. If it's a whole profile/hashtag, run the scope gate and get a yes (Step 3).
5. Confirm the tool is installed (Step 4); install if missing.
6. Pick the tool (Step 5); build the exact command from the cookbook.
7. Download into the output layout (Step 6).
8. Verify completeness — carousels especially — and report with the folder path (Step 7).
9. On failure, diagnose via the troubleshooting table — don't blindly resubmit.

---

# Command cookbook

All commands write into `downloads/instagram/<username>/<type>/`. Adjust `-D` / `-P` / `-o`
to match.

## gallery-dl (default)

The general-purpose workhorse — handles carousels, profiles, stories, highlights without
special casing.

```bash
# A single post / carousel (downloads ALL carousel slides automatically)
gallery-dl -D "downloads/instagram/<user>/posts" "https://www.instagram.com/p/<code>/"

# A single reel
gallery-dl -D "downloads/instagram/<user>/reels" "https://www.instagram.com/reel/<code>/"

# A whole profile (everything). Honor the scope gate first.
gallery-dl -D "downloads/instagram/<user>" "https://www.instagram.com/<user>/"

# Just the profile's reels, or just posts:
gallery-dl "https://www.instagram.com/<user>/reels/"
gallery-dl "https://www.instagram.com/<user>/"      # posts tab

# Stories / highlights (login required)
gallery-dl --cookies-from-browser firefox "https://www.instagram.com/stories/<user>/"
gallery-dl --cookies-from-browser firefox "https://www.instagram.com/stories/highlights/<id>/"

# Limit a bulk pull to the most recent N items (range is 1-based, inclusive)
gallery-dl --range "1-30" "https://www.instagram.com/<user>/"

# Pace a bulk pull to dodge rate limits (randomized seconds)
gallery-dl --sleep 2-5 --sleep-request 2-4 "https://www.instagram.com/<user>/"

# Resume / skip already-downloaded items on a re-run (idempotent archive)
gallery-dl --download-archive "downloads/instagram/<user>/.archive" "https://www.instagram.com/<user>/"
```

Useful flags: `--write-metadata` (JSON sidecar per file), `-g` (print URLs only, preview
what *would* be fetched), `--cookies cookies.txt` (Netscape-format cookie file when browser
extraction is blocked).

## yt-dlp (single video, best quality)

For one reel/IGTV at top quality, or when gallery-dl chokes on a specific video.

```bash
# Best video+audio, named by uploader + title
yt-dlp -P "downloads/instagram/<user>/reels" \
       -o "%(uploader_id)s - %(title).80s [%(id)s].%(ext)s" \
       "https://www.instagram.com/reel/<code>/"

# Force an mp4 container (most compatible). Needs ffmpeg.
yt-dlp -f "bv*+ba/b" --merge-output-format mp4 "https://www.instagram.com/reel/<code>/"

# Login-gated video
yt-dlp --cookies-from-browser firefox "https://www.instagram.com/reel/<code>/"
```

`bv*+ba/b` = best video + best audio, falling back to best combined.

## instaloader (archives & profile pics)

Built for archiving — writes captions, timestamps, location as metadata alongside media.

```bash
# Full profile archive with metadata (login recommended for completeness)
instaloader --dirname-pattern "downloads/instagram/{profile}" <username>

# Profile picture only, original resolution
instaloader --profile-pic-only <username>

# Session login (interactive, once; caches a session file) — or import browser cookies
instaloader --login <your_ig_username>
instaloader --load-cookies firefox

# Stories / highlights (login required)
instaloader --login <your_user> --stories <username>
instaloader --login <your_user> --highlights <username>

# Posts since a date; skip media you already have (resumable)
instaloader --post-filter "date_utc >= datetime(2024,1,1)" <username>
instaloader --fast-update <username>
```

Trim with `--no-videos`, `--no-pictures`, `--no-captions`, `--no-metadata-json`; cap with
`--count N`.

## Playwright — mobile-emulated browser (last-resort fallback)

Use this **only** when gallery-dl *and* yt-dlp both fail on a public single item. It opens the
page in a headless Chromium emulating an iPhone, lets the reel start, and grabs the real
`.mp4` URL straight off the network — what the CLI parsers couldn't reach. Single items only;
do **not** use it for bulk profile pulls.

This skill keeps no permanent script. At run time, write the snippet below to a temp file,
run it, read the printed link, then delete the temp file. One-time setup:

```bash
npm i -g playwright >/dev/null 2>&1 || npx -y playwright --version >/dev/null   # ensure CLI
npx playwright install chromium                                                # browser, once
```

Then create and run a throwaway script (delete it after):

```bash
cat > /tmp/ig-vidlink.mjs <<'JS'
import { chromium, devices } from 'playwright';
const url = process.argv[2];
const found = new Set();
const isVid = (u, ct='') => /\.mp4(\?|$)/i.test(u) || /\.m3u8(\?|$)/i.test(u) || /^video\//i.test(ct);
const b = await chromium.launch({ headless: true });
const ctx = await b.newContext({ ...devices['iPhone 13'], locale: 'en-US' });
const p = await ctx.newPage();
p.on('response', r => { const u=r.url(), ct=r.headers()['content-type']||''; if (isVid(u,ct)) found.add(u.split('&bytestart=')[0]); });
try {
  await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
  await p.waitForTimeout(4000);
  try { await p.locator('video').first().click({ timeout: 3000 }); await p.waitForTimeout(2500); } catch {}
  const dom = await p.evaluate(() => {
    const o=[]; const og=document.querySelector('meta[property="og:video"],meta[property="og:video:url"],meta[property="og:video:secure_url"]');
    if (og?.content) o.push(og.content);
    for (const v of document.querySelectorAll('video')) { if (v.src) o.push(v.src); for (const s of v.querySelectorAll('source')) if (s.src) o.push(s.src); }
    return o;
  });
  dom.forEach(u => { if (u && !u.startsWith('blob:')) found.add(u); });
} finally { await b.close(); }
if (!found.size) { console.error('no video link found (login wall / rate-limit / blob stream)'); process.exit(2); }
for (const u of found) console.log(u);
JS
# strip tracking query first, then run:
node /tmp/ig-vidlink.mjs "https://www.instagram.com/reel/<code>/"
rm -f /tmp/ig-vidlink.mjs
```

Once you have the `.mp4` URL, download it normally (e.g. `gallery-dl "<mp4-url>"`,
`yt-dlp "<mp4-url>"`, or `curl -L -o reel.mp4 "<mp4-url>"`) into the Step 6 output layout.

Notes:
- For login-gated content, add `storageState` / cookies to `newContext(...)` — but prefer the
  CLI tools' `--cookies-from-browser` for that; this fallback targets *public* items the
  parsers choke on.
- If nothing is captured, the video may stream via `blob:` — re-run with
  `headless: false` to watch, or fall back to yt-dlp with fresh cookies.

---

# Rate limits & pacing

Instagram aggressively rate-limits unauthenticated and high-volume access. A 401/403/429, a
sudden "login required" on public content, or empty results usually means rate-limiting, not
a broken URL.

- **Single items are safe.** Bulk profile/hashtag pulls are where blocks happen.
- For bulk jobs, add delays: gallery-dl `--sleep 2-5 --sleep-request 2-4`; instaloader is
  paced by default.
- If you hit a wall, **stop** — don't hammer. Wait 10–30 min, or authenticate with cookies
  (a logged-in session has higher limits), then resume with `--download-archive` /
  `--fast-update` so you don't re-fetch what you already have.
- A logged-in session reduces but doesn't eliminate rate-limiting. Heavy automated
  downloading can still get an account temporarily action-blocked — keep volumes reasonable.

# Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `401` / `403` / "login required" on a **public** post | rate-limited, or tool out of date | update the tool; wait; add `--cookies-from-browser` |
| `429 Too Many Requests` | rate limit hit | stop, wait 10–30 min, authenticate, add `--sleep`, resume with archive |
| Only the **first** image of a carousel downloaded | tool/version quirk | update gallery-dl; verify slide count vs files; re-run that post |
| Reel saves but has **no audio** / won't play | missing `ffmpeg` or bad muxing | install `ffmpeg`; use yt-dlp `-f "bv*+ba/b" --merge-output-format mp4` |
| Stories/highlights return nothing | not logged in, or content expired (24h) | add cookies / `instaloader --login`; stories are ephemeral and may be gone |
| Private account, no media | not following / not logged in as an approved follower | authenticate as an account that follows it; otherwise inaccessible |
| `Could not extract` / parser error | Instagram changed internals | `pip install -U` the tool; if still broken, fall back to a different tool |
| Both gallery-dl **and** yt-dlp fail on a **public** single item | parser break / login wall on the CLI path | use the Playwright mobile fallback (cookbook) to sniff the `.mp4`, then download that URL directly |
| `externally-managed-environment` on install | system Python is protected | use `pipx` or a virtualenv |
| Chrome cookie extraction fails on macOS | keychain access not granted | grant terminal keychain access, or use `firefox`, or export a cookies.txt |
| 0-byte or truncated file | interrupted download / rate limit mid-fetch | delete the partial, re-run with the download archive so only the gap re-fetches |

When a tool fails on one specific item but works on others, fall back to the other tool
(gallery-dl ↔ yt-dlp) rather than abandoning the whole job, and note which tool succeeded.

---

# Optional: hand off to KARYAWAN.AI generation

This skill is hosted on KARYAWAN.AI, which also offers AI generation. If the user's intent
after downloading is clearly to *create* something — "download this reel so I can remix it",
"grab this photo and turn it into a video" — offer to pass the saved file into the relevant
Karyawan generation tool (e.g. `karyawan_gen_run` for image-to-video). Downloading and
generating are separate steps; only chain them when the user asks.
