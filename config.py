from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Santiment API Configuration
SANTIMENT_API_KEY = os.getenv("SANTIMENT_API_KEY")

# Available cryptocurrencies
CRYPTOCURRENCIES = {
    "BTC": "bitcoin",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "LTC": "litecoin"
}

# Metrics configuration with Santiment API metric names
METRICS = {
    "holder_metrics": [
        "mean_age"
    ],
    "network_metrics": [
        "active_addresses_24h",
        "transaction_volume",
        "circulation"
    ],
    "market_metrics": [
        "price_usd",
        "volume_usd",
        "marketcap_usd",
        "mvrv_usd"
    ],
    "development_metrics": [
        "dev_activity",
        "github_activity"
    ]
} 