import bcrypt
from supabase import Client
import streamlit as st

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def authenticate_user(supabase: Client, email: str, password: str) -> dict:
    """Authenticate user credentials"""
    try:
        result = supabase.table('users').select('*').eq('email', email).execute()
        
        if result.data:
            user = result.data[0]
            if verify_password(password, user['password_hash']):
                return user
        return None
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return None

def register_user(supabase: Client, email: str, password: str, role: str, 
                  store_location: str = None, experience_level: int = 0) -> bool:
    """Register new user"""
    try:
        # Check if email exists
        existing = supabase.table('users').select('id').eq('email', email).execute()
        if existing.data:
            st.error("Email already registered")
            return False
        
        hashed_password = hash_password(password)
        
        supabase.table('users').insert({
            'email': email,
            'password_hash': hashed_password,
            'role': role,
            'store_location': store_location,
            'experience_level': experience_level
        }).execute()
        
        return True
    except Exception as e:
        st.error(f"Registration error: {e}")
        return False


def get_user_role(supabase: Client, user_id: str) -> str:
    """Get user role by ID"""
    try:
        result = supabase.table('users').select('role').eq('id', user_id).execute()
        return result.data[0]['role'] if result.data else None
    except Exception as e:
        st.error(f"Error fetching user role: {e}")
        return None