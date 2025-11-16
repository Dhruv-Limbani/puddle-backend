-- ========================================
-- Puddle Synthetic Data Population Script
-- Generated with bcrypt password hashing
-- ========================================

-- Clean existing data (optional - comment out if you want to keep existing data)
-- TRUNCATE TABLE chat_messages, chats, dataset_columns, datasets, ai_agents, buyers, vendors, users CASCADE;

-- ========================================
-- 1. USERS
-- ========================================
-- Password for all users: 'password123'

INSERT INTO users (email, password_hash, role, full_name, is_active) VALUES ('admin@puddle.com', '$2b$12$00nC7Ko2w5tvS0lb1GxDKOZHONcEy8ftaRyiXCJ5doQ.yjbP7XSkC', 'admin', 'Admin User', TRUE);
INSERT INTO users (email, password_hash, role, full_name, is_active) VALUES ('vendor1@datamart.com', '$2b$12$00nC7Ko2w5tvS0lb1GxDKOZHONcEy8ftaRyiXCJ5doQ.yjbP7XSkC', 'vendor', 'Alice Johnson', TRUE);
INSERT INTO users (email, password_hash, role, full_name, is_active) VALUES ('vendor2@insights.io', '$2b$12$00nC7Ko2w5tvS0lb1GxDKOZHONcEy8ftaRyiXCJ5doQ.yjbP7XSkC', 'vendor', 'Bob Smith', TRUE);
INSERT INTO users (email, password_hash, role, full_name, is_active) VALUES ('vendor3@analytics.net', '$2b$12$00nC7Ko2w5tvS0lb1GxDKOZHONcEy8ftaRyiXCJ5doQ.yjbP7XSkC', 'vendor', 'Carol White', TRUE);
INSERT INTO users (email, password_hash, role, full_name, is_active) VALUES ('buyer1@research.edu', '$2b$12$00nC7Ko2w5tvS0lb1GxDKOZHONcEy8ftaRyiXCJ5doQ.yjbP7XSkC', 'buyer', 'David Brown', TRUE);
INSERT INTO users (email, password_hash, role, full_name, is_active) VALUES ('buyer2@startup.io', '$2b$12$00nC7Ko2w5tvS0lb1GxDKOZHONcEy8ftaRyiXCJ5doQ.yjbP7XSkC', 'buyer', 'Emma Davis', TRUE);
INSERT INTO users (email, password_hash, role, full_name, is_active) VALUES ('buyer3@enterprise.com', '$2b$12$00nC7Ko2w5tvS0lb1GxDKOZHONcEy8ftaRyiXCJ5doQ.yjbP7XSkC', 'buyer', 'Frank Miller', TRUE);

-- ========================================
-- 2. VENDORS
-- ========================================

INSERT INTO vendors (user_id, name, industry_focus, description, contact_email, contact_phone, website_url, country, region, city, organization_type, founded_year) VALUES ((SELECT id FROM users WHERE email = 'vendor1@datamart.com'), 'DataMart Solutions', 'Finance', 'Leading provider of financial market data and analytics', 'contact@datamart.com', '+1-555-0101', 'https://datamart.com', 'United States', 'California', 'San Francisco', 'Corporation', 2018);
INSERT INTO vendors (user_id, name, industry_focus, description, contact_email, contact_phone, website_url, country, region, city, organization_type, founded_year) VALUES ((SELECT id FROM users WHERE email = 'vendor2@insights.io'), 'Insights Analytics', 'Healthcare', 'Healthcare data intelligence and predictive analytics platform', 'hello@insights.io', '+1-555-0102', 'https://insights.io', 'United States', 'Massachusetts', 'Boston', 'Startup', 2020);
INSERT INTO vendors (user_id, name, industry_focus, description, contact_email, contact_phone, website_url, country, region, city, organization_type, founded_year) VALUES ((SELECT id FROM users WHERE email = 'vendor3@analytics.net'), 'Global Analytics Corp', 'Retail', 'E-commerce and retail consumer behavior datasets', 'info@analytics.net', '+44-20-5550103', 'https://analytics.net', 'United Kingdom', 'England', 'London', 'Corporation', 2015);

-- ========================================
-- 3. BUYERS
-- ========================================

INSERT INTO buyers (user_id, name, organization, contact_email, contact_phone, country, region, city, organization_type, job_title, industry, use_case_focus) VALUES ((SELECT id FROM users WHERE email = 'buyer1@research.edu'), 'David Brown', 'University Research Lab', 'd.brown@research.edu', '+1-555-0201', 'United States', 'New York', 'New York', 'Academic', 'Research Scientist', 'Education', 'Machine learning research on financial time series');
INSERT INTO buyers (user_id, name, organization, contact_email, contact_phone, country, region, city, organization_type, job_title, industry, use_case_focus) VALUES ((SELECT id FROM users WHERE email = 'buyer2@startup.io'), 'Emma Davis', 'TechStart Inc', 'emma@startup.io', '+1-555-0202', 'United States', 'California', 'Palo Alto', 'Startup', 'Data Scientist', 'Technology', 'Building recommendation systems for e-commerce');
INSERT INTO buyers (user_id, name, organization, contact_email, contact_phone, country, region, city, organization_type, job_title, industry, use_case_focus) VALUES ((SELECT id FROM users WHERE email = 'buyer3@enterprise.com'), 'Frank Miller', 'Enterprise Analytics Ltd', 'f.miller@enterprise.com', '+1-555-0203', 'Canada', 'Ontario', 'Toronto', 'Enterprise', 'Chief Data Officer', 'Consulting', 'Healthcare outcomes analysis and predictive modeling');

-- ========================================
-- 4. AI AGENTS
-- ========================================

INSERT INTO ai_agents (vendor_id, name, description, model_used, config, active) VALUES ((SELECT id FROM vendors WHERE user_id = (SELECT id FROM users WHERE email = 'vendor1@datamart.com')), 'FinanceBot', 'AI assistant for financial data queries and analysis', 'gemini-embedding-001', '{"temperature": 0.7, "max_tokens": 2000}'::jsonb, TRUE);
INSERT INTO ai_agents (vendor_id, name, description, model_used, config, active) VALUES ((SELECT id FROM vendors WHERE user_id = (SELECT id FROM users WHERE email = 'vendor2@insights.io')), 'HealthInsight AI', 'Healthcare data exploration and insights assistant', 'gemini-embedding-001', '{"temperature": 0.5, "max_tokens": 1500}'::jsonb, TRUE);
INSERT INTO ai_agents (vendor_id, name, description, model_used, config, active) VALUES ((SELECT id FROM vendors WHERE user_id = (SELECT id FROM users WHERE email = 'vendor3@analytics.net')), 'RetailGenie', 'E-commerce and retail analytics chatbot', 'gemini-embedding-001', '{"temperature": 0.8, "max_tokens": 2500}'::jsonb, TRUE);

-- ========================================
-- 5. DATASETS
-- ========================================

INSERT INTO datasets (vendor_id, title, status, visibility, description, domain, dataset_type, granularity, pricing_model, license, topics, entities, temporal_coverage, geographic_coverage, embedding_input) VALUES ((SELECT id FROM vendors WHERE user_id = (SELECT id FROM users WHERE email = 'vendor1@datamart.com')), 'Global Stock Market Data 2020-2024', 'active', 'public', 'Comprehensive stock market data covering major exchanges worldwide', 'Finance', 'Time-series', 'Daily', 'Subscription', 'Commercial Use Allowed', '["stocks", "markets", "trading"]'::jsonb, '["companies", "exchanges", "indices"]'::jsonb, '{"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"}'::jsonb, '{"countries": ["US", "UK", "JP", "DE"], "regions": ["North America", "Europe", "Asia"]}'::jsonb, 'Global Stock Market Data 2020-2024 Comprehensive stock market data covering major exchanges worldwide Finance');

-- Columns for: Global Stock Market Data 2020-2024
INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) VALUES ((SELECT id FROM datasets WHERE title = 'Global Stock Market Data 2020-2024'), 'ticker', 'Stock ticker symbol', 'VARCHAR(10)', '["AAPL", "GOOGL", "MSFT"]'::jsonb);
INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) VALUES ((SELECT id FROM datasets WHERE title = 'Global Stock Market Data 2020-2024'), 'date', 'Trading date', 'DATE', '["2024-01-15", "2024-01-16"]'::jsonb);
INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) VALUES ((SELECT id FROM datasets WHERE title = 'Global Stock Market Data 2020-2024'), 'open', 'Opening price', 'DECIMAL(10,2)', '[150.25, 151.3]'::jsonb);
INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) VALUES ((SELECT id FROM datasets WHERE title = 'Global Stock Market Data 2020-2024'), 'close', 'Closing price', 'DECIMAL(10,2)', '[152.1, 153.45]'::jsonb);
INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) VALUES ((SELECT id FROM datasets WHERE title = 'Global Stock Market Data 2020-2024'), 'volume', 'Trading volume', 'BIGINT', '[45000000, 42000000]'::jsonb);

INSERT INTO datasets (vendor_id, title, status, visibility, description, domain, dataset_type, granularity, pricing_model, license, topics, entities, temporal_coverage, geographic_coverage, embedding_input) VALUES ((SELECT id FROM vendors WHERE user_id = (SELECT id FROM users WHERE email = 'vendor2@insights.io')), 'Patient Outcomes Dataset 2023', 'active', 'public', 'Anonymized patient treatment outcomes and recovery metrics', 'Healthcare', 'Clinical', 'Patient-level', 'One-time Purchase', 'Research Use Only', '["healthcare", "outcomes", "treatment"]'::jsonb, '["patients", "treatments", "diagnoses"]'::jsonb, '{"start_date": "2023-01-01", "end_date": "2023-12-31", "frequency": "Event-based"}'::jsonb, '{"countries": ["US"], "regions": ["North America"]}'::jsonb, 'Patient Outcomes Dataset 2023 Anonymized patient treatment outcomes and recovery metrics Healthcare');

-- Columns for: Patient Outcomes Dataset 2023
INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) VALUES ((SELECT id FROM datasets WHERE title = 'Patient Outcomes Dataset 2023'), 'patient_id', 'Anonymized patient identifier', 'UUID', '["a1b2c3d4", "e5f6g7h8"]'::jsonb);
INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) VALUES ((SELECT id FROM datasets WHERE title = 'Patient Outcomes Dataset 2023'), 'diagnosis_code', 'ICD-10 diagnosis code', 'VARCHAR(10)', '["E11.9", "I10"]'::jsonb);
INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) VALUES ((SELECT id FROM datasets WHERE title = 'Patient Outcomes Dataset 2023'), 'treatment_type', 'Type of treatment administered', 'VARCHAR(100)', '["Medication", "Surgery"]'::jsonb);
INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) VALUES ((SELECT id FROM datasets WHERE title = 'Patient Outcomes Dataset 2023'), 'outcome_score', 'Recovery outcome score (0-100)', 'INTEGER', '[85, 92]'::jsonb);

INSERT INTO datasets (vendor_id, title, status, visibility, description, domain, dataset_type, granularity, pricing_model, license, topics, entities, temporal_coverage, geographic_coverage, embedding_input) VALUES ((SELECT id FROM vendors WHERE user_id = (SELECT id FROM users WHERE email = 'vendor3@analytics.net')), 'E-commerce Transactions 2024', 'active', 'public', 'Global e-commerce transaction data with product and customer insights', 'Retail', 'Transactional', 'Transaction-level', 'Usage-based', 'Commercial Use Allowed', '["e-commerce", "retail", "consumer behavior"]'::jsonb, '["transactions", "products", "customers"]'::jsonb, '{"start_date": "2024-01-01", "end_date": "2024-12-31", "frequency": "Real-time"}'::jsonb, '{"countries": ["US", "UK", "CA", "AU"], "regions": ["North America", "Europe", "Oceania"]}'::jsonb, 'E-commerce Transactions 2024 Global e-commerce transaction data with product and customer insights Retail');

-- Columns for: E-commerce Transactions 2024
INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) VALUES ((SELECT id FROM datasets WHERE title = 'E-commerce Transactions 2024'), 'transaction_id', 'Unique transaction identifier', 'UUID', '["tx_001", "tx_002"]'::jsonb);
INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) VALUES ((SELECT id FROM datasets WHERE title = 'E-commerce Transactions 2024'), 'customer_id', 'Customer identifier', 'UUID', '["cust_123", "cust_456"]'::jsonb);
INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) VALUES ((SELECT id FROM datasets WHERE title = 'E-commerce Transactions 2024'), 'product_id', 'Product SKU', 'VARCHAR(50)', '["SKU-001", "SKU-002"]'::jsonb);
INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) VALUES ((SELECT id FROM datasets WHERE title = 'E-commerce Transactions 2024'), 'amount', 'Transaction amount in USD', 'DECIMAL(10,2)', '[49.99, 129.99]'::jsonb);
INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) VALUES ((SELECT id FROM datasets WHERE title = 'E-commerce Transactions 2024'), 'timestamp', 'Transaction timestamp', 'TIMESTAMP', '["2024-01-15 10:30:00", "2024-01-15 11:45:00"]'::jsonb);

INSERT INTO datasets (vendor_id, title, status, visibility, description, domain, dataset_type, granularity, pricing_model, license, topics, entities, temporal_coverage, geographic_coverage, embedding_input) VALUES ((SELECT id FROM vendors WHERE user_id = (SELECT id FROM users WHERE email = 'vendor1@datamart.com')), 'Cryptocurrency Market Data', 'active', 'public', 'Real-time and historical cryptocurrency trading data', 'Finance', 'Time-series', 'Minute-level', 'Subscription', 'Commercial Use Allowed', '["cryptocurrency", "blockchain", "trading"]'::jsonb, '["coins", "exchanges", "wallets"]'::jsonb, '{"start_date": "2023-01-01", "end_date": "2024-12-31", "frequency": "Minute"}'::jsonb, '{"countries": ["Global"], "regions": ["Worldwide"]}'::jsonb, 'Cryptocurrency Market Data Real-time and historical cryptocurrency trading data Finance');

-- Columns for: Cryptocurrency Market Data
INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) VALUES ((SELECT id FROM datasets WHERE title = 'Cryptocurrency Market Data'), 'coin_symbol', 'Cryptocurrency symbol', 'VARCHAR(10)', '["BTC", "ETH", "SOL"]'::jsonb);
INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) VALUES ((SELECT id FROM datasets WHERE title = 'Cryptocurrency Market Data'), 'timestamp', 'Price timestamp', 'TIMESTAMP', '["2024-01-15 10:00:00"]'::jsonb);
INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) VALUES ((SELECT id FROM datasets WHERE title = 'Cryptocurrency Market Data'), 'price_usd', 'Price in USD', 'DECIMAL(18,8)', '[45000.5, 3200.75]'::jsonb);
INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) VALUES ((SELECT id FROM datasets WHERE title = 'Cryptocurrency Market Data'), 'volume_24h', '24-hour trading volume', 'DECIMAL(20,2)', '[25000000000.0]'::jsonb);


-- ========================================
-- DONE
-- ========================================
-- All synthetic data inserted successfully!
-- You can now log in with any user using password: 'password123'
