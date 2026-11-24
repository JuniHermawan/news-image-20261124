# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/JuniHermawan/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/JuniHermawan/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

One image that sums up Tuesday 24 November 2026's world news: Jensen Huang returns as Nvidia CEO as shares surge 31%, COP31 climate talks collapse with no deal, Ukraine claims it sank a Russian warship off Libya, the world court finds Myanmar guilty of genocide against the Rohingya, 12,000 people are evacuated from a Manchester concert after a gas alert, and Iranian singer Parastoo Ahmadi is sentenced to 74 lashes for a concert without a hijab. A newspaper front page drawn for make.fun's "Sum up 24 November's world news in one image" bounty, $100 in USDC.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 -S main.py
```

`main.py` (Python 3.13 standard library only) validates `entry.png` — PNG magic, IHDR dimensions at most 1024x1024, size at most 1 MiB, terminating IEND chunk, SHA-256 digest — then copies it byte-for-byte to the output directory and re-verifies the written copy, so both runs produce identical bytes.

---

<sub>Entered on [make.fun](https://make.fun/?ref=yspfqw66&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
