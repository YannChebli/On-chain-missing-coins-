import json
import pandas as pd
import os
from datetime import datetime
import numpy as np

class CryptoDataPreprocessor:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.cryptocurrencies = ["BTC", "XRP", "DOGE", "LTC"]
        self.categories = ["holder_metrics", "network_metrics", "market_metrics", "development_metrics"]
        
    def load_metric_data(self, crypto, category, metric):
        """Load data from a JSON file and convert to DataFrame."""
        file_path = os.path.join(self.data_dir, crypto, category, f"{metric}.json")
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Extract the data points
        df = pd.DataFrame(data['data'])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        df.rename(columns={'value': metric}, inplace=True)
        return df
    
    def process_cryptocurrency(self, crypto):
        """Process all metrics for a single cryptocurrency."""
        print(f"\nProcessing {crypto} data...")
        dfs = []
        
        # Load all metrics for the cryptocurrency
        for category in self.categories:
            category_dir = os.path.join(self.data_dir, crypto, category)
            metrics = [f.split('.')[0] for f in os.listdir(category_dir) if f.endswith('.json')]
            
            for metric in metrics:
                try:
                    df = self.load_metric_data(crypto, category, metric)
                    dfs.append(df)
                    print(f"✓ Loaded {metric}")
                except Exception as e:
                    print(f"⚠️ Error loading {metric}: {str(e)}")
        
        # Merge all metrics on datetime index
        if dfs:
            combined_df = pd.concat(dfs, axis=1)
            
            # Handle missing values
            combined_df = self.handle_missing_values(combined_df)
            
            # Add derived features
            combined_df = self.add_derived_features(combined_df, crypto)
            
            # Save processed dataset
            self.save_processed_data(combined_df, crypto)
            
            return combined_df
        return None
    
    def handle_missing_values(self, df):
        """Handle missing values in the dataset."""
        # Create a copy to avoid modifying the original
        df = df.copy()
        
        # Convert timestamp columns to datetime if they exist
        timestamp_cols = df.select_dtypes(include=['object']).columns
        for col in timestamp_cols:
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass
        
        # Get numeric columns only
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Handle missing values for numeric columns
        for col in numeric_cols:
            # Forward fill missing values up to 1 day
            df[col] = df[col].ffill(limit=1)
            
            # Backward fill remaining missing values up to 1 day
            df[col] = df[col].bfill(limit=1)
            
            # For any remaining missing values, use column median
            df[col] = df[col].fillna(df[col].median())
        
        return df
    
    def add_derived_features(self, df, crypto):
        """Add derived features useful for AI analysis."""
        # Price changes
        if 'price_usd' in df.columns:
            df['price_change_24h'] = df['price_usd'].pct_change(1)
            df['price_change_7d'] = df['price_usd'].pct_change(7)
            df['price_volatility'] = df['price_change_24h'].rolling(window=7).std()
        
        # Volume-based features
        if 'volume_usd' in df.columns:
            df['volume_change_24h'] = df['volume_usd'].pct_change(1)
            df['volume_ma_7d'] = df['volume_usd'].rolling(window=7).mean()
        
        # Network health indicators
        if 'active_addresses_24h' in df.columns and 'transaction_volume' in df.columns:
            df['avg_transaction_per_address'] = df['transaction_volume'] / df['active_addresses_24h']
        
        # Development activity momentum
        if 'dev_activity' in df.columns:
            df['dev_activity_ma_7d'] = df['dev_activity'].rolling(window=7).mean()
            df['dev_activity_momentum'] = df['dev_activity'] / df['dev_activity_ma_7d']
        
        return df
    
    def save_processed_data(self, df, crypto):
        """Save the processed dataset in multiple formats."""
        # Create processed data directory
        output_dir = os.path.join('processed_data', crypto)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save as CSV
        csv_path = os.path.join(output_dir, f"{crypto}_processed.csv")
        df.to_csv(csv_path)
        print(f"✓ Saved CSV to {csv_path}")
        
        # Save as JSON with metadata
        json_path = os.path.join(output_dir, f"{crypto}_processed.json")
        
        # Convert DataFrame to JSON-serializable format
        df_dict = df.reset_index()
        df_dict['datetime'] = df_dict['datetime'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        records = df_dict.to_dict(orient='records')
        
        json_data = {
            'metadata': {
                'generated_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                'cryptocurrencies': self.cryptocurrencies,
                'time_period': '30 days',
                'data_source': 'Santiment API'
            },
            'market_analysis': {
                crypto: {
                    'price_metrics': {
                        'current_price': df['price_usd'].iloc[-1],
                        'price_change_24h': df['price_change_24h'].iloc[-1],
                        'price_change_7d': df['price_change_7d'].iloc[-1],
                        'price_volatility': df['price_volatility'].iloc[-1],
                        'price_trend': df['price_change_24h'].rolling(window=7).mean().tolist()
                    },
                    'volume_metrics': {
                        'current_volume': df['volume_usd'].iloc[-1],
                        'volume_change_24h': df['volume_change_24h'].iloc[-1],
                        'volume_trend': df['volume_change_24h'].rolling(window=7).mean().tolist()
                    }
                }
            },
            'network_health': {
                crypto: {
                    'active_addresses': {
            'cryptocurrency': crypto,
            'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'features': list(df.columns),
            'data_points': len(df),
            'date_range': {
                'start': df.index.min().strftime('%Y-%m-%d'),
                'end': df.index.max().strftime('%Y-%m-%d')
            },
            'data': records
        }
        
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=4)
        print(f"✓ Saved JSON to {json_path}")
        
        # Save feature statistics (numeric columns only)
        numeric_df = df.select_dtypes(include=[np.number])
        stats_path = os.path.join(output_dir, f"{crypto}_statistics.json")
        stats = {
            'mean': numeric_df.mean().to_dict(),
            'std': numeric_df.std().to_dict(),
            'min': numeric_df.min().to_dict(),
            'max': numeric_df.max().to_dict(),
            'median': numeric_df.median().to_dict()
        }
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=4)
        print(f"✓ Saved statistics to {stats_path}")
    
    def process_all_cryptocurrencies(self):
        """Process all cryptocurrencies."""
        processed_data = {}
        
        for crypto in self.cryptocurrencies:
            processed_data[crypto] = self.process_cryptocurrency(crypto)
        
        return processed_data

def main():
    print("Starting data preprocessing...")
    preprocessor = CryptoDataPreprocessor()
    processed_data = preprocessor.process_all_cryptocurrencies()
    print("\nData preprocessing completed!")

if __name__ == "__main__":
    main() 