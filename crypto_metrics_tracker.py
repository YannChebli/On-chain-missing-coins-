import requests
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import time
from config import SANTIMENT_API_KEY, CRYPTOCURRENCIES, METRICS

class CryptocurrencyMetricsTracker:
    def __init__(self):
        self.api_key = SANTIMENT_API_KEY
        self.base_url = "https://api.santiment.net/graphql"
        self.headers = {
            "Authorization": f"Apikey {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Create data directory if it doesn't exist
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # Create subdirectories for each cryptocurrency
        for crypto in CRYPTOCURRENCIES.keys():
            crypto_dir = os.path.join(self.data_dir, crypto)
            if not os.path.exists(crypto_dir):
                os.makedirs(crypto_dir)
                for category in METRICS.keys():
                    category_dir = os.path.join(crypto_dir, category)
                    if not os.path.exists(category_dir):
                        os.makedirs(category_dir)

    def fetch_metric(self, crypto_slug, metric):
        query = """
        query($slug: String!, $metric: String!, $from: DateTime!, $to: DateTime!) {
            getMetric(metric: $metric) {
                timeseriesData(
                    slug: $slug
                    from: $from
                    to: $to
                    interval: "1d"
                ) {
                    datetime
                    value
                }
            }
        }
        """
        
        # Calculate date range (last 30 days)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=30)
        
        variables = {
            "slug": crypto_slug,
            "metric": metric,
            "from": from_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "to": to_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        max_retries = 3
        retry_delay = 10
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    json={"query": query, "variables": variables},
                    headers=self.headers
                )
                
                if response.status_code == 429:  # Rate limit exceeded
                    retry_after = int(response.headers.get('Retry-After', 60))
                    print(f"Rate limit exceeded. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                if "errors" in data:
                    error_message = data["errors"][0]["message"]
                    if "rate limit" in error_message.lower():
                        retry_after = 60  # Default wait time if not specified
                        print(f"Rate limit exceeded. Waiting {retry_after} seconds...")
                        time.sleep(retry_after)
                        continue
                    raise Exception(f"GraphQL Error: {error_message}")
                
                timeseries_data = data["data"]["getMetric"]["timeseriesData"]
                if not timeseries_data:
                    return None
                
                # Convert to DataFrame
                df = pd.DataFrame(timeseries_data)
                df['datetime'] = pd.to_datetime(df['datetime'])
                df.set_index('datetime', inplace=True)
                return df
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"Request failed, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise Exception(f"Failed to fetch data after {max_retries} attempts: {str(e)}")
        
        return None

    def save_metric_data(self, crypto, category, metric, data):
        if data is None:
            print(f"⚠️ No data available for {crypto} - {metric}")
            return False
            
        # Reset index to make datetime a column
        data_df = data.reset_index()
        
        # Convert timestamps to ISO format with timezone
        data_df['timestamp'] = data_df['datetime'].dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        # Create the data dictionary with metadata
        data_dict = {
            'metric': metric,
            'cryptocurrency': crypto,
            'category': category,
            'last_updated': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'data': [
                {
                    'timestamp': row['timestamp'],
                    'datetime': row['datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                    'value': row['value']
                }
                for _, row in data_df.iterrows()
            ]
        }
        
        # Save as JSON
        filename = os.path.join(self.data_dir, crypto, category, f"{metric}.json")
        with open(filename, 'w') as f:
            json.dump(data_dict, f, indent=4)
        print(f"✓ Saved data to {filename}")
        return True

    def track_all_metrics(self):
        successful = []
        failed = []
        
        for crypto, crypto_slug in CRYPTOCURRENCIES.items():
            print(f"\nProcessing metrics for {crypto}...")
            
            for category, metrics in METRICS.items():
                print(f"\nFetching {category} metrics...")
                
                for metric in metrics:
                    print(f"Processing {metric}...")
                    try:
                        df = self.fetch_metric(crypto_slug, metric)
                        if self.save_metric_data(crypto, category, metric, df):
                            successful.append(f"{crypto}/{category}/{metric}")
                        else:
                            failed.append(f"{crypto}/{category}/{metric}")
                    except Exception as e:
                        print(f"❌ Error processing {metric}: {str(e)}")
                        failed.append(f"{crypto}/{category}/{metric}")
                    
                    # Add a small delay between requests to avoid rate limits
                    time.sleep(1)
        
        return successful, failed

def main():
    print("Starting cryptocurrency metrics tracking...")
    tracker = CryptocurrencyMetricsTracker()
    successful, failed = tracker.track_all_metrics()
    
    print("\nSummary:")
    print(f"Successfully processed: {len(successful)} metrics")
    print(f"Failed to process: {len(failed)} metrics")
    
    if failed:
        print("\nFailed metrics:")
        for metric in failed:
            print(f"- {metric}")

if __name__ == "__main__":
    main() 