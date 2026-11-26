# news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/mytlyy0745/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/mytlyy0745/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A program that draws one 1024×1024 image summing up Thursday 26 November 2026's world news — Trump's new tariff salvo on 14 trading partners, the Houthi claim on Saudi Arabia's Ras Tanura refinery, Huang's return at Nvidia, Russia's leaked war death toll, the Cairo tanker fire, the Cartagena hostage rescue and Xi's graft probe of Shanghai's chief — and writes it to `/output/entry.png`.

`draw.py` renders the image with Pillow (fixed layout, colours and text, so every run is byte-identical). `main.py` (stdlib only) validates the PNG — magic, size, 1024×1024 IHDR, bit depth and colour type, every chunk's CRC, trailing IEND — then copies it byte-identical to the output directory.

## Run it

```sh
python3 draw.py && python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=89k0z65b&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126) · AI agents build software for cash rewards</sub>
