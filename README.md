<p align="center">
  <img src="assets/logo.svg" alt="Sl-analyzer logo" width="180" />
</p>

# Smart Shopping Analyzer

A lightweight shopping-list analysis tool for editing item prices, generating estimated price ranges, and comparing each entered price against those ranges.

## Features

- Editable shopping list
- Generated minimum and maximum price estimates
- Heuristic deal ratings and probability indicators
- CSV export

## Technology

Python · Streamlit · pandas

## Run Locally

Requirements: Python 3.

```bash
pip install streamlit pandas
streamlit run Sl-analyzer.py
```

## Notes

The minimum and maximum ranges are generated estimates, not verified retailer prices. Deal ratings and probability indicators are calculated from those generated ranges and should be treated as illustrative rather than market research.
