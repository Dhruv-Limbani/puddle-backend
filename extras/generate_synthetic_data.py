#!/usr/bin/env python3
"""
Generate synthetic data SQL script for Puddle database.
Uses bcrypt for password hashing (same as backend).
Outputs a SQL file ready to run against PostgreSQL.
"""

import sys
from passlib.context import CryptContext
import json

# Initialize bcrypt context (same as backend)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password using bcrypt (same as backend)."""
    if not isinstance(password, str):
        password = str(password)
    password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.hash(password)


def generate_sql():
    """Generate SQL INSERT statements with synthetic data."""
    
    sql_lines = [
        "-- ========================================",
        "-- Puddle Synthetic Data Population Script",
        "-- Generated with bcrypt password hashing",
        "-- ========================================",
        "",
        "-- Clean existing data (optional - comment out if you want to keep existing data)",
        "-- TRUNCATE TABLE chat_messages, chats, dataset_columns, datasets, ai_agents, buyers, vendors, users CASCADE;",
        "",
        "-- ========================================",
        "-- 1. USERS",
        "-- ========================================",
        "-- Password for all users: 'password123'",
        "",
    ]
    
    # Hash the common password once
    common_password_hash = hash_password("password123")
    
    # Users data
    users = [
        # Admins
        {
            "email": "admin@puddle.com",
            "role": "admin",
            "full_name": "Admin User",
            "hash": common_password_hash
        },
        # Vendors
        {
            "email": "vendor1@datamart.com",
            "role": "vendor",
            "full_name": "Alice Johnson",
            "hash": common_password_hash
        },
        {
            "email": "vendor2@insights.io",
            "role": "vendor",
            "full_name": "Bob Smith",
            "hash": common_password_hash
        },
        {
            "email": "vendor3@analytics.net",
            "role": "vendor",
            "full_name": "Carol White",
            "hash": common_password_hash
        },
        # Buyers
        {
            "email": "buyer1@research.edu",
            "role": "buyer",
            "full_name": "David Brown",
            "hash": common_password_hash
        },
        {
            "email": "buyer2@startup.io",
            "role": "buyer",
            "full_name": "Emma Davis",
            "hash": common_password_hash
        },
        {
            "email": "buyer3@enterprise.com",
            "role": "buyer",
            "full_name": "Frank Miller",
            "hash": common_password_hash
        },
    ]
    
    for user in users:
        sql_lines.append(
            f"INSERT INTO users (email, password_hash, role, full_name, is_active) "
            f"VALUES ('{user['email']}', '{user['hash']}', '{user['role']}', '{user['full_name']}', TRUE);"
        )
    
    sql_lines.extend([
        "",
        "-- ========================================",
        "-- 2. VENDORS",
        "-- ========================================",
        "",
    ])
    
    vendors = [
        {
            "email": "vendor1@datamart.com",
            "name": "DataMart Solutions",
            "industry_focus": "Finance",
            "description": "Leading provider of financial market data and analytics",
            "contact_email": "contact@datamart.com",
            "contact_phone": "+1-555-0101",
            "website_url": "https://datamart.com",
            "country": "United States",
            "region": "California",
            "city": "San Francisco",
            "organization_type": "Corporation",
            "founded_year": 2018
        },
        {
            "email": "vendor2@insights.io",
            "name": "Insights Analytics",
            "industry_focus": "Healthcare",
            "description": "Healthcare data intelligence and predictive analytics platform",
            "contact_email": "hello@insights.io",
            "contact_phone": "+1-555-0102",
            "website_url": "https://insights.io",
            "country": "United States",
            "region": "Massachusetts",
            "city": "Boston",
            "organization_type": "Startup",
            "founded_year": 2020
        },
        {
            "email": "vendor3@analytics.net",
            "name": "Global Analytics Corp",
            "industry_focus": "Retail",
            "description": "E-commerce and retail consumer behavior datasets",
            "contact_email": "info@analytics.net",
            "contact_phone": "+44-20-5550103",
            "website_url": "https://analytics.net",
            "country": "United Kingdom",
            "region": "England",
            "city": "London",
            "organization_type": "Corporation",
            "founded_year": 2015
        },
    ]
    
    for vendor in vendors:
        sql_lines.append(
            f"INSERT INTO vendors (user_id, name, industry_focus, description, contact_email, contact_phone, "
            f"website_url, country, region, city, organization_type, founded_year) "
            f"VALUES ("
            f"(SELECT id FROM users WHERE email = '{vendor['email']}'), "
            f"'{vendor['name']}', '{vendor['industry_focus']}', '{vendor['description']}', "
            f"'{vendor['contact_email']}', '{vendor['contact_phone']}', '{vendor['website_url']}', "
            f"'{vendor['country']}', '{vendor['region']}', '{vendor['city']}', "
            f"'{vendor['organization_type']}', {vendor['founded_year']});"
        )
    
    sql_lines.extend([
        "",
        "-- ========================================",
        "-- 3. BUYERS",
        "-- ========================================",
        "",
    ])
    
    buyers = [
        {
            "email": "buyer1@research.edu",
            "name": "David Brown",
            "organization": "University Research Lab",
            "contact_email": "d.brown@research.edu",
            "contact_phone": "+1-555-0201",
            "country": "United States",
            "region": "New York",
            "city": "New York",
            "organization_type": "Academic",
            "job_title": "Research Scientist",
            "industry": "Education",
            "use_case_focus": "Machine learning research on financial time series"
        },
        {
            "email": "buyer2@startup.io",
            "name": "Emma Davis",
            "organization": "TechStart Inc",
            "contact_email": "emma@startup.io",
            "contact_phone": "+1-555-0202",
            "country": "United States",
            "region": "California",
            "city": "Palo Alto",
            "organization_type": "Startup",
            "job_title": "Data Scientist",
            "industry": "Technology",
            "use_case_focus": "Building recommendation systems for e-commerce"
        },
        {
            "email": "buyer3@enterprise.com",
            "name": "Frank Miller",
            "organization": "Enterprise Analytics Ltd",
            "contact_email": "f.miller@enterprise.com",
            "contact_phone": "+1-555-0203",
            "country": "Canada",
            "region": "Ontario",
            "city": "Toronto",
            "organization_type": "Enterprise",
            "job_title": "Chief Data Officer",
            "industry": "Consulting",
            "use_case_focus": "Healthcare outcomes analysis and predictive modeling"
        },
    ]
    
    for buyer in buyers:
        sql_lines.append(
            f"INSERT INTO buyers (user_id, name, organization, contact_email, contact_phone, "
            f"country, region, city, organization_type, job_title, industry, use_case_focus) "
            f"VALUES ("
            f"(SELECT id FROM users WHERE email = '{buyer['email']}'), "
            f"'{buyer['name']}', '{buyer['organization']}', '{buyer['contact_email']}', '{buyer['contact_phone']}', "
            f"'{buyer['country']}', '{buyer['region']}', '{buyer['city']}', "
            f"'{buyer['organization_type']}', '{buyer['job_title']}', '{buyer['industry']}', "
            f"'{buyer['use_case_focus']}');"
        )
    
    sql_lines.extend([
        "",
        "-- ========================================",
        "-- 4. AI AGENTS",
        "-- ========================================",
        "",
    ])
    
    agents = [
        {
            "vendor_email": "vendor1@datamart.com",
            "name": "FinanceBot",
            "description": "AI assistant for financial data queries and analysis",
            "model_used": "gemini-embedding-001",
            "config": {"temperature": 0.7, "max_tokens": 2000},
            "active": True
        },
        {
            "vendor_email": "vendor2@insights.io",
            "name": "HealthInsight AI",
            "description": "Healthcare data exploration and insights assistant",
            "model_used": "gemini-embedding-001",
            "config": {"temperature": 0.5, "max_tokens": 1500},
            "active": True
        },
        {
            "vendor_email": "vendor3@analytics.net",
            "name": "RetailGenie",
            "description": "E-commerce and retail analytics chatbot",
            "model_used": "gemini-embedding-001",
            "config": {"temperature": 0.8, "max_tokens": 2500},
            "active": True
        },
    ]
    
    for agent in agents:
        config_json = json.dumps(agent['config']).replace("'", "''")
        sql_lines.append(
            f"INSERT INTO ai_agents (vendor_id, name, description, model_used, config, active) "
            f"VALUES ("
            f"(SELECT id FROM vendors WHERE user_id = (SELECT id FROM users WHERE email = '{agent['vendor_email']}')), "
            f"'{agent['name']}', '{agent['description']}', '{agent['model_used']}', "
            f"'{config_json}'::jsonb, {str(agent['active']).upper()});"
        )
    
    sql_lines.extend([
        "",
        "-- ========================================",
        "-- 5. DATASETS",
        "-- ========================================",
        "",
    ])
    
    datasets = [
        {
            "vendor_email": "vendor1@datamart.com",
            "title": "Global Stock Market Data 2020-2024",
            "status": "active",
            "visibility": "public",
            "description": "Comprehensive stock market data covering major exchanges worldwide",
            "domain": "Finance",
            "dataset_type": "Time-series",
            "granularity": "Daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["stocks", "markets", "trading"],
            "entities": ["companies", "exchanges", "indices"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "UK", "JP", "DE"], "regions": ["North America", "Europe", "Asia"]},
            "columns": [
                {"name": "ticker", "description": "Stock ticker symbol", "data_type": "VARCHAR(10)", "sample_values": ["AAPL", "GOOGL", "MSFT"]},
                {"name": "date", "description": "Trading date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-01-16"]},
                {"name": "open", "description": "Opening price", "data_type": "DECIMAL(10,2)", "sample_values": [150.25, 151.30]},
                {"name": "close", "description": "Closing price", "data_type": "DECIMAL(10,2)", "sample_values": [152.10, 153.45]},
                {"name": "volume", "description": "Trading volume", "data_type": "BIGINT", "sample_values": [45000000, 42000000]},
            ]
        },
        {
            "vendor_email": "vendor2@insights.io",
            "title": "Patient Outcomes Dataset 2023",
            "status": "active",
            "visibility": "public",
            "description": "Anonymized patient treatment outcomes and recovery metrics",
            "domain": "Healthcare",
            "dataset_type": "Clinical",
            "granularity": "Patient-level",
            "pricing_model": "One-time Purchase",
            "license": "Research Use Only",
            "topics": ["healthcare", "outcomes", "treatment"],
            "entities": ["patients", "treatments", "diagnoses"],
            "temporal_coverage": {"start_date": "2023-01-01", "end_date": "2023-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US"], "regions": ["North America"]},
            "columns": [
                {"name": "patient_id", "description": "Anonymized patient identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4", "e5f6g7h8"]},
                {"name": "diagnosis_code", "description": "ICD-10 diagnosis code", "data_type": "VARCHAR(10)", "sample_values": ["E11.9", "I10"]},
                {"name": "treatment_type", "description": "Type of treatment administered", "data_type": "VARCHAR(100)", "sample_values": ["Medication", "Surgery"]},
                {"name": "outcome_score", "description": "Recovery outcome score (0-100)", "data_type": "INTEGER", "sample_values": [85, 92]},
            ]
        },
        {
            "vendor_email": "vendor3@analytics.net",
            "title": "E-commerce Transactions 2024",
            "status": "active",
            "visibility": "public",
            "description": "Global e-commerce transaction data with product and customer insights",
            "domain": "Retail",
            "dataset_type": "Transactional",
            "granularity": "Transaction-level",
            "pricing_model": "Usage-based",
            "license": "Commercial Use Allowed",
            "topics": ["e-commerce", "retail", "consumer behavior"],
            "entities": ["transactions", "products", "customers"],
            "temporal_coverage": {"start_date": "2024-01-01", "end_date": "2024-12-31", "frequency": "Real-time"},
            "geographic_coverage": {"countries": ["US", "UK", "CA", "AU"], "regions": ["North America", "Europe", "Oceania"]},
            "columns": [
                {"name": "transaction_id", "description": "Unique transaction identifier", "data_type": "UUID", "sample_values": ["tx_001", "tx_002"]},
                {"name": "customer_id", "description": "Customer identifier", "data_type": "UUID", "sample_values": ["cust_123", "cust_456"]},
                {"name": "product_id", "description": "Product SKU", "data_type": "VARCHAR(50)", "sample_values": ["SKU-001", "SKU-002"]},
                {"name": "amount", "description": "Transaction amount in USD", "data_type": "DECIMAL(10,2)", "sample_values": [49.99, 129.99]},
                {"name": "timestamp", "description": "Transaction timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 10:30:00", "2024-01-15 11:45:00"]},
            ]
        },
        {
            "vendor_email": "vendor1@datamart.com",
            "title": "Cryptocurrency Market Data",
            "status": "active",
            "visibility": "public",
            "description": "Real-time and historical cryptocurrency trading data",
            "domain": "Finance",
            "dataset_type": "Time-series",
            "granularity": "Minute-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["cryptocurrency", "blockchain", "trading"],
            "entities": ["coins", "exchanges", "wallets"],
            "temporal_coverage": {"start_date": "2023-01-01", "end_date": "2024-12-31", "frequency": "Minute"},
            "geographic_coverage": {"countries": ["Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "coin_symbol", "description": "Cryptocurrency symbol", "data_type": "VARCHAR(10)", "sample_values": ["BTC", "ETH", "SOL"]},
                {"name": "timestamp", "description": "Price timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 10:00:00"]},
                {"name": "price_usd", "description": "Price in USD", "data_type": "DECIMAL(18,8)", "sample_values": [45000.50, 3200.75]},
                {"name": "volume_24h", "description": "24-hour trading volume", "data_type": "DECIMAL(20,2)", "sample_values": [25000000000.00]},
            ]
        },
    ]
    
    for ds in datasets:
        topics_json = json.dumps(ds['topics']).replace("'", "''")
        entities_json = json.dumps(ds['entities']).replace("'", "''")
        temporal_json = json.dumps(ds['temporal_coverage']).replace("'", "''")
        geographic_json = json.dumps(ds['geographic_coverage']).replace("'", "''")
        
        # Build embedding_input (simplified - backend will regenerate proper embeddings)
        embedding_input = f"{ds['title']} {ds['description']} {ds['domain']}"
        
        sql_lines.append(
            f"INSERT INTO datasets (vendor_id, title, status, visibility, description, domain, dataset_type, "
            f"granularity, pricing_model, license, topics, entities, temporal_coverage, geographic_coverage, embedding_input) "
            f"VALUES ("
            f"(SELECT id FROM vendors WHERE user_id = (SELECT id FROM users WHERE email = '{ds['vendor_email']}')), "
            f"'{ds['title']}', '{ds['status']}', '{ds['visibility']}', '{ds['description']}', "
            f"'{ds['domain']}', '{ds['dataset_type']}', '{ds['granularity']}', '{ds['pricing_model']}', "
            f"'{ds['license']}', '{topics_json}'::jsonb, '{entities_json}'::jsonb, "
            f"'{temporal_json}'::jsonb, '{geographic_json}'::jsonb, '{embedding_input}');"
        )
        
        # Add columns for this dataset
        sql_lines.append("")
        sql_lines.append(f"-- Columns for: {ds['title']}")
        for col in ds['columns']:
            sample_json = json.dumps(col['sample_values']).replace("'", "''")
            sql_lines.append(
                f"INSERT INTO dataset_columns (dataset_id, name, description, data_type, sample_values) "
                f"VALUES ("
                f"(SELECT id FROM datasets WHERE title = '{ds['title']}'), "
                f"'{col['name']}', '{col['description']}', '{col['data_type']}', '{sample_json}'::jsonb);"
            )
        sql_lines.append("")
    
    sql_lines.extend([
        "",
        "-- ========================================",
        "-- DONE",
        "-- ========================================",
        "-- All synthetic data inserted successfully!",
        "-- You can now log in with any user using password: 'password123'",
        "",
    ])
    
    return "\n".join(sql_lines)


def main():
    """Main entry point."""
    print("Generating synthetic data SQL script...")
    print("Hashing passwords with bcrypt (this may take a moment)...")
    
    sql_script = generate_sql()
    
    output_file = "populate_synthetic_data.sql"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(sql_script)
    
    print(f"\n✓ SQL script generated: {output_file}")
    print("\nTo populate your database, run:")
    print(f"  psql -U <username> -d <database_name> -f {output_file}")
    print("\nAll users have password: 'password123'")
    print("\nUsers created:")
    print("  - admin@puddle.com (admin)")
    print("  - vendor1@datamart.com (vendor)")
    print("  - vendor2@insights.io (vendor)")
    print("  - vendor3@analytics.net (vendor)")
    print("  - buyer1@research.edu (buyer)")
    print("  - buyer2@startup.io (buyer)")
    print("  - buyer3@enterprise.com (buyer)")


if __name__ == "__main__":
    main()

