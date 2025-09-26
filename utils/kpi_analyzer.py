import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from supabase import Client
import numpy as np

class KPIAnalyzer:
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    def process_sales_data(self, df: pd.DataFrame, user_id: str) -> bool:
        """Process and store sales data"""
        try:
            # Data cleaning and validation
            df = self._clean_sales_data(df)
            
            # Calculate KPIs
            kpi_data = self._calculate_kpis(df, user_id)
            
            # Store in database
            for record in kpi_data:
                result = self.supabase.table('kpi_data').insert(record).execute()
            
            return True
            
        except Exception as e:
            st.error(f"Error processing sales data: {e}")
            return False
    
    def _clean_sales_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize sales data"""
        # Standard cleaning operations
        df = df.dropna(subset=['date', 'sales_amount'])
        df['date'] = pd.to_datetime(df['date'])
        df['sales_amount'] = pd.to_numeric(df['sales_amount'], errors='coerce')
        
        return df
    
    def _calculate_kpis(self, df: pd.DataFrame, user_id: str) -> list:
        """Calculate KPIs from sales data"""
        kpi_records = []
        
        # Group by date for daily KPIs
        daily_data = df.groupby('date').agg({
            'sales_amount': 'sum',
            'transaction_id': 'count',
            'customer_id': 'nunique',
            'footfall': 'first',
            'returns': 'sum'
        }).reset_index()
        
        for _, row in daily_data.iterrows():
            record = {
                'user_id': user_id,
                'date': row['date'].date(),
                'conversion_rate': (row['transaction_id'] / row['footfall'] * 100) if row['footfall'] > 0 else 0,
                'avg_bill_value': row['sales_amount'] / row['transaction_id'] if row['transaction_id'] > 0 else 0,
                'footfall': row['footfall'],
                'actual_sales': row['sales_amount'],
                'return_rate': (row['returns'] / row['transaction_id'] * 100) if row['transaction_id'] > 0 else 0
            }
            kpi_records.append(record)
        
        return kpi_records
    
    def get_user_kpis(self, user_id: str) -> pd.DataFrame:
        """Retrieve user's KPI data"""
        try:
            result = self.supabase.table('kpi_data').select('*').eq('user_id', user_id).execute()
            return pd.DataFrame(result.data)
        except Exception as e:
            st.error(f"Error fetching KPI data: {e}")
            return pd.DataFrame()
    
    def display_kpi_dashboard(self, kpi_data: pd.DataFrame):
        """Display interactive KPI dashboard"""
        if kpi_data.empty:
            st.warning("No KPI data available")
            return
        
        # Convert date column
        kpi_data['date'] = pd.to_datetime(kpi_data['date'])
        
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_conversion = kpi_data['conversion_rate'].mean()
            st.metric(
                "Avg Conversion Rate", 
                f"{avg_conversion:.1f}%",
                delta=f"{avg_conversion - 10:.1f}%" if avg_conversion > 10 else None
            )
        
        with col2:
            avg_bill = kpi_data['avg_bill_value'].mean()
            st.metric(
                "Avg Bill Value", 
                f"₹{avg_bill:.0f}",
                delta=f"₹{avg_bill - 1500:.0f}" if avg_bill > 1500 else None
            )
        
        with col3:
            total_footfall = kpi_data['footfall'].sum()
            st.metric("Total Footfall", f"{total_footfall:,}")
        
        with col4:
            avg_return_rate = kpi_data['return_rate'].mean()
            st.metric(
                "Avg Return Rate", 
                f"{avg_return_rate:.1f}%",
                delta=f"{avg_return_rate - 5:.1f}%" if avg_return_rate < 5 else None
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Conversion Rate Trend
            fig_conversion = px.line(
                kpi_data, 
                x='date', 
                y='conversion_rate',
                title='Conversion Rate Trend',
                labels={'conversion_rate': 'Conversion Rate (%)', 'date': 'Date'}
            )
            st.plotly_chart(fig_conversion, use_container_width=True)
        
        with col2:
            # Average Bill Value Trend
            fig_bill = px.line(
                kpi_data, 
                x='date', 
                y='avg_bill_value',
                title='Average Bill Value Trend',
                labels={'avg_bill_value': 'Avg Bill Value (₹)', 'date': 'Date'}
            )
            st.plotly_chart(fig_bill, use_container_width=True)
        
        # Sales vs Target Analysis
        st.subheader("Sales Performance Analysis")
        
        # Add target achievement analysis
        kpi_data['target_achievement'] = (kpi_data['actual_sales'] / kpi_data.get('sales_target', kpi_data['actual_sales'])) * 100
        
        fig_target = px.bar(
            kpi_data, 
            x='date', 
            y='target_achievement',
            title='Daily Target Achievement %',
            labels={'target_achievement': 'Target Achievement (%)', 'date': 'Date'}
        )
        fig_target.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Target Line")
        st.plotly_chart(fig_target, use_container_width=True)
        
        # KPI Correlation Matrix
        st.subheader("KPI Correlation Analysis")
        
        numeric_columns = ['conversion_rate', 'avg_bill_value', 'footfall', 'return_rate']
        correlation_matrix = kpi_data[numeric_columns].corr()
        
        fig_corr = px.imshow(
            correlation_matrix,
            title='KPI Correlation Matrix',
            color_continuous_scale='RdBu',
            aspect="auto"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    
    def generate_insights(self, kpi_data: pd.DataFrame) -> dict:
        """Generate AI-powered insights from KPI data"""
        insights = {
            'performance_summary': '',
            'improvement_areas': [],
            'recommendations': []
        }
        
        if kpi_data.empty:
            return insights
        
        # Calculate key metrics
        avg_conversion = kpi_data['conversion_rate'].mean()
        avg_bill = kpi_data['avg_bill_value'].mean()
        avg_return_rate = kpi_data['return_rate'].mean()
        
        # Performance summary
        if avg_conversion > 15:
            conversion_status = "excellent"
        elif avg_conversion > 10:
            conversion_status = "good"
        else:
            conversion_status = "needs improvement"
        
        insights['performance_summary'] = f"Your conversion rate is {conversion_status} at {avg_conversion:.1f}%. Average bill value is ₹{avg_bill:.0f}."
        
        # Improvement areas
        if avg_conversion < 12:
            insights['improvement_areas'].append("Conversion rate is below industry average")
        if avg_bill < 1500:
            insights['improvement_areas'].append("Average bill value could be increased")
        if avg_return_rate > 8:
            insights['improvement_areas'].append("Return rate is higher than optimal")
        
        # Recommendations
        if avg_conversion < 12:
            insights['recommendations'].append("Focus on customer engagement and needs assessment training")
        if avg_bill < 1500:
            insights['recommendations'].append("Implement cross-selling and upselling strategies")
        if avg_return_rate > 8:
            insights['recommendations'].append("Review product quality and size guidance processes")
        
        return insights

    def export_kpi_report(self, kpi_data: pd.DataFrame, user_data: dict) -> str:
        """Generate downloadable KPI report"""
        if kpi_data.empty:
            return "No data available for report generation"
        
        # Calculate summary statistics
        summary_stats = {
            'avg_conversion_rate': kpi_data['conversion_rate'].mean(),
            'avg_bill_value': kpi_data['avg_bill_value'].mean(),
            'total_footfall': kpi_data['footfall'].sum(),
            'avg_return_rate': kpi_data['return_rate'].mean(),
            'total_sales': kpi_data['actual_sales'].sum()
        }
        
        insights = self.generate_insights(kpi_data)
        
        report = f"""
        # Max Fashion KPI Report
        
        **Manager:** {user_data['email']}
        **Store Location:** {user_data.get('store_location', 'Not specified')}
        **Report Period:** {kpi_data['date'].min()} to {kpi_data['date'].max()}
        
        ## Summary Statistics
        - Average Conversion Rate: {summary_stats['avg_conversion_rate']:.2f}%
        - Average Bill Value: ₹{summary_stats['avg_bill_value']:.2f}
        - Total Footfall: {summary_stats['total_footfall']:,}
        - Average Return Rate: {summary_stats['avg_return_rate']:.2f}%
        - Total Sales: ₹{summary_stats['total_sales']:,.2f}
        
        ## Performance Insights
        {insights['performance_summary']}
        
        ## Areas for Improvement
        {chr(10).join([f"- {area}" for area in insights['improvement_areas']])}
        
        ## Recommendations
        {chr(10).join([f"- {rec}" for rec in insights['recommendations']])}
        """
        
        return report