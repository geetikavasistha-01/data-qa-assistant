import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

class DataProcessor:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    
    def clean_sales_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize sales data"""
        # Make a copy to avoid modifying original
        df_clean = df.copy()
        
        # Standard column name mapping
        column_mapping = {
            'Date': 'date',
            'Sales': 'sales_amount',
            'Transaction_ID': 'transaction_id',
            'Customer_ID': 'customer_id',
            'Product_ID': 'product_id',
            'Quantity': 'quantity',
            'Price': 'unit_price'
        }
        
        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in df_clean.columns:
                df_clean = df_clean.rename(columns={old_name: new_name})
        
        # Data type conversions
        if 'date' in df_clean.columns:
            df_clean['date'] = pd.to_datetime(df_clean['date'], errors='coerce')
        
        numeric_columns = ['sales_amount', 'quantity', 'unit_price']
        for col in numeric_columns:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Remove rows with critical missing data
        critical_columns = ['date', 'sales_amount']
        for col in critical_columns:
            if col in df_clean.columns:
                df_clean = df_clean.dropna(subset=[col])
        
        # Calculate derived columns
        if 'sales_amount' not in df_clean.columns and 'quantity' in df_clean.columns and 'unit_price' in df_clean.columns:
            df_clean['sales_amount'] = df_clean['quantity'] * df_clean['unit_price']
        
        return df_clean
    
    def calculate_advanced_kpis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate advanced KPIs from sales data"""
        kpi_df = df.copy()
        
        # Group by date for daily calculations
        daily_stats = df.groupby('date').agg({
            'sales_amount': ['sum', 'mean', 'count'],
            'customer_id': 'nunique',
            'product_id': 'nunique',
            'quantity': 'sum'
        }).reset_index()
        
        # Flatten column names
        daily_stats.columns = ['date', 'total_sales', 'avg_transaction_value', 'transaction_count', 
                              'unique_customers', 'unique_products', 'total_quantity']
        
        # Calculate KPIs
        daily_stats['revenue_per_customer'] = daily_stats['total_sales'] / daily_stats['unique_customers']
        daily_stats['items_per_transaction'] = daily_stats['total_quantity'] / daily_stats['transaction_count']
        daily_stats['product_diversity_ratio'] = daily_stats['unique_products'] / daily_stats['transaction_count']
        
        # Add trend analysis
        daily_stats['sales_growth_rate'] = daily_stats['total_sales'].pct_change()
        daily_stats['customer_growth_rate'] = daily_stats['unique_customers'].pct_change()
        
        return daily_stats
    
    def detect_sales_patterns(self, df: pd.DataFrame) -> dict:
        """Detect patterns in sales data"""
        patterns = {}
        
        if 'date' in df.columns:
            df['day_of_week'] = df['date'].dt.day_name()
            df['hour'] = df['date'].dt.hour
            df['month'] = df['date'].dt.month
            
            # Day of week patterns
            dow_sales = df.groupby('day_of_week')['sales_amount'].sum().sort_values(ascending=False)
            patterns['best_sales_day'] = dow_sales.index[0]
            patterns['worst_sales_day'] = dow_sales.index[-1]
            
            # Hourly patterns (if time data available)
            if df['hour'].nunique() > 1:
                hourly_sales = df.groupby('hour')['sales_amount'].sum()
                patterns['peak_sales_hour'] = hourly_sales.idxmax()
                patterns['lowest_sales_hour'] = hourly_sales.idxmin()
            
            # Monthly patterns
            monthly_sales = df.groupby('month')['sales_amount'].sum()
            patterns['best_sales_month'] = monthly_sales.idxmax()
            patterns['worst_sales_month'] = monthly_sales.idxmin()
        
        # Product patterns
        if 'product_id' in df.columns:
            product_sales = df.groupby('product_id')['sales_amount'].sum().sort_values(ascending=False)
            patterns['top_selling_product'] = product_sales.index[0]
            patterns['least_selling_product'] = product_sales.index[-1]
        
        return patterns
    
    def generate_data_quality_report(self, df: pd.DataFrame) -> dict:
        """Generate data quality assessment"""
        report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_data': {},
            'data_types': {},
            'duplicates': 0,
            'quality_score': 0
        }
        
        # Missing data analysis
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            missing_percent = (missing_count / len(df)) * 100
            report['missing_data'][col] = {
                'count': missing_count,
                'percentage': missing_percent
            }
        
        # Data type analysis
        for col in df.columns:
            report['data_types'][col] = str(df[col].dtype)
        
        # Duplicate analysis
        report['duplicates'] = df.duplicated().sum()
        
        # Calculate quality score (0-100)
        quality_factors = []
        
        # Factor 1: Missing data (lower missing = higher quality)
        avg_missing_percent = sum([v['percentage'] for v in report['missing_data'].values()]) / len(report['missing_data'])
        missing_score = max(0, 100 - avg_missing_percent * 2)  # Penalty for missing data
        quality_factors.append(missing_score)
        
        # Factor 2: Duplicates (lower duplicates = higher quality)
        duplicate_percent = (report['duplicates'] / len(df)) * 100
        duplicate_score = max(0, 100 - duplicate_percent * 5)  # Heavy penalty for duplicates
        quality_factors.append(duplicate_score)
        
        # Factor 3: Data consistency (simplified check)
        consistency_score = 85  # Default baseline
        quality_factors.append(consistency_score)
        
        report['quality_score'] = sum(quality_factors) / len(quality_factors)
        
        return report

    def vectorize_scenarios(self, scenarios: list) -> np.ndarray:
        """Vectorize training scenarios for similarity matching"""
        scenario_texts = []
        for scenario in scenarios:
            text = f"{scenario.get('description', '')} {scenario.get('customer_dialogue', '')} {scenario.get('challenge', '')}"
            scenario_texts.append(text)
        
        if scenario_texts:
            vectors = self.vectorizer.fit_transform(scenario_texts)
            return vectors.toarray()
        else:
            return np.array([])
    
    def find_similar_scenarios(self, query_scenario: str, scenario_vectors: np.ndarray, scenarios: list, top_k: int = 3) -> list:
        """Find similar scenarios using cosine similarity"""
        if len(scenario_vectors) == 0:
            return []
        
        query_vector = self.vectorizer.transform([query_scenario]).toarray()
        similarities = cosine_similarity(query_vector, scenario_vectors)[0]
        
        # Get top-k most similar scenarios
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        similar_scenarios = [scenarios[i] for i in top_indices if similarities[i] > 0.1]  # Threshold for relevance
        
        return similar_scenarios