"""
Database Handler for Supabase Integration
Handles all database operations for the Max Fashion Training System
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import streamlit as st
import json

load_dotenv()

class DatabaseHandler:
    """Handles all Supabase database operations"""
    
    def __init__(self):
        """Initialize Supabase client"""
        try:
            self.url = os.getenv("SUPABASE_URL")
            self.key = os.getenv("SUPABASE_KEY")
            
            if not self.url or not self.key:
                st.error("Supabase credentials not found. Please check your .env file")
                self.client = None
            else:
                self.client: Client = create_client(self.url, self.key)
        except Exception as e:
            st.error(f"Failed to initialize Supabase client: {str(e)}")
            self.client = None
    
    # User Management
    def create_user(self, email: str, password: str, role: str, metadata: Dict = None) -> Dict:
        """Create a new user"""
        try:
            # Create auth user
            auth_response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": metadata or {}
                }
            })
            
            if auth_response.user:
                # Create user profile
                profile_data = {
                    "id": auth_response.user.id,
                    "email": email,
                    "role": role,
                    "created_at": datetime.now().isoformat(),
                    "metadata": json.dumps(metadata) if metadata else None
                }
                
                self.client.table("user_profiles").insert(profile_data).execute()
                
                return {"success": True, "user_id": auth_response.user.id}
            
            return {"success": False, "error": "User creation failed"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def authenticate_user(self, email: str, password: str) -> Dict:
        """Authenticate a user"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                # Get user profile
                profile = self.client.table("user_profiles").select("*").eq("id", response.user.id).single().execute()
                
                return {
                    "success": True,
                    "user_id": response.user.id,
                    "email": response.user.email,
                    "role": profile.data.get("role") if profile.data else "user",
                    "session": response.session
                }
            
            return {"success": False, "error": "Authentication failed"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Training Scenarios
    def get_training_scenarios(self, persona: str = None, difficulty: str = None) -> List[Dict]:
        """Get training scenarios based on filters"""
        try:
            query = self.client.table("training_scenarios").select("*")
            
            if persona:
                query = query.eq("persona", persona)
            if difficulty:
                query = query.eq("difficulty", difficulty)
            
            response = query.execute()
            return response.data if response.data else []
            
        except Exception as e:
            st.error(f"Error fetching scenarios: {str(e)}")
            return []
    
    def save_training_session(self, user_id: str, scenario_id: str, response: str, scores: Dict) -> bool:
        """Save a training session result"""
        try:
            session_data = {
                "user_id": user_id,
                "scenario_id": scenario_id,
                "response": response,
                "scores": json.dumps(scores),
                "total_score": sum(scores.values()) / len(scores),
                "completed_at": datetime.now().isoformat()
            }
            
            self.client.table("training_sessions").insert(session_data).execute()
            return True
            
        except Exception as e:
            st.error(f"Error saving training session: {str(e)}")
            return False
    
    # KPI Management
    def upload_sales_data(self, data: List[Dict]) -> bool:
        """Upload sales data for KPI analysis"""
        try:
            # Process and validate data
            processed_data = []
            for record in data:
                processed_record = {
                    "date": record.get("date"),
                    "sales_amount": float(record.get("sales", 0)),
                    "customer_id": record.get("customer_id"),
                    "product_category": record.get("product_category"),
                    "store_id": record.get("store_id"),
                    "uploaded_at": datetime.now().isoformat()
                }
                processed_data.append(processed_record)
            
            # Batch insert
            self.client.table("sales_data").insert(processed_data).execute()
            return True
            
        except Exception as e:
            st.error(f"Error uploading sales data: {str(e)}")
            return False
    
    def get_kpi_metrics(self, user_id: str = None, date_range: tuple = None) -> Dict:
        """Get KPI metrics for dashboard"""
        try:
            metrics = {}
            
            # Get training metrics
            query = self.client.table("training_sessions").select("*")
            if user_id:
                query = query.eq("user_id", user_id)
            
            sessions = query.execute().data
            
            if sessions:
                metrics["total_sessions"] = len(sessions)
                metrics["avg_score"] = sum(s.get("total_score", 0) for s in sessions) / len(sessions)
                metrics["completion_rate"] = len([s for s in sessions if s.get("total_score", 0) >= 70]) / len(sessions) * 100
            
            # Get sales metrics
            sales_query = self.client.table("sales_data").select("*")
            if date_range and len(date_range) == 2:
                sales_query = sales_query.gte("date", date_range[0].isoformat())
                sales_query = sales_query.lte("date", date_range[1].isoformat())
            
            sales = sales_query.execute().data
            
            if sales:
                metrics["total_sales"] = sum(s.get("sales_amount", 0) for s in sales)
                metrics["transaction_count"] = len(sales)
                metrics["avg_transaction"] = metrics["total_sales"] / metrics["transaction_count"]
            
            return metrics
            
        except Exception as e:
            st.error(f"Error fetching KPI metrics: {str(e)}")
            return {}
    
    # Performance Analytics
    def get_user_performance(self, user_id: str) -> Dict:
        """Get detailed performance analytics for a user"""
        try:
            # Get all training sessions
            sessions = self.client.table("training_sessions").select("*").eq("user_id", user_id).execute().data
            
            if not sessions:
                return {}
            
            # Calculate performance metrics
            performance = {
                "total_sessions": len(sessions),
                "avg_score": sum(s.get("total_score", 0) for s in sessions) / len(sessions),
                "best_score": max(s.get("total_score", 0) for s in sessions),
                "improvement_rate": 0,
                "scores_by_category": {},
                "sessions_by_persona": {},
                "recent_sessions": sorted(sessions, key=lambda x: x.get("completed_at", ""), reverse=True)[:5]
            }
            
            # Calculate improvement rate (compare first 25% to last 25% of sessions)
            if len(sessions) >= 4:
                quarter = len(sessions) // 4
                early_avg = sum(s.get("total_score", 0) for s in sessions[:quarter]) / quarter
                recent_avg = sum(s.get("total_score", 0) for s in sessions[-quarter:]) / quarter
                performance["improvement_rate"] = ((recent_avg - early_avg) / early_avg) * 100
            
            # Aggregate scores by category
            for session in sessions:
                scores = json.loads(session.get("scores", "{}"))
                for category, score in scores.items():
                    if category not in performance["scores_by_category"]:
                        performance["scores_by_category"][category] = []
                    performance["scores_by_category"][category].append(score)
            
            # Calculate averages for each category
            for category, scores in performance["scores_by_category"].items():
                performance["scores_by_category"][category] = sum(scores) / len(scores)
            
            return performance
            
        except Exception as e:
            st.error(f"Error fetching user performance: {str(e)}")
            return {}
    
    # Leaderboard
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top performers"""
        try:
            # Get all users with their average scores
            sessions = self.client.table("training_sessions").select("user_id, total_score").execute().data
            
            # Aggregate by user
            user_scores = {}
            for session in sessions:
                user_id = session.get("user_id")
                if user_id not in user_scores:
                    user_scores[user_id] = []
                user_scores[user_id].append(session.get("total_score", 0))
            
            # Calculate averages and sort
            leaderboard = []
            for user_id, scores in user_scores.items():
                avg_score = sum(scores) / len(scores) if scores else 0
                leaderboard.append({"user_id": user_id, "avg_score": avg_score})
            
            leaderboard_sorted = sorted(leaderboard, key=lambda x: x["avg_score"], reverse=True)
            
            return leaderboard_sorted[:limit]
        except Exception as e:
            st.error(f"Error fetching leaderboard: {str(e)}")
            return []
