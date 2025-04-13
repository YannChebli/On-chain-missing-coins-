import json
import pandas as pd
import os
from datetime import datetime

def format_data_for_ai():
    """Format the processed data into a structure optimized for AI analysis."""
    
    # Load processed data for all cryptocurrencies
    cryptos = ["BTC", "XRP", "DOGE", "LTC"]
    ai_ready_data = {
        "metadata": {
            "generated_at": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "cryptocurrencies": cryptos,
            "time_period": "30 days",
            "data_source": "Santiment API"
        },
        "market_analysis": {},
        "network_health": {},
        "development_activity": {},
        "correlations": {}
    }
    
    all_crypto_data = {}
    
    # Load data for each cryptocurrency
    for crypto in cryptos:
        with open(f'processed_data/{crypto}/{crypto}_processed.json', 'r') as f:
            data = json.load(f)
            all_crypto_data[crypto] = pd.DataFrame(data['data'])
    
    # Market Analysis
    for crypto in cryptos:
        df = all_crypto_data[crypto]
        ai_ready_data["market_analysis"][crypto] = {
            "price_metrics": {
                "current_price": float(df.iloc[-1]['price_usd']),
                "price_change_24h": float(df.iloc[-1]['price_change_24h']),
                "price_change_7d": float(df.iloc[-1]['price_change_7d']),
                "price_volatility": float(df.iloc[-1]['price_volatility']),
                "price_trend": [float(price) for price in df['price_usd'].tail(7)]
            },
            "volume_metrics": {
                "current_volume": float(df.iloc[-1]['volume_usd']),
                "volume_change_24h": float(df.iloc[-1]['volume_change_24h']),
                "volume_trend": [float(vol) for vol in df['volume_usd'].tail(7)]
            }
        }
    
    # Network Health
    for crypto in cryptos:
        df = all_crypto_data[crypto]
        ai_ready_data["network_health"][crypto] = {
            "active_addresses": {
                "current": float(df.iloc[-1]['active_addresses_24h']),
                "trend": [float(addr) for addr in df['active_addresses_24h'].tail(7)]
            },
            "transaction_metrics": {
                "volume": float(df.iloc[-1]['transaction_volume']),
                "avg_per_address": float(df.iloc[-1]['avg_transaction_per_address'])
            },
            "circulation": float(df.iloc[-1]['circulation'])
        }
    
    # Development Activity
    for crypto in cryptos:
        df = all_crypto_data[crypto]
        ai_ready_data["development_activity"][crypto] = {
            "github_activity": {
                "current": float(df.iloc[-1]['github_activity']),
                "trend": [float(act) for act in df['github_activity'].tail(7)]
            },
            "dev_metrics": {
                "current_activity": float(df.iloc[-1]['dev_activity']),
                "momentum": float(df.iloc[-1]['dev_activity_momentum']),
                "trend": [float(act) for act in df['dev_activity'].tail(7)]
            }
        }
    
    # Calculate correlations
    for crypto in cryptos:
        df = all_crypto_data[crypto]
        correlations = {
            "price_volume_correlation": float(df['price_usd'].corr(df['volume_usd'])),
            "price_dev_correlation": float(df['price_usd'].corr(df['dev_activity'])),
            "price_network_correlation": float(df['price_usd'].corr(df['active_addresses_24h']))
        }
        ai_ready_data["correlations"][crypto] = correlations
    
    # Save the AI-ready data
    output_file = "ai_ready_data.json"
    with open(output_file, 'w') as f:
        json.dump(ai_ready_data, f, indent=4)
    print(f"✓ Saved AI-ready data to {output_file}")
    
    return ai_ready_data

if __name__ == "__main__":
    format_data_for_ai() 