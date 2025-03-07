import streamlit as st
from db import Database
from pages import login_page, user_page, admin_page, change_password_page

# Initialize session state
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.session_state.username = None
        st.session_state.user_id = None
        st.session_state.password_change_required = False

# Main app
def main():
    # Initialize database
    db = Database()
    
    # Initialize session state
    init_session_state()
    
    # Display appropriate page based on user state
    if not st.session_state.logged_in:
        login_page(db)
    elif st.session_state.password_change_required:
        change_password_page(db)
    else:
        # Create sidebar for navigation
        st.sidebar.title(f"Welcome, {st.session_state.username}")
        
        if st.session_state.is_admin:
            page = st.sidebar.radio("Navigation", ["User Page", "Admin Page"])
            
            if page == "User Page":
                user_page()
            else:
                admin_page(db)
        else:
            user_page()

if __name__ == "__main__":
    main()