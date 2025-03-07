import streamlit as st
from db import Database, UserCreate

def login_page(db: Database):
    st.title("Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user = db.authenticate_user(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = user.username
            st.session_state.user_id = user.id
            st.session_state.is_admin = user.is_admin
            st.session_state.password_change_required = user.password_change_required
            st.success(f"Welcome {user.username}!")
            st.rerun()
        else:
            st.error("Invalid username or password")

def change_password_page(db: Database):
    st.title("Change Password")
    st.write("You need to change your password before continuing.")
    
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Change Password"):
        if not new_password:
            st.error("Password cannot be empty")
        elif new_password != confirm_password:
            st.error("Passwords do not match")
        else:
            success = db.change_password(st.session_state.user_id, new_password)
            if success:
                st.session_state.password_change_required = False
                st.success("Password changed successfully!")
                st.rerun()
            else:
                st.error("Failed to change password")

def user_page():
    st.title(f"User Dashboard - Welcome, {st.session_state.username}!")
    st.write("This is the user page. All authenticated users can see this page.")
    
    # Empty user page as requested
    st.write("user")
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_id = None
        st.session_state.is_admin = False
        st.session_state.password_change_required = False
        st.rerun()

def admin_page(db: Database):
    st.title(f"Admin Dashboard - Welcome, {st.session_state.username}!")
    st.write("This is the admin page. Only admin users can see this page.")
    
    # Empty admin page as requested
    st.write("admin")
    
    # Add user management functionality for admin
    with st.expander("User Management"):
        st.subheader("Create New User")
        new_username = st.text_input("New Username")
        new_password = st.text_input("Initial Password", type="password")
        is_admin = st.checkbox("Admin Role")
        password_change = st.checkbox("Require Password Change on First Login", value=True)
        
        if st.button("Create User"):
            if new_username and new_password:
                new_user = UserCreate(
                    username=new_username,
                    password=new_password,
                    is_admin=is_admin,
                    password_change_required=password_change
                )
                result = db.create_user(new_user)
                if result:
                    st.success(f"User {new_username} created successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to create user. Username may already exist.")
            else:
                st.warning("Username and password are required")
        
        st.subheader("All Users")
        users = db.get_all_users()
        for user in users:
            role = "Admin" if user.is_admin else "User"
            pw_status = "Password change required" if user.password_change_required else "Password set"
            st.write(f"ID: {user.id}, Username: {user.username}, Role: {role}, {pw_status}, Created: {user.created_at}")