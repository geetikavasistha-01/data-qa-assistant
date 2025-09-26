import streamlit as st
from utils.auth import authenticate_user, get_user_role
from utils.database import init_supabase
from utils.training_engine import TrainingEngine
from utils.kpi_analyzer import KPIAnalyzer
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Max Fashion Training System",
    page_icon="👔",
    layout="wide"
)

def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None

    # Initialize database
    supabase = init_supabase()
    
    if not st.session_state.authenticated:
        show_login_page(supabase)
    else:
        show_main_dashboard(supabase)

def show_login_page(supabase):
    st.title("🛍️ Max Fashion Training System")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login")
        
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                user_data = authenticate_user(supabase, email, password)
                if user_data:
                    st.session_state.authenticated = True
                    st.session_state.user_data = user_data
                    st.rerun()
                else:
                    st.error("Invalid credentials")

def show_main_dashboard(supabase):
    user_role = st.session_state.user_data['role']
    
    st.sidebar.title(f"Welcome, {st.session_state.user_data['email']}")
    st.sidebar.write(f"Role: {user_role.replace('_', ' ').title()}")
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user_data = None
        st.rerun()
    
    # Navigation
    pages = {
        "Dashboard": show_dashboard,
        "Training Center": show_training_center,
        "KPI Analysis": show_kpi_analysis,
        "Performance Reports": show_performance_reports
    }
    
    if user_role == 'admin':
        pages["User Management"] = show_user_management
    
    selected_page = st.sidebar.selectbox("Navigation", list(pages.keys()))
    pages[selected_page](supabase)

def show_dashboard(supabase):
    st.title("📊 Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Training Sessions", "23", "+5")
    with col2:
        st.metric("Average Score", "4.2/5", "+0.3")
    with col3:
        st.metric("Conversion Rate", "12.5%", "+2.1%")
    with col4:
        st.metric("Sales Target Achievement", "98%", "+8%")
    
    # Recent training activity
    st.subheader("Recent Training Activity")
    # Add charts and recent activity here

def show_training_center(supabase):
    st.title("🎯 Training Center")
    
    training_engine = TrainingEngine(supabase)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Select Training Mode")
        
        # Persona selection
        personas = training_engine.get_personas()
        selected_persona = st.selectbox("Choose Customer Persona", 
                                      [p['name'] for p in personas])
        
        # Difficulty level
        difficulty = st.selectbox("Difficulty Level", 
                                ["Easy", "Medium", "Hard", "Expert"])
        
        if st.button("Start Training Session"):
            st.session_state.training_active = True
            st.session_state.current_scenario = training_engine.generate_scenario(
                selected_persona, difficulty
            )
    
    with col2:
        if st.session_state.get('training_active', False):
            show_training_scenario(training_engine)

def show_training_scenario(training_engine):
    scenario = st.session_state.current_scenario
    
    st.subheader(f"Scenario: {scenario['persona']} - {scenario['difficulty']}")
    st.write(scenario['description'])
    
    # Customer dialogue
    st.write("**Customer says:**")
    st.info(scenario['customer_dialogue'])
    
    # Response input
    user_response = st.text_area("Your response as a sales manager:", 
                               height=100)
    
    if st.button("Submit Response"):
        if user_response:
            # Evaluate response
            evaluation = training_engine.evaluate_response(
                scenario, user_response
            )
            
            st.subheader("Evaluation Results")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Accuracy", f"{evaluation['accuracy']}/5")
            with col2:
                st.metric("Application", f"{evaluation['application']}/5")
            with col3:
                st.metric("Communication", f"{evaluation['communication']}/5")
            with col4:
                st.metric("Adaptability", f"{evaluation['adaptability']}/5")
            
            st.write("**Feedback:**")
            st.success(evaluation['feedback'])
            
            st.write("**Improvement Suggestions:**")
            st.info(evaluation['suggestions'])
            
            if st.button("Next Scenario"):
                st.session_state.current_scenario = training_engine.generate_scenario(
                    scenario['persona'], scenario['difficulty']
                )
                st.rerun()

def show_kpi_analysis(supabase):
    st.title("📈 KPI Analysis")
    
    analyzer = KPIAnalyzer(supabase)
    
    # Upload CSV data
    st.subheader("Upload Sales Data")
    uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("Data Preview:")
        st.dataframe(df.head())
        
        if st.button("Process Data"):
            analyzer.process_sales_data(df, st.session_state.user_data['id'])
            st.success("Data processed successfully!")
    
    # KPI Dashboard
    st.subheader("KPI Dashboard")
    kpi_data = analyzer.get_user_kpis(st.session_state.user_data['id'])
    
    if not kpi_data.empty:
        analyzer.display_kpi_dashboard(kpi_data)

def show_performance_reports(supabase):
    st.title("📋 Performance Reports")
    # Implementation for performance reports

def show_user_management(supabase):
    st.title("👥 User Management")
    # Implementation for user management (admin only)

if __name__ == "__main__":
    main()