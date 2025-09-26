-- Enable UUID extension for UUID support
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. USERS TABLE
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    role VARCHAR NOT NULL CHECK (role IN ('store_manager', 'regional_manager', 'trainer', 'admin')),
    store_location UUID REFERENCES stores(id),
    experience_level INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. STORES TABLE
CREATE TABLE IF NOT EXISTS stores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    store_name VARCHAR NOT NULL,
    location VARCHAR NOT NULL,
    region VARCHAR,
    manager_id UUID REFERENCES users(id),
    store_size VARCHAR CHECK (store_size IN ('small', 'medium', 'large')),
    target_metrics JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);


-- 3. PERSONAS TABLE
CREATE TABLE personas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR UNIQUE NOT NULL,
    description TEXT,
    profile JSONB,
    scenarios JSONB,
    difficulty_mapping JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert example personas
INSERT INTO personas (name, description, profile, scenarios, difficulty_mapping) VALUES
('Bargain Hunter', 
 'Price-focused customer seeking best deals',
 '{"age": 32, "occupation": "working professional", "behavior": "price-focused, resists upselling", "pain_points": ["budget", "price comparison"]}'::jsonb,
 '["Discount requests", "Competitor price comparison"]'::jsonb,
 '{"Easy": "Basic price objections", "Medium": "Price matching", "Hard": "Competitive negotiation"}'::jsonb),
('Overwhelmed Parent',
 'Parent shopping under time constraints',
 '{"age": 40, "occupation": "parent", "behavior": "time pressured, practical", "pain_points": ["time", "multiple needs"]}'::jsonb,
 '["Quick purchases", "Durability concerns"]'::jsonb,
 '{"Easy": "Quick assistance", "Medium": "Multi-tasking", "Hard": "Crisis handling"}'::jsonb),
('Trend-Seeking Influencer',
 'Fashion conscious young customer',
 '{"age": 22, "occupation": "student", "behavior": "trend focused, social media active", "pain_points": ["style", "budget"]}'::jsonb,
 '["Trendy advice", "Exclusive items"]'::jsonb,
 '{"Easy": "Basic trend advice", "Medium": "Personalization", "Hard": "High maintenance"}'::jsonb);

-- 4. TRAINING_SCENARIOS TABLE
CREATE TABLE IF NOT EXISTS training_scenarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    persona_id UUID REFERENCES personas(id) ON DELETE CASCADE,
    scenario_title VARCHAR NOT NULL,
    scenario_description TEXT NOT NULL,
    difficulty_level VARCHAR NOT NULL CHECK (LOWER(difficulty_level) IN ('easy', 'medium', 'hard', 'expert')),
    kpi_focus TEXT,
    scenario_data JSONB NOT NULL,
    expected_response_guidelines JSONB,
    evaluation_criteria JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. TRAINING_SESSIONS TABLE
 CREATE TABLE IF NOT EXISTS training_sessions(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    persona_type VARCHAR NOT NULL,
    difficulty_level VARCHAR NOT NULL,
    scenario_data JSONB,
    responses JSONB,
    scores JSONB,
    completion_time INTEGER,
    session_status VARCHAR DEFAULT 'active' CHECK (session_status IN ('active', 'completed', 'abandoned')),
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6. TRAINING_INTERACTIONS TABLE
CREATE TABLE IF NOT EXISTS  training_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES training_sessions(id) ON DELETE CASCADE,
    scenario_id UUID REFERENCES training_scenarios(id),
    question_text TEXT,
    user_response TEXT,
    ai_evaluation JSONB,
    feedback TEXT,
    interaction_order INTEGER DEFAULT 1,
    response_time INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. TRAINING_TRANSCRIPTS TABLE
CREATE TABLE IF NOT EXISTS training_transcripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES training_sessions(id) ON DELETE CASCADE,
    full_transcript JSONB,
    summary TEXT,
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 8. KPI_DATA TABLE
CREATE TABLE IF NOT EXISTS  kpi_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    store_id UUID REFERENCES stores(id),
    date DATE NOT NULL,
    conversion_rate DECIMAL(5,2),
    avg_bill_value DECIMAL(10,2),
    footfall INTEGER,
    sales_target DECIMAL(12,2),
    actual_sales DECIMAL(12,2),
    return_rate DECIMAL(5,2),
    customer_satisfaction DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, store_id, date)
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_training_scenarios_persona ON training_scenarios(persona_id);

-- RLS example enabling
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy for users to access their own data
CREATE POLICY users_own_data ON users FOR ALL USING (auth.uid()::text = id::text);

-- Simple trigger to update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Confirmation of setup
SELECT '🎉 Max Fashion training database created successfully!' AS message;
