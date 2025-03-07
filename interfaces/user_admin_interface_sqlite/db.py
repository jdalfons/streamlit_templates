import sqlite3
import hashlib
import os
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Pydantic models for data validation
class User(BaseModel):
    id: Optional[int] = None
    username: str
    password: str
    is_admin: bool = False
    created_at: Optional[datetime] = None
    password_change_required: bool = False

class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool
    created_at: datetime
    password_change_required: bool

class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False
    password_change_required: bool = True

# Database class
class Database:
    def __init__(self, db_path="security.db"):
        self.db_path = db_path
        self._init_database()
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def _init_database(self):
        # Check if database file exists
        db_exists = os.path.exists(self.db_path)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if not db_exists:
            # Execute init.sql script if it exists
            sql_path = "init.sql"
            if os.path.exists(sql_path):
                with open(sql_path, 'r') as sql_file:
                    sql_script = sql_file.read()
                    cursor.executescript(sql_script)
        
        # Check if users table exists (in case init.sql didn't create it)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            # Create users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                password_change_required BOOLEAN NOT NULL DEFAULT 0
            )
            ''')
        
        # Create default users
        self._create_default_users(cursor)
        
        conn.commit()
        conn.close()
    
    def _create_default_users(self, cursor):
        # Check if admin exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            admin = User(
                username="admin",
                password=self._hash_password("adminpass"),
                is_admin=True,
                password_change_required=True
            )
            cursor.execute(
                "INSERT INTO users (username, password, is_admin, password_change_required) VALUES (?, ?, ?, ?)",
                (admin.username, admin.password, admin.is_admin, admin.password_change_required)
            )
        
        # Check if regular user exists
        cursor.execute("SELECT * FROM users WHERE username = 'user'")
        if not cursor.fetchone():
            user = User(
                username="user",
                password=self._hash_password("userpass"),
                is_admin=False,
                password_change_required=True
            )
            cursor.execute(
                "INSERT INTO users (username, password, is_admin, password_change_required) VALUES (?, ?, ?, ?)",
                (user.username, user.password, user.is_admin, user.password_change_required)
            )
    
    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, username: str, password: str) -> Optional[UserResponse]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        hashed_password = self._hash_password(password)
        cursor.execute(
            "SELECT id, username, is_admin, created_at, password_change_required FROM users WHERE username = ? AND password = ?",
            (username, hashed_password)
        )
        user_data = cursor.fetchone()
        
        conn.close()
        
        if user_data:
            return UserResponse(
                id=user_data[0],
                username=user_data[1],
                is_admin=bool(user_data[2]),
                created_at=datetime.fromisoformat(user_data[3]) if user_data[3] else datetime.now(),
                password_change_required=bool(user_data[4])
            )
        return None
    
    def get_all_users(self) -> List[UserResponse]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, is_admin, created_at, password_change_required FROM users")
        users_data = cursor.fetchall()
        
        conn.close()
        
        return [
            UserResponse(
                id=user[0],
                username=user[1],
                is_admin=bool(user[2]),
                created_at=datetime.fromisoformat(user[3]) if user[3] else datetime.now(),
                password_change_required=bool(user[4])
            )
            for user in users_data
        ]
    
    def create_user(self, user: UserCreate) -> Optional[UserResponse]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        hashed_password = self._hash_password(user.password)
        
        try:
            cursor.execute(
                "INSERT INTO users (username, password, is_admin, password_change_required) VALUES (?, ?, ?, ?)",
                (user.username, hashed_password, user.is_admin, user.password_change_required)
            )
            user_id = cursor.lastrowid
            conn.commit()
            
            cursor.execute(
                "SELECT id, username, is_admin, created_at, password_change_required FROM users WHERE id = ?",
                (user_id,)
            )
            new_user = cursor.fetchone()
            
            conn.close()
            
            if new_user:
                return UserResponse(
                    id=new_user[0],
                    username=new_user[1],
                    is_admin=bool(new_user[2]),
                    created_at=datetime.fromisoformat(new_user[3]) if new_user[3] else datetime.now(),
                    password_change_required=bool(new_user[4])
                )
        except sqlite3.IntegrityError:
            conn.close()
            return None
        
        return None
    
    def change_password(self, user_id: int, new_password: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        hashed_password = self._hash_password(new_password)
        
        try:
            cursor.execute(
                "UPDATE users SET password = ?, password_change_required = 0 WHERE id = ?",
                (hashed_password, user_id)
            )
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except:
            conn.close()
            return False