# 23 November 2026 — World News in One Image

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/joyrichh/makefun-news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/joyrichh/makefun-news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

Make.Fun competition entry ([`news-image-20261123`](https://make.fun/bounty/news-image-20261123)) by [@joyrichh](https://github.com/joyrichh).
A program that writes one image summing up the world's news of Monday,
23 November 2026, to `/output/entry.png`.

## The image

A 1024×1024 PNG infographic — "Monday 23 November 2026: the day's biggest
stories, in one image" — with six main stories and an "Also today" strip:

1. **Tech** — Huang is back as Nvidia CEO.
   Reinstated 11 days after quitting; shares soar 33%, Nasdaq jumps 6%.
2. **War** — Ukraine sinks Russian warship off Libya.
   Seven sea drones sink the corvette Merkury at Benghazi; a cargo ship
   is hit too.
3. **Climate** — COP31 ends with no climate deal.
   After record overtime in Antalya, nations reject a pact with no
   fossil-fuel plan.
4. **Asia** — 24 dead in Indonesia factory fire.
   Blaze guts a sweets factory in Banten; about 30 workers still missing.
5. **Trade** — US blacklists Megaspeed.
   Singapore chip firm accused of diverting AI chips to China joins the
   Entity List.
6. **Diplomacy** — EU unveils 22nd Russia sanctions.
   60 banks cut from SWIFT, a crypto task force, and no Russian flag at
   EU sport.

Also today:

- Russian strikes kill 15 in Kyiv region; flats collapse in Dymer.
- US sanctions Iran's shadow banks: two dozen exchange houses hit.
- Mexico captures 'El Chapo Isidro' and vows to try him at home.

The stories were verified on 24 November 2026 against Reuters, CNN, AP,
Al Jazeera and US Treasury reporting and are retained in `news.json`.
Sources credited in the image footer are Reuters, CNN, AP, Al Jazeera,
US Treasury (OFAC) and UN News. The build performs no network requests.

## How it works

- `main.ts` (Node 22, standard library only) copies the bundled
  `entry.png` to `/output/entry.png`. No network, randomness or
  timestamps: repeated runs write identical bytes.
- `news.json` holds all six stories, three additional stories, date and sources.
- `render_23nov.py` renders the PNG using Pillow 10.2.0 and system DejaVu
  fonts. It measures every line, fits headlines to at most two lines and
  summaries to at most three, and fails loudly on overflow — no words are
  truncated. Each story panel carries a simple drawn pictogram.
- `.makefun/owner.json` is not needed: the repository owner is the
  account's GitHub login.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
# out/entry.png — 1024x1024 PNG, 123,914 bytes
```

Rebuild the bundled image (Pillow 10.2.0 and DejaVu fonts required):

```sh
python3 render_23nov.py
```

Determinism check:

```sh
mkdir -p out1 out2
MAKEFUN_OUTPUT_DIR=out1 node main.ts
MAKEFUN_OUTPUT_DIR=out2 node main.ts
sha256sum out1/entry.png out2/entry.png   # identical hashes
```

## License

MIT — see `LICENSE`.
