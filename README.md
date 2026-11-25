# Market Mood Index (MMI)

A Streamlit reimplementation of the [Market Mood Index](https://www.tickertape.in/market-mood-index) for Indian equities — a single fear/greed gauge built from FII flows, volatility, momentum and market breadth.

![Python](https://img.shields.io/badge/python-3.x-3776AB)
![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B)
![Plotly](https://img.shields.io/badge/Plotly-charts-3F4F75)

## Signals

| Component | Input | Method |
| --- | --- | --- |
| FII activity | NSE FII derivative stats (`fii_stats_<dd>-<Mon>-<yyyy>.xls`) | Index-futures buy minus sell, normalised |
| Volatility | India VIX history | 45-day rolling mean and standard deviation, normalised |
| Momentum | Nifty 50 daily closes | 30-day and 90-day EMA spread, normalised |
| Market breadth | NSE market-activity files (`MA<dd><mm><yy>.csv`) | Advances vs declines (Arms-index style) |

Each series is normalised to 0–100 with a 45-day rolling window and combined into the mood gauge. The exact methodology lives in `mmiIndex.py` (`methodology()`), so it is easy to swap weights or windows.

## Quickstart

```bash
git clone https://github.com/hirawatt/mmi.git
cd mmi
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run mmiIndex.py
```

The repository ships with historical CSVs under `data/`, so the dashboard renders without a live NSE connection.

## Data refresh

Two helpers fetch fresh data and are intentionally left commented out near the top of `mmiIndex.py`:

- `get_fii_activity(...)` — downloads FII statistics for each date in the index.
- `get_market_activity(...)` — downloads NSE market-activity files.

NSE moved and hardened these endpoints after the files were captured; expect to update the URLs, add request headers and handle rate limits if you re-enable them. `nsepyData.py` wraps `nsepy` for Nifty/India VIX history.

## Project structure

```
.
├── mmiIndex.py         # Streamlit dashboard + methodology
├── nsepyData.py        # nsepy wrapper for index history
├── scripts/            # Streamlit test helper
├── data/
│   ├── nifty50.csv
│   ├── indiavix.csv
│   ├── fii/            # Daily FII derivative stats
│   ├── mactivity/      # Daily market activity (advances/declines)
│   └── fii_activity.csv
└── requirements.txt
```

## Status

Research prototype. The committed dataset covers early 2022, the NSE downloaders are brittle, and there is no license file — add one before redistributing.

Not investment advice.

## Roadmap

- [x] Gauge charts
- [x] FII activity
- [x] Momentum
- [ ] Volatility and skew
- [ ] Market breadth weighting
- [ ] Price strength
- [ ] Gold demand
