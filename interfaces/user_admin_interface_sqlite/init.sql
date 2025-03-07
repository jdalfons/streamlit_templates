-- Initialize database schema
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    password_change_required BOOLEAN NOT NULL DEFAULT 0
);

-- Create default users with hashed passwords
-- Use pre-hashed passwords
