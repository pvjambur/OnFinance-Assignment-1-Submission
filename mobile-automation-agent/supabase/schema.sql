-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    pin_hash VARCHAR(255) NOT NULL,  -- Hashed 4-digit PIN
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Credentials table (encrypted)
CREATE TABLE credentials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    app_name VARCHAR(255) NOT NULL,
    app_package VARCHAR(255),
    email_encrypted TEXT NOT NULL,  -- Encrypted with user's PIN
    password_encrypted TEXT NOT NULL,  -- Encrypted with user's PIN
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, app_name)
);

-- Task history
CREATE TABLE task_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    command TEXT NOT NULL,
    intent JSONB,
    app_name VARCHAR(255),
    status VARCHAR(50),  -- pending, in_progress, completed, failed
    steps JSONB DEFAULT '[]',
    result TEXT,
    error TEXT,
    duration_seconds INTEGER,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Session state (for multi-step tasks)
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    task_id UUID REFERENCES task_history(id) ON DELETE CASCADE,
    state JSONB NOT NULL,  -- Current task state
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Device sessions (track BrowserStack sessions)
CREATE TABLE device_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    browserstack_session_id VARCHAR(255),
    device_name VARCHAR(255),
    platform_version VARCHAR(50),
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    duration_minutes INTEGER
);

-- Indexes for performance
CREATE INDEX idx_credentials_user_id ON credentials(user_id);
CREATE INDEX idx_task_history_user_id ON task_history(user_id);
CREATE INDEX idx_task_history_status ON task_history(status);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_active ON sessions(is_active);

-- Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- Policies (users can only access their own data)
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can view own credentials" ON credentials
    FOR ALL USING (user_id = auth.uid());

CREATE POLICY "Users can view own task history" ON task_history
    FOR ALL USING (user_id = auth.uid());

CREATE POLICY "Users can view own sessions" ON sessions
    FOR ALL USING (user_id = auth.uid());
