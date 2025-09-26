import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta

def create_performance_gauge(value: float, title: str, max_value: float = 100):
    """Create a performance gauge chart"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        delta = {'reference': max_value * 0.8},
        gauge = {
            'axis': {'range': [None, max_value]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, max_value * 0.5], 'color': "lightgray"},
                {'range': [max_value * 0.5, max_value * 0.8], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def create_training_progress_chart(training_data: pd.DataFrame):
    """Create training progress visualization"""
    if training_data.empty:
        return go.Figure()
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Accuracy Over Time', 'Communication Skills', 'Adaptability', 'Overall Progress'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Accuracy trend
    fig.add_trace(
        go.Scatter(x=training_data['date'], y=training_data['accuracy_score'], 
                  name='Accuracy', line=dict(color='blue')),
        row=1, col=1
    )
    
    # Communication trend
    fig.add_trace(
        go.Scatter(x=training_data['date'], y=training_data['communication_score'], 
                  name='Communication', line=dict(color='green')),
        row=1, col=2
    )
    
    # Adaptability trend
    fig.add_trace(
        go.Scatter(x=training_data['date'], y=training_data['adaptability_score'], 
                  name='Adaptability', line=dict(color='orange')),
        row=2, col=1
    )
    
    # Overall progress
    training_data['overall_score'] = training_data[['accuracy_score', 'communication_score', 'adaptability_score']].mean(axis=1)
    fig.add_trace(
        go.Scatter(x=training_data['date'], y=training_data['overall_score'], 
                  name='Overall', line=dict(color='red', width=3)),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False)
    return fig

def display_kpi_cards(kpi_data: dict):
    """Display KPI cards in a grid layout"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Conversion Rate",
            value=f"{kpi_data.get('conversion_rate', 0):.1f}%",
            delta=f"{kpi_data.get('conversion_delta', 0):+.1f}%"
        )
    
    with col2:
        st.metric(
            label="Avg Bill Value",
            value=f"₹{kpi_data.get('avg_bill_value', 0):,.0f}",
            delta=f"₹{kpi_data.get('bill_delta', 0):+,.0f}"
        )
    
    with col3:
        st.metric(
            label="Customer Footfall",
            value=f"{kpi_data.get('footfall', 0):,}",
            delta=f"{kpi_data.get('footfall_delta', 0):+,}"
        )
    
    with col4:
        st.metric(
            label="Sales Target Achievement",
            value=f"{kpi_data.get('target_achievement', 0):.0f}%",
            delta=f"{kpi_data.get('target_delta', 0):+.0f}%"
        )

def create_persona_performance_radar(performance_data: dict):
    """Create radar chart for persona-based performance"""
    categories = list(performance_data.keys())
    values = list(performance_data.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Performance'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )),
        showlegend=True,
        title="Performance by Customer Persona",
        height=400
    )
    
    return fig

def display_training_recommendations(user_performance: dict):
    """Display personalized training recommendations"""
    st.subheader("🎯 Personalized Training Recommendations")
    
    weak_areas = [area for area, score in user_performance.items() if score < 3.5]
    strong_areas = [area for area, score in user_performance.items() if score >= 4.0]
    
    if weak_areas:
        st.warning("**Focus Areas for Improvement:**")
        for area in weak_areas:
            st.write(f"• **{area.replace('_', ' ').title()}**: Consider additional practice scenarios")
    
    if strong_areas:
        st.success("**Your Strengths:**")
        for area in strong_areas:
            st.write(f"• **{area.replace('_', ' ').title()}**: Excellent performance! Consider mentoring others")
    
    # Suggested next steps
    st.info("**Suggested Next Steps:**")
    if len(weak_areas) > 2:
        st.write("• Focus on 1-2 key areas at a time for better results")
    if user_performance.get('overall_score', 0) > 4.0:
        st.write("• Ready for advanced scenarios and leadership training")
    else:
        st.write("• Continue with current difficulty level until consistent 4+ scores")