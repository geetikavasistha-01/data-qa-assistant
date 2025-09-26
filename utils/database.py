from supabase import create_client, Client
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

@st.cache_resource
def init_supabase() -> Client:
    """Initialize Supabase client"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        st.error("Supabase credentials not found in environment variables")
        return None
    
    return create_client(url, key)

def insert_training_session(supabase: Client, user_id: str, session_data: dict) -> bool:
    """Insert training session data"""
    try:
        result = supabase.table('training_sessions').insert({
            'user_id': user_id,
            'persona_type': session_data['persona'],
            'difficulty_level': session_data['difficulty'],
            'scenario_data': session_data['scenario'],
            'responses': session_data['responses'],
            'scores': session_data['scores'],
            'completion_time': session_data.get('completion_time', 0)
        }).execute()
        
        return True
    except Exception as e:
        st.error(f"Error saving training session: {e}")
        return False

def get_user_training_history(supabase: Client, user_id: str) -> list:
    """Get user's training history"""
    try:
        result = supabase.table('training_sessions').select('*').eq('user_id', user_id).execute()
        return result.data
    except Exception as e:
        st.error(f"Error fetching training history: {e}")
        return []

def insert_kpi_data(supabase: Client, kpi_data: dict) -> bool:
    """Insert KPI data"""
    try:
        result = supabase.table('kpi_data').insert(kpi_data).execute()
        return True
    except Exception as e:
        st.error(f"Error saving KPI data: {e}")
        return False