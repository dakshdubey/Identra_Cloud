-- Identra Cloud Database Schema
-- Database: evobiomat_test

-- Table: user_files
-- Stores metadata for files uploaded by users to their secure cloud storage.

CREATE TABLE IF NOT EXISTS user_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,       -- The Biometric User ID (e.g., 'agent_007')
    filename VARCHAR(255) NOT NULL,      -- Original filename (sanitized)
    size VARCHAR(50) NOT NULL,           -- Formatted size string (e.g., '2.5 MB')
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP, -- Timestamp of upload
    local_path VARCHAR(255) NOT NULL     -- Path to the file on the local server storage
);

-- Indexes for faster lookup by user
CREATE INDEX idx_user_id ON user_files(user_id);

-- Table: activity_logs
-- Tracks user actions for security auditing.
CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255),
    action VARCHAR(255),        -- e.g., 'LOGIN', 'UPLOAD', 'DELETE'
    details VARCHAR(255),       -- e.g., 'Filename: secret.pdf'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
