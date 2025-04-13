# Cryptocurrency Metrics Tracker

This script tracks various cryptocurrency metrics using the Santiment API for Bitcoin (BTC), Ripple (XRP), Dogecoin (DOGE), and Litecoin (LTC).

## Features

The script tracks the following metrics:

### Holder Metrics
- Mean Dollar Invested Age
- Mean Age
- Percent of Total Supply on Exchanges

### Network Metrics
- Active Addresses (24h)
- Network Growth
- Transaction Volume
- Circulation

### Market Metrics
- Price (USD)
- Volume (USD)
- Market Cap (USD)
- MVRV Ratio

### Development Metrics
- Development Activity
- GitHub Activity

## Installation

1. Clone this repository

2. Install dependencies:
```bash
python3 -m pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your Santiment API key:
```
SANTIMENT_API_KEY=your_api_key_here
```

## Usage

Run the script:
```bash
python3 crypto_metrics_tracker.py
```

The script will:
- Fetch metrics for the last 30 days
- Generate plots for each metric
- Save the plots in the `plots` directory
- Handle API rate limits automatically

## Configuration

You can modify the following in `config.py`:
- API key (stored in `.env` file)
- Available cryptocurrencies
- Metrics to track

## Output

The script generates:
- Time series data for each metric
- Visual plots saved as PNG files in the `plots` directory
- Each plot shows the metric's value over time for the specified period

## Notes

- The script uses the Santiment API free tier
- The script includes rate limit handling and automatic retries
- Some metrics might not be available for all cryptocurrencies
- The script creates a `plots` directory to store the generated visualizations
- Always use `python3` command instead of `python` on macOS 

The visualizations will be saved in the following structure:
```
plots/
├── BTC/
│   ├── holder_metrics/
│   ├── network_metrics/
│   ├── market_metrics/
│   └── development_metrics/
├── XRP/
├── DOGE/
└── LTC/
```