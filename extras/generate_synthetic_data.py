#!/usr/bin/env python3
"""
Generate synthetic data SQL script for Puddle database.
Uses bcrypt for password hashing (same as backend).
Outputs a SQL file ready to run against PostgreSQL.
"""

import sys
from passlib.context import CryptContext
import json
import os
from google import genai
from google.genai import types
from typing import List, Dict, Any
import asyncio
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize bcrypt context (same as backend)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password using bcrypt (same as backend)."""
    if not isinstance(password, str):
        password = str(password)
    password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.hash(password)

def build_embedding_input(ds: Dict[str, Any]) -> str:
    """
    Replicates logic from app/utils/embedding_utils.py
    Builds a text string suitable for embedding from a dataset dictionary.
    """
    domain: str = ds.get("domain") or ""
    topics = ds.get("topics") or []
    description: str = ds.get("description") or ds.get("title") or ""
    columns = ds.get("columns") or []

    col_texts: List[str] = []
    for col in columns:
        # In this script, col is always a dict
        c = col
        name = c.get("name", "")
        desc = c.get("description", "")
        if name and desc:
            col_texts.append(f"{name} — {desc}")
        elif name:
            col_texts.append(name)

    topics_text: str = ", ".join(topics) if isinstance(topics, (list, tuple)) else str(topics)

    pieces: List[str] = []
    if domain:
        pieces.append(f"This dataset focuses on the {domain} domain.")
    if topics_text:
        pieces.append(f"Topics include: {topics_text}.")
    if description:
        pieces.append(description)
        if description[:-1] != ".":
            pieces.append(".")
    if col_texts:
        pieces.append("It includes columns like: " + ", ".join(col_texts))

    result: str = " ".join(pieces).strip()
    return result


async def generate_embedding_vector(text: str, model: str = "gemini-embedding-001") -> List[float]:
    """
    Generate embedding using Google Gemini API.
    """
    api_key = GEMINI_API_KEY
    if not api_key:
        return [0.0] * 1536

    try:
        def sync_call():
            client = genai.Client(api_key=api_key)
            resp = client.models.embed_content(
                model=model,
                contents=text,
                config=types.EmbedContentConfig(
                    task_type="SEMANTIC_SIMILARITY",
                    output_dimensionality=1536,
                ),
            )
            # Handle response structure variation
            try:
                return list(resp.embeddings[0].values)
            except Exception:
                if isinstance(resp, dict) and resp.get("embeddings"):
                    return list(resp["embeddings"][0]["values"])
                raise

        # Run sync API call in thread to avoid blocking
        return await asyncio.to_thread(sync_call)
    except Exception as e:
        return [0.0] * 1536


async def generate_sql():
    """Generate SQL INSERT statements with synthetic data."""
    
    sql_lines = [
        "-- ========================================",
        "-- Puddle Synthetic Data Population Script",
        "-- Generated with bcrypt password hashing",
        "-- ========================================",
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
        # Admin
        {"email": "admin@puddle.com", "role": "admin", "full_name": "Admin User", "hash": common_password_hash},
        
        # FINANCE VENDORS (4)
        {"email": "admin@marketpulse.com", "role": "vendor", "full_name": "Michael Thompson", "hash": common_password_hash},
        {"email": "contact@cryptostream.io", "role": "vendor", "full_name": "Jennifer Wu", "hash": common_password_hash},
        {"email": "info@quantedge.co.uk", "role": "vendor", "full_name": "Robert Sterling", "hash": common_password_hash},
        {"email": "support@fxglobal.com", "role": "vendor", "full_name": "Patricia Lee", "hash": common_password_hash},
        
        # HEALTHCARE VENDORS (4)
        {"email": "contact@medivault.com", "role": "vendor", "full_name": "Dr. Sarah Chen", "hash": common_password_hash},
        {"email": "info@clinicaldata.io", "role": "vendor", "full_name": "Dr. James Patterson", "hash": common_password_hash},
        {"email": "sales@pharmalytics.com", "role": "vendor", "full_name": "Dr. Maria Garcia", "hash": common_password_hash},
        {"email": "support@healthmetrics.org", "role": "vendor", "full_name": "Dr. David Kumar", "hash": common_password_hash},
        
        # ENTERTAINMENT & MEDIA VENDORS (4)
        {"email": "data@streamvault.com", "role": "vendor", "full_name": "Emily Rodriguez", "hash": common_password_hash},
        {"email": "sales@cinemetrics.io", "role": "vendor", "full_name": "Thomas Anderson", "hash": common_password_hash},
        {"email": "info@gamelytics.net", "role": "vendor", "full_name": "Jennifer Park", "hash": common_password_hash},
        {"email": "contact@socialdata.ai", "role": "vendor", "full_name": "Marcus Thompson", "hash": common_password_hash},
        
        # SPORTS VENDORS (4)
        {"email": "data@sportstats.pro", "role": "vendor", "full_name": "Michael Jordan", "hash": common_password_hash},
        {"email": "sales@oddsdata.io", "role": "vendor", "full_name": "Jessica Williams", "hash": common_password_hash},
        {"email": "info@athletemetrics.com", "role": "vendor", "full_name": "Robert Martinez", "hash": common_password_hash},
        {"email": "contact@leagueinsights.net", "role": "vendor", "full_name": "Amanda Chen", "hash": common_password_hash},
        
        # RETAIL VENDORS (4)
        {"email": "data@retailpulse.com", "role": "vendor", "full_name": "Sarah Johnson", "hash": common_password_hash},
        {"email": "sales@ecomanalytics.io", "role": "vendor", "full_name": "David Kim", "hash": common_password_hash},
        {"email": "info@loyaltymetrics.net", "role": "vendor", "full_name": "Maria Garcia", "hash": common_password_hash},
        {"email": "contact@inventoryintel.com", "role": "vendor", "full_name": "James Wilson", "hash": common_password_hash},
        
        # TECHNOLOGY DOMAIN (4 vendors)
        {"email": "data@cloudmetrics.io", "role": "vendor", "full_name": "Jennifer Chen", "hash": common_password_hash},
        {"email": "info@devopsdata.com", "role": "vendor", "full_name": "Robert Martinez", "hash": common_password_hash},
        {"email": "sales@apianalytics.net", "role": "vendor", "full_name": "Emily Taylor", "hash": common_password_hash},
        {"email": "contact@usageinsights.com", "role": "vendor", "full_name": "Michael Brown", "hash": common_password_hash},
        
        # BUYERS (35)
        {"email": "sarah.mitchell@mit.edu", "role": "buyer", "full_name": "Sarah Mitchell", "hash": common_password_hash},
        {"email": "james.chen@datadriven.io", "role": "buyer", "full_name": "James Chen", "hash": common_password_hash},
        {"email": "maria.rodriguez@acme-corp.com", "role": "buyer", "full_name": "Maria Rodriguez", "hash": common_password_hash},
        {"email": "david.kim@stanford.edu", "role": "buyer", "full_name": "David Kim", "hash": common_password_hash},
        {"email": "rachel.johnson@microsoft.com", "role": "buyer", "full_name": "Rachel Johnson", "hash": common_password_hash},
        {"email": "alexander.murphy@mckinsey.com", "role": "buyer", "full_name": "Alexander Murphy", "hash": common_password_hash},
        {"email": "olivia.zhang@quanthedge.com", "role": "buyer", "full_name": "Olivia Zhang", "hash": common_password_hash},
        {"email": "marcus.williams@who-research.org", "role": "buyer", "full_name": "Marcus Williams", "hash": common_password_hash},
        {"email": "emma.taylor@netflix-analytics.com", "role": "buyer", "full_name": "Emma Taylor", "hash": common_password_hash},
        {"email": "liam.patel@sportstech.ai", "role": "buyer", "full_name": "Liam Patel", "hash": common_password_hash},
        {"email": "sophia.anderson@govdata.gov", "role": "buyer", "full_name": "Sophia Anderson", "hash": common_password_hash},
        {"email": "william.lee@walmart-labs.com", "role": "buyer", "full_name": "William Lee", "hash": common_password_hash},
        {"email": "ava.wong@singtel-insights.sg", "role": "buyer", "full_name": "Ava Wong", "hash": common_password_hash},
        {"email": "noah.fischer@berlin-institute.de", "role": "buyer", "full_name": "Noah Fischer", "hash": common_password_hash},
        {"email": "isabella.martin@aetna-analytics.com", "role": "buyer", "full_name": "Isabella Martin", "hash": common_password_hash},
        {"email": "ethan.brown@jpmorgan-risk.com", "role": "buyer", "full_name": "Ethan Brown", "hash": common_password_hash},
        {"email": "mia.santos@roche-analytics.ch", "role": "buyer", "full_name": "Mia Santos", "hash": common_password_hash},
        {"email": "lucas.davies@bbc-insights.uk", "role": "buyer", "full_name": "Lucas Davies", "hash": common_password_hash},
        {"email": "amelia.nguyen@riot-games.com", "role": "buyer", "full_name": "Amelia Nguyen", "hash": common_password_hash},
        {"email": "benjamin.cooper@campaign-hq.org", "role": "buyer", "full_name": "Benjamin Cooper", "hash": common_password_hash},
        {"email": "charlotte.torres@blackrock-quant.com", "role": "buyer", "full_name": "Charlotte Torres", "hash": common_password_hash},
        {"email": "henry.tanaka@tokyo-medical.jp", "role": "buyer", "full_name": "Henry Tanaka", "hash": common_password_hash},
        {"email": "grace.eriksson@spotify-analytics.se", "role": "buyer", "full_name": "Grace Eriksson", "hash": common_password_hash},
        {"email": "daniel.phillips@nba-stats.com", "role": "buyer", "full_name": "Daniel Phillips", "hash": common_password_hash},
        {"email": "zoe.murphy@gallup-polling.com", "role": "buyer", "full_name": "Zoe Murphy", "hash": common_password_hash},
        {"email": "jack.bennett@amazon-retail.com", "role": "buyer", "full_name": "Jack Bennett", "hash": common_password_hash},
        {"email": "lily.ross@google-cloud.com", "role": "buyer", "full_name": "Lily Ross", "hash": common_password_hash},
        {"email": "owen.coleman@ucsd-bio.edu", "role": "buyer", "full_name": "Owen Coleman", "hash": common_password_hash},
        {"email": "harper.hughes@citadel-quant.com", "role": "buyer", "full_name": "Harper Hughes", "hash": common_password_hash},
        {"email": "elijah.bell@community-health.org", "role": "buyer", "full_name": "Elijah Bell", "hash": common_password_hash},
        {"email": "chloe.carter@universal-studios.com", "role": "buyer", "full_name": "Chloe Carter", "hash": common_password_hash},
        {"email": "ryan.mitchell@cowboys-analytics.com", "role": "buyer", "full_name": "Ryan Mitchell", "hash": common_password_hash},
        {"email": "aria.barnes@brookings.org", "role": "buyer", "full_name": "Aria Barnes", "hash": common_password_hash},
        {"email": "tyler.watson@tesco-analytics.uk", "role": "buyer", "full_name": "Tyler Watson", "hash": common_password_hash},
        {"email": "luna.hayes@aws-ireland.ie", "role": "buyer", "full_name": "Luna Hayes", "hash": common_password_hash},
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
        # FINANCE DOMAIN (4 vendors)
        {"email": "admin@marketpulse.com", "name": "MarketPulse Data", "industry_focus": "Finance", "description": "Premium equity market data and company financials for institutional investors", "contact_email": "sales@marketpulse.com", "contact_phone": "+1-212-555-2001", "website_url": "https://marketpulse.com", "country": "United States", "region": "New York", "city": "New York", "organization_type": "Corporation", "founded_year": 2015},
        {"email": "contact@cryptostream.io", "name": "CryptoStream Analytics", "industry_focus": "Finance", "description": "Real-time cryptocurrency and blockchain data for traders and institutions", "contact_email": "hello@cryptostream.io", "contact_phone": "+1-415-555-2002", "website_url": "https://cryptostream.io", "country": "United States", "region": "California", "city": "San Francisco", "organization_type": "Startup", "founded_year": 2019},
        {"email": "info@quantedge.co.uk", "name": "QuantEdge Financial Data", "industry_focus": "Finance", "description": "Alternative financial data and derivatives market intelligence", "contact_email": "sales@quantedge.co.uk", "contact_phone": "+44-20-555-2003", "website_url": "https://quantedge.co.uk", "country": "United Kingdom", "region": "England", "city": "London", "organization_type": "Corporation", "founded_year": 2012},
        {"email": "support@fxglobal.com", "name": "FX Global Markets", "industry_focus": "Finance", "description": "Foreign exchange rates and international trade data provider", "contact_email": "contact@fxglobal.com", "contact_phone": "+65-6555-2004", "website_url": "https://fxglobal.com", "country": "Singapore", "region": "Central Region", "city": "Singapore", "organization_type": "Corporation", "founded_year": 2014},
        
        # HEALTHCARE DOMAIN (4 vendors)
        {"email": "contact@medivault.com", "name": "MediVault Health Data", "industry_focus": "Healthcare", "description": "HIPAA-compliant clinical data and electronic health records analytics", "contact_email": "sales@medivault.com", "contact_phone": "+1-617-555-3001", "website_url": "https://medivault.com", "country": "United States", "region": "Massachusetts", "city": "Boston", "organization_type": "Corporation", "founded_year": 2016},
        {"email": "info@clinicaldata.io", "name": "ClinicalData Intelligence", "industry_focus": "Healthcare", "description": "Clinical trial data and pharmaceutical research datasets", "contact_email": "hello@clinicaldata.io", "contact_phone": "+41-61-555-3002", "website_url": "https://clinicaldata.io", "country": "Switzerland", "region": "Basel", "city": "Basel", "organization_type": "Startup", "founded_year": 2018},
        {"email": "sales@pharmalytics.com", "name": "PharmaLytics Global", "industry_focus": "Healthcare", "description": "Drug prescription data and pharmaceutical market intelligence", "contact_email": "contact@pharmalytics.com", "contact_phone": "+44-20-555-3003", "website_url": "https://pharmalytics.com", "country": "United Kingdom", "region": "England", "city": "London", "organization_type": "Corporation", "founded_year": 2013},
        {"email": "support@healthmetrics.org", "name": "HealthMetrics Institute", "industry_focus": "Healthcare", "description": "Public health data and epidemiological surveillance datasets", "contact_email": "info@healthmetrics.org", "contact_phone": "+1-404-555-3004", "website_url": "https://healthmetrics.org", "country": "United States", "region": "Georgia", "city": "Atlanta", "organization_type": "Non-profit", "founded_year": 2010},
        
        # ENTERTAINMENT & MEDIA DOMAIN (4 vendors)
        {"email": "data@streamvault.com", "name": "StreamVault Media Analytics", "industry_focus": "Entertainment & Media", "description": "Music, podcast, and video streaming consumption data with audience engagement metrics", "contact_email": "sales@streamvault.com", "contact_phone": "+1-310-555-4001", "website_url": "https://streamvault.com", "country": "United States", "region": "California", "city": "Los Angeles", "organization_type": "Corporation", "founded_year": 2017},
        {"email": "sales@cinemetrics.io", "name": "CineMetrics Intelligence", "industry_focus": "Entertainment & Media", "description": "Box office performance, TV ratings, and film/television industry analytics", "contact_email": "info@cinemetrics.io", "contact_phone": "+1-323-555-4002", "website_url": "https://cinemetrics.io", "country": "United States", "region": "California", "city": "Hollywood", "organization_type": "Startup", "founded_year": 2019},
        {"email": "info@gamelytics.net", "name": "GameLytics Pro", "industry_focus": "Entertainment & Media", "description": "Video game telemetry, player behavior, and esports analytics", "contact_email": "support@gamelytics.net", "contact_phone": "+1-206-555-4003", "website_url": "https://gamelytics.net", "country": "United States", "region": "Washington", "city": "Seattle", "organization_type": "Corporation", "founded_year": 2016},
        {"email": "contact@socialdata.ai", "name": "SocialData Insights", "industry_focus": "Entertainment & Media", "description": "Social media engagement, influencer analytics, and digital content performance data", "contact_email": "hello@socialdata.ai", "contact_phone": "+1-415-555-4004", "website_url": "https://socialdata.ai", "country": "United States", "region": "California", "city": "San Francisco", "organization_type": "Startup", "founded_year": 2020},
        
        # SPORTS DOMAIN (4 vendors)
        {"email": "data@sportstats.pro", "name": "SportStats Global", "industry_focus": "Sports", "description": "Comprehensive sports statistics, game results, and player performance data across major leagues", "contact_email": "sales@sportstats.pro", "contact_phone": "+1-212-555-5001", "website_url": "https://sportstats.pro", "country": "United States", "region": "New York", "city": "New York", "organization_type": "Corporation", "founded_year": 2008},
        {"email": "sales@oddsdata.io", "name": "OddsData Analytics", "industry_focus": "Sports", "description": "Sports betting odds, lines, and wagering analytics across global sportsbooks", "contact_email": "info@oddsdata.io", "contact_phone": "+44-20-555-5002", "website_url": "https://oddsdata.io", "country": "United Kingdom", "region": "England", "city": "London", "organization_type": "Startup", "founded_year": 2019},
        {"email": "info@athletemetrics.com", "name": "AthleteMetrics Performance", "industry_focus": "Sports", "description": "Athlete biometrics, training data, and performance analytics for professional sports", "contact_email": "support@athletemetrics.com", "contact_phone": "+1-650-555-5003", "website_url": "https://athletemetrics.com", "country": "United States", "region": "California", "city": "Palo Alto", "organization_type": "Corporation", "founded_year": 2015},
        {"email": "contact@leagueinsights.net", "name": "LeagueInsights Data", "industry_focus": "Sports", "description": "League-wide analytics, franchise valuations, and sports business intelligence", "contact_email": "hello@leagueinsights.net", "contact_phone": "+1-312-555-5004", "website_url": "https://leagueinsights.net", "country": "United States", "region": "Illinois", "city": "Chicago", "organization_type": "Startup", "founded_year": 2021},
        
        # RETAIL DOMAIN (4 vendors)
        {"email": "data@retailpulse.com", "name": "RetailPulse Analytics", "industry_focus": "Retail", "description": "Point-of-sale data, store performance, and retail transaction analytics", "contact_email": "sales@retailpulse.com", "contact_phone": "+1-469-555-6001", "website_url": "https://retailpulse.com", "country": "United States", "region": "Texas", "city": "Dallas", "organization_type": "Corporation", "founded_year": 2012},
        {"email": "sales@ecomanalytics.io", "name": "EcomAnalytics Pro", "industry_focus": "Retail", "description": "E-commerce metrics, online shopping behavior, and digital retail analytics", "contact_email": "info@ecomanalytics.io", "contact_phone": "+1-206-555-6002", "website_url": "https://ecomanalytics.io", "country": "United States", "region": "Washington", "city": "Seattle", "organization_type": "Startup", "founded_year": 2018},
        {"email": "info@loyaltymetrics.net", "name": "LoyaltyMetrics Intelligence", "industry_focus": "Retail", "description": "Customer loyalty programs, rewards analytics, and retention data", "contact_email": "support@loyaltymetrics.net", "contact_phone": "+1-404-555-6003", "website_url": "https://loyaltymetrics.net", "country": "United States", "region": "Georgia", "city": "Atlanta", "organization_type": "Corporation", "founded_year": 2015},
        {"email": "contact@inventoryintel.com", "name": "InventoryIntel Solutions", "industry_focus": "Retail", "description": "Supply chain data, inventory management, and stock level analytics", "contact_email": "hello@inventoryintel.com", "contact_phone": "+1-312-555-6004", "website_url": "https://inventoryintel.com", "country": "United States", "region": "Illinois", "city": "Chicago", "organization_type": "Startup", "founded_year": 2020},
        
        # TECHNOLOGY DOMAIN (4 vendors)
        {"email": "data@cloudmetrics.io", "name": "CloudMetrics Analytics", "industry_focus": "Technology", "description": "Cloud infrastructure metrics, resource utilization, cost analytics, and SaaS performance data", "contact_email": "support@cloudmetrics.io", "contact_phone": "+1-415-555-7001", "website_url": "https://cloudmetrics.io", "country": "United States", "region": "California", "city": "San Francisco", "organization_type": "Startup", "founded_year": 2019},
        {"email": "info@devopsdata.com", "name": "DevOps Intelligence", "industry_focus": "Technology", "description": "DevOps metrics, CI/CD analytics, deployment tracking, and software delivery performance data", "contact_email": "data@devopsdata.com", "contact_phone": "+1-512-555-7002", "website_url": "https://devopsdata.com", "country": "United States", "region": "Texas", "city": "Austin", "organization_type": "Corporation", "founded_year": 2016},
        {"email": "sales@apianalytics.net", "name": "API Analytics Pro", "industry_focus": "Technology", "description": "API usage metrics, endpoint performance, integration analytics, and developer platform data", "contact_email": "info@apianalytics.net", "contact_phone": "+1-617-555-7003", "website_url": "https://apianalytics.net", "country": "United States", "region": "Massachusetts", "city": "Boston", "organization_type": "Startup", "founded_year": 2020},
        {"email": "contact@usageinsights.com", "name": "SaaS Usage Insights", "industry_focus": "Technology", "description": "SaaS application usage, feature adoption, user engagement, and product analytics data", "contact_email": "hello@usageinsights.com", "contact_phone": "+1-206-555-7004", "website_url": "https://usageinsights.com", "country": "United States", "region": "Washington", "city": "Seattle", "organization_type": "Startup", "founded_year": 2018},
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
        {"email": "sarah.mitchell@mit.edu", "name": "Sarah Mitchell", "organization": "MIT Research Lab", "contact_email": "sarah.mitchell@mit.edu", "contact_phone": "+1-617-555-0101", "country": "United States", "region": "Massachusetts", "city": "Cambridge", "organization_type": "Academic", "job_title": "Research Scientist", "industry": "Education", "use_case_focus": "Machine learning research on financial time series and market prediction"},
        {"email": "james.chen@datadriven.io", "name": "James Chen", "organization": "DataDriven Analytics", "contact_email": "james@datadriven.io", "contact_phone": "+1-415-555-0102", "country": "United States", "region": "California", "city": "San Francisco", "organization_type": "Startup", "job_title": "Lead Data Scientist", "industry": "Technology", "use_case_focus": "Building personalized recommendation engines for e-commerce platforms"},
        {"email": "maria.rodriguez@acme-corp.com", "name": "Maria Rodriguez", "organization": "Acme Analytics Corporation", "contact_email": "m.rodriguez@acme-corp.com", "contact_phone": "+1-416-555-0103", "country": "Canada", "region": "Ontario", "city": "Toronto", "organization_type": "Enterprise", "job_title": "Chief Data Officer", "industry": "Consulting", "use_case_focus": "Healthcare outcomes analysis and predictive modeling for hospitals"},
        {"email": "david.kim@stanford.edu", "name": "David Kim", "organization": "Stanford Political Science Lab", "contact_email": "dkim@stanford.edu", "contact_phone": "+1-650-555-0104", "country": "United States", "region": "California", "city": "Palo Alto", "organization_type": "Academic", "job_title": "Associate Professor", "industry": "Education", "use_case_focus": "Election forecasting and political sentiment analysis using polling data"},
        {"email": "rachel.johnson@microsoft.com", "name": "Rachel Johnson", "organization": "Microsoft Research", "contact_email": "rachel.j@microsoft.com", "contact_phone": "+1-425-555-0105", "country": "United States", "region": "Washington", "city": "Seattle", "organization_type": "Enterprise", "job_title": "Senior ML Engineer", "industry": "Technology", "use_case_focus": "Content recommendation systems and user engagement analytics"},
        {"email": "alexander.murphy@mckinsey.com", "name": "Alexander Murphy", "organization": "McKinsey Analytics", "contact_email": "alex.murphy@mckinsey.com", "contact_phone": "+1-212-555-0106", "country": "United States", "region": "New York", "city": "New York", "organization_type": "Enterprise", "job_title": "Senior Business Analyst", "industry": "Consulting", "use_case_focus": "Retail market intelligence and consumer behavior trends analysis"},
        {"email": "olivia.zhang@quanthedge.com", "name": "Olivia Zhang", "organization": "QuantHedge Capital", "contact_email": "o.zhang@quanthedge.com", "contact_phone": "+44-20-555-0107", "country": "United Kingdom", "region": "England", "city": "London", "organization_type": "Enterprise", "job_title": "Quantitative Analyst", "industry": "Finance", "use_case_focus": "Algorithmic trading strategies and market microstructure analysis"},
        {"email": "marcus.williams@who-research.org", "name": "Marcus Williams", "organization": "Global Health Research Institute", "contact_email": "m.williams@who-research.org", "contact_phone": "+41-22-555-0108", "country": "Switzerland", "region": "Geneva", "city": "Geneva", "organization_type": "Non-profit", "job_title": "Research Director", "industry": "Healthcare", "use_case_focus": "Disease surveillance and public health intervention effectiveness"},
        {"email": "emma.taylor@netflix-analytics.com", "name": "Emma Taylor", "organization": "StreamVision Media", "contact_email": "emma.t@streamvision.com", "contact_phone": "+1-323-555-0109", "country": "United States", "region": "California", "city": "Los Angeles", "organization_type": "Enterprise", "job_title": "Senior Data Analyst", "industry": "Entertainment", "use_case_focus": "Content performance analytics and viewer engagement optimization"},
        {"email": "liam.patel@sportstech.ai", "name": "Liam Patel", "organization": "SportsTech Analytics", "contact_email": "liam@sportstech.ai", "contact_phone": "+1-312-555-0110", "country": "United States", "region": "Illinois", "city": "Chicago", "organization_type": "Startup", "job_title": "Sports Data Scientist", "industry": "Sports", "use_case_focus": "Player performance prediction and team strategy optimization using advanced metrics"},
        {"email": "sophia.anderson@govdata.gov", "name": "Sophia Anderson", "organization": "Federal Policy Analytics Bureau", "contact_email": "s.anderson@govdata.gov", "contact_phone": "+1-202-555-0111", "country": "United States", "region": "District of Columbia", "city": "Washington", "organization_type": "Government", "job_title": "Senior Policy Analyst", "industry": "Government", "use_case_focus": "Legislative impact assessment and public policy effectiveness research"},
        {"email": "william.lee@walmart-labs.com", "name": "William Lee", "organization": "RetailMax Corporation", "contact_email": "w.lee@retailmax.com", "contact_phone": "+1-479-555-0112", "country": "United States", "region": "Arkansas", "city": "Bentonville", "organization_type": "Enterprise", "job_title": "Director of Business Intelligence", "industry": "Retail", "use_case_focus": "Inventory optimization and customer lifetime value prediction"},
        {"email": "ava.wong@singtel-insights.sg", "name": "Ava Wong", "organization": "AsiaPac DataInsights", "contact_email": "ava.wong@asiapac-insights.sg", "contact_phone": "+65-6555-0113", "country": "Singapore", "region": "Central Region", "city": "Singapore", "organization_type": "Startup", "job_title": "Analytics Lead", "industry": "Consulting", "use_case_focus": "Cross-industry competitive intelligence and market trend forecasting"},
        {"email": "noah.fischer@berlin-institute.de", "name": "Noah Fischer", "organization": "Berlin Research Institute", "contact_email": "n.fischer@berlin-inst.de", "contact_phone": "+49-30-555-0114", "country": "Germany", "region": "Berlin", "city": "Berlin", "organization_type": "Academic", "job_title": "Principal Researcher", "industry": "Education", "use_case_focus": "Social media impact on political discourse and election outcomes"},
        {"email": "isabella.martin@aetna-analytics.com", "name": "Isabella Martin", "organization": "HealthGuard Insurance", "contact_email": "i.martin@healthguard.com", "contact_phone": "+1-860-555-0115", "country": "United States", "region": "Connecticut", "city": "Hartford", "organization_type": "Enterprise", "job_title": "Chief Actuarial Analyst", "industry": "Insurance", "use_case_focus": "Risk modeling using healthcare claims and demographic data"},
        {"email": "ethan.brown@jpmorgan-risk.com", "name": "Ethan Brown", "organization": "Global Trust Bank", "contact_email": "e.brown@globaltrust.com", "contact_phone": "+44-20-555-0116", "country": "United Kingdom", "region": "England", "city": "London", "organization_type": "Enterprise", "job_title": "VP of Risk Management", "industry": "Finance", "use_case_focus": "Credit risk assessment and fraud detection using transaction patterns"},
        {"email": "mia.santos@roche-analytics.ch", "name": "Mia Santos", "organization": "PharmaCore Research", "contact_email": "m.santos@pharmacore.ch", "contact_phone": "+41-61-555-0117", "country": "Switzerland", "region": "Basel", "city": "Basel", "organization_type": "Enterprise", "job_title": "Clinical Data Manager", "industry": "Healthcare", "use_case_focus": "Drug efficacy analysis and patient outcome prediction in clinical trials"},
        {"email": "lucas.davies@bbc-insights.uk", "name": "Lucas Davies", "organization": "British Media Analytics", "contact_email": "l.davies@britishmedia.uk", "contact_phone": "+44-20-555-0118", "country": "United Kingdom", "region": "England", "city": "London", "organization_type": "Enterprise", "job_title": "Head of Audience Research", "industry": "Entertainment", "use_case_focus": "Television ratings optimization and audience demographic segmentation"},
        {"email": "amelia.nguyen@riot-games.com", "name": "Amelia Nguyen", "organization": "PixelForge Studios", "contact_email": "a.nguyen@pixelforge.io", "contact_phone": "+1-310-555-0119", "country": "United States", "region": "California", "city": "Los Angeles", "organization_type": "Startup", "job_title": "Lead Game Designer", "industry": "Entertainment", "use_case_focus": "Player behavior analytics and game economy balancing using telemetry data"},
        {"email": "benjamin.cooper@campaign-hq.org", "name": "Benjamin Cooper", "organization": "Victory Campaign Strategies", "contact_email": "b.cooper@victory-campaign.org", "contact_phone": "+1-202-555-0120", "country": "United States", "region": "District of Columbia", "city": "Washington", "organization_type": "Non-profit", "job_title": "Campaign Data Director", "industry": "Politics", "use_case_focus": "Voter targeting and micro-targeting for political campaigns using polling data"},
        {"email": "charlotte.torres@blackrock-quant.com", "name": "Charlotte Torres", "organization": "Apex Capital Management", "contact_email": "c.torres@apexcapital.com", "contact_phone": "+1-212-555-0121", "country": "United States", "region": "New York", "city": "New York", "organization_type": "Enterprise", "job_title": "Portfolio Manager", "industry": "Finance", "use_case_focus": "Alternative data integration for investment decision making and alpha generation"},
        {"email": "henry.tanaka@tokyo-medical.jp", "name": "Henry Tanaka", "organization": "Metropolitan Medical Center", "contact_email": "h.tanaka@metro-med.jp", "contact_phone": "+81-3-555-0122", "country": "Japan", "region": "Tokyo", "city": "Tokyo", "organization_type": "Healthcare", "job_title": "Clinical Research Coordinator", "industry": "Healthcare", "use_case_focus": "Patient treatment pathway optimization and hospital operations efficiency"},
        {"email": "grace.eriksson@spotify-analytics.se", "name": "Grace Eriksson", "organization": "SoundWave Platform", "contact_email": "g.eriksson@soundwave.se", "contact_phone": "+46-8-555-0123", "country": "Sweden", "region": "Stockholm", "city": "Stockholm", "organization_type": "Startup", "job_title": "Product Data Analyst", "industry": "Entertainment", "use_case_focus": "Music recommendation algorithms and playlist curation optimization"},
        {"email": "daniel.phillips@nba-stats.com", "name": "Daniel Phillips", "organization": "Premier League Analytics", "contact_email": "d.phillips@premier-analytics.com", "contact_phone": "+1-212-555-0124", "country": "United States", "region": "New York", "city": "New York", "organization_type": "Enterprise", "job_title": "Director of Analytics", "industry": "Sports", "use_case_focus": "League operations optimization and fan engagement analytics using attendance data"},
        {"email": "zoe.murphy@gallup-polling.com", "name": "Zoe Murphy", "organization": "Electoral Insights Group", "contact_email": "z.murphy@electoral-insights.org", "contact_phone": "+1-703-555-0125", "country": "United States", "region": "Virginia", "city": "Arlington", "organization_type": "Non-profit", "job_title": "Senior Data Director", "industry": "Politics", "use_case_focus": "Election forecasting models and voter turnout prediction"},
        {"email": "jack.bennett@amazon-retail.com", "name": "Jack Bennett", "organization": "E-Shop Marketplace", "contact_email": "j.bennett@eshop-market.com", "contact_phone": "+1-206-555-0126", "country": "United States", "region": "Washington", "city": "Seattle", "organization_type": "Enterprise", "job_title": "Senior Data Engineer", "industry": "Retail", "use_case_focus": "Customer churn prediction and lifetime value optimization for e-commerce"},
        {"email": "lily.ross@google-cloud.com", "name": "Lily Ross", "organization": "CloudScale Technologies", "contact_email": "l.ross@cloudscale.tech", "contact_phone": "+1-408-555-0127", "country": "United States", "region": "California", "city": "San Jose", "organization_type": "Startup", "job_title": "Engineering Manager", "industry": "Technology", "use_case_focus": "Software usage telemetry and feature adoption analytics for SaaS products"},
        {"email": "owen.coleman@ucsd-bio.edu", "name": "Owen Coleman", "organization": "Biomedical Genomics Lab", "contact_email": "o.coleman@ucsd-bio.edu", "contact_phone": "+1-858-555-0128", "country": "United States", "region": "California", "city": "San Diego", "organization_type": "Academic", "job_title": "Principal Investigator", "industry": "Healthcare", "use_case_focus": "Genomics data analysis for precision medicine and drug target discovery"},
        {"email": "harper.hughes@citadel-quant.com", "name": "Harper Hughes", "organization": "Quantum Trading Partners", "contact_email": "h.hughes@quantumtrading.com", "contact_phone": "+1-203-555-0129", "country": "United States", "region": "Connecticut", "city": "Greenwich", "organization_type": "Enterprise", "job_title": "Quantitative Researcher", "industry": "Finance", "use_case_focus": "High-frequency trading strategies and market microstructure analysis"},
        {"email": "elijah.bell@community-health.org", "name": "Elijah Bell", "organization": "Community Health Network", "contact_email": "e.bell@commhealth.org", "contact_phone": "+1-713-555-0130", "country": "United States", "region": "Texas", "city": "Houston", "organization_type": "Non-profit", "job_title": "Medical Director", "industry": "Healthcare", "use_case_focus": "Population health management and preventive care program effectiveness"},
        {"email": "chloe.carter@universal-studios.com", "name": "Chloe Carter", "organization": "Silver Screen Studios", "contact_email": "c.carter@silverscreen.com", "contact_phone": "+1-818-555-0131", "country": "United States", "region": "California", "city": "Burbank", "organization_type": "Enterprise", "job_title": "Market Research Analyst", "industry": "Entertainment", "use_case_focus": "Box office forecasting and audience demographic analysis for film releases"},
        {"email": "ryan.mitchell@cowboys-analytics.com", "name": "Ryan Mitchell", "organization": "Championship Sports Team", "contact_email": "r.mitchell@championship-team.com", "contact_phone": "+1-214-555-0132", "country": "United States", "region": "Texas", "city": "Dallas", "organization_type": "Enterprise", "job_title": "Performance Analyst", "industry": "Sports", "use_case_focus": "Player scouting and game strategy analysis using advanced statistics"},
        {"email": "aria.barnes@brookings.org", "name": "Aria Barnes", "organization": "Policy Research Institute", "contact_email": "a.barnes@policy-research.org", "contact_phone": "+1-202-555-0133", "country": "United States", "region": "District of Columbia", "city": "Washington", "organization_type": "Non-profit", "job_title": "Senior Research Fellow", "industry": "Politics", "use_case_focus": "Legislative effectiveness analysis and policy impact assessment"},
        {"email": "tyler.watson@tesco-analytics.uk", "name": "Tyler Watson", "organization": "GlobalMart Enterprises", "contact_email": "t.watson@globalmart.uk", "contact_phone": "+44-161-555-0134", "country": "United Kingdom", "region": "England", "city": "Manchester", "organization_type": "Enterprise", "job_title": "Head of Data Analytics", "industry": "Retail", "use_case_focus": "Supply chain optimization and demand forecasting using POS data"},
        {"email": "luna.hayes@aws-ireland.ie", "name": "Luna Hayes", "organization": "CloudInfra Systems", "contact_email": "l.hayes@cloudinfra.ie", "contact_phone": "+353-1-555-0135", "country": "Ireland", "region": "Dublin", "city": "Dublin", "organization_type": "Startup", "job_title": "Data Platform Lead", "industry": "Technology", "use_case_focus": "Cloud infrastructure monitoring and cost optimization analytics"},
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
        # FINANCE DOMAIN
        {
            "vendor_email": "data@marketpulse.io",
            "name": "MarketPulse Assistant",
            "description": "AI assistant for stock market data, equity prices, and trading volume analysis",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "All data is sourced from major stock exchanges with 15-minute delay for real-time feeds. Historical data available back to 2010.",
                "usage_guidelines": "Our datasets are ideal for backtesting trading strategies, portfolio analysis, and market research. Commercial use allowed with proper attribution.",
                "data_refresh": "Real-time data updated every 15 minutes during market hours. End-of-day data available by 6 PM ET.",
                "support_contact": "For technical support or custom data requests, email support@marketpulse.io"
            },
            "active": True
        },
        {
            "vendor_email": "sales@cryptostream.net",
            "name": "CryptoStream Agent",
            "description": "AI assistant for cryptocurrency market data, trading pairs, and blockchain analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "We aggregate data from 50+ exchanges worldwide. Data includes spot, futures, and perpetual markets with tick-level granularity.",
                "usage_guidelines": "Perfect for crypto trading algorithms, market making strategies, and DeFi research. API access included with all subscriptions.",
                "data_coverage": "Coverage includes 5000+ cryptocurrencies and tokens across major blockchains (Bitcoin, Ethereum, Binance Smart Chain, Solana).",
                "compliance_note": "All data is public blockchain data. Users responsible for compliance with local cryptocurrency regulations."
            },
            "active": True
        },
        {
            "vendor_email": "info@quantedge.com",
            "name": "QuantEdge Advisor",
            "description": "AI assistant for derivatives data, options chains, and quantitative trading analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "Premium derivatives data covering equity options, index options, and futures. Institutional-grade quality with microsecond timestamps.",
                "usage_guidelines": "Designed for quantitative researchers, options traders, and risk managers. Full historical options chains available for backtesting.",
                "data_quality": "We perform rigorous data cleaning and normalization. Includes implied volatility calculations and Greeks for all options.",
                "licensing": "Commercial use requires Enterprise tier subscription. Academic discounts available for university researchers."
            },
            "active": True
        },
        {
            "vendor_email": "contact@fxglobal.com",
            "name": "FX Global Assistant",
            "description": "AI assistant for foreign exchange rates, currency pair data, and forex market analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "FX data sourced from major banks and ECNs. Covers 180+ currency pairs with tick-by-tick data for major pairs.",
                "usage_guidelines": "Ideal for forex trading, currency risk management, and international treasury operations. Includes central bank rates and economic indicators.",
                "data_updates": "Real-time streaming available 24/5 during forex market hours. Historical data back to 1999.",
                "special_features": "We provide correlation matrices, volatility indices, and carry trade indicators as complementary analytics."
            },
            "active": True
        },
        
        # HEALTHCARE DOMAIN
        {
            "vendor_email": "data@medivault.com",
            "name": "MediVault Assistant",
            "description": "AI assistant for electronic health records, patient data, and clinical outcomes analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "All patient data is fully anonymized and HIPAA-compliant. We never share identifiable health information.",
                "usage_guidelines": "Designed for healthcare researchers, hospital administrators, and population health analysts. IRB approval may be required for certain use cases.",
                "data_security": "We maintain SOC 2 Type II and HITRUST certifications. All data encrypted at rest and in transit.",
                "ethical_use": "Data must be used for legitimate healthcare research and quality improvement. Prohibited uses include patient re-identification attempts."
            },
            "active": True
        },
        {
            "vendor_email": "info@clinicaldata.io",
            "name": "ClinicalData Agent",
            "description": "AI assistant for clinical trial data, research outcomes, and pharmaceutical trial analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "Clinical trial data aggregated from ClinicalTrials.gov and global trial registries. Includes trial protocols, enrollment data, and published results.",
                "usage_guidelines": "Perfect for pharmaceutical companies, CROs, and academic medical centers conducting competitive intelligence and trial planning.",
                "data_coverage": "Over 500,000 clinical trials from 2000-present across all therapeutic areas and phases.",
                "licensing": "Academic institutions receive 40% discount. Pharma and biotech companies require commercial license."
            },
            "active": True
        },
        {
            "vendor_email": "sales@pharmalytics.net",
            "name": "PharmaLytics Advisor",
            "description": "AI assistant for pharmaceutical sales, drug prescriptions, and market share analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "Prescription data sourced from anonymized pharmacy claims and de-identified patient records. Fully compliant with HIPAA and state privacy laws.",
                "usage_guidelines": "Essential for pharmaceutical market research, drug launch planning, and sales force effectiveness analysis.",
                "data_granularity": "Available at physician-level, zip code, and DMA geography. Updated monthly with 6-8 week lag.",
                "competitive_intel": "Track market share trends, generic erosion, and prescriber behavior patterns across therapeutic classes."
            },
            "active": True
        },
        {
            "vendor_email": "contact@healthmetrics.org",
            "name": "HealthMetrics Assistant",
            "description": "AI assistant for population health data, disease prevalence, and public health analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "Public health data aggregated from CDC, WHO, and state health departments. All data is publicly available but curated for research use.",
                "usage_guidelines": "Ideal for epidemiologists, health policy researchers, and public health officials tracking disease trends and intervention effectiveness.",
                "data_sources": "Combines multiple authoritative sources with standardized coding (ICD-10, SNOMED CT) for interoperability.",
                "updates": "Disease surveillance data updated weekly. Mortality and census data updated annually."
            },
            "active": True
        },
        
        # ENTERTAINMENT & MEDIA DOMAIN
        {
            "vendor_email": "data@streamvault.io",
            "name": "StreamVault Agent",
            "description": "AI assistant for streaming platform data, content performance, and audience engagement analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "Streaming data collected from partnerships with major platforms and public APIs. All user data anonymized to protect privacy.",
                "usage_guidelines": "Perfect for content producers, studios, and streaming platforms analyzing viewership trends and content ROI.",
                "data_coverage": "Covers Netflix, Disney+, Amazon Prime, HBO Max, and 20+ other platforms. Global coverage across 50+ countries.",
                "insights": "Includes genre performance, binge-watching patterns, content discovery paths, and subscriber churn indicators."
            },
            "active": True
        },
        {
            "vendor_email": "sales@cinemetrics.com",
            "name": "CineMetrics Assistant",
            "description": "AI assistant for box office data, movie performance, and theatrical analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "Box office data sourced from theater chains, distributors, and Box Office Mojo. Historical data back to 1980.",
                "usage_guidelines": "Essential for film studios, distributors, and entertainment analysts forecasting theatrical performance and planning release strategies.",
                "data_granularity": "Daily box office grosses by theater, DMA, and international markets. Includes screening counts and per-screen averages.",
                "forecasting": "Our predictive models incorporate social media buzz, critic reviews, and comparable film performance for release weekend forecasts."
            },
            "active": True
        },
        {
            "vendor_email": "info@gamelytics.gg",
            "name": "GameLytics Bot",
            "description": "AI assistant for gaming industry data, player metrics, and esports analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "Gaming data from Steam, Epic, PlayStation Network, Xbox Live, and mobile app stores. Player telemetry from partner game studios.",
                "usage_guidelines": "Designed for game developers, publishers, and esports organizations optimizing game design, monetization, and competitive balance.",
                "data_types": "Includes player progression, in-game economy, matchmaking data, and esports tournament results.",
                "privacy": "All player data aggregated and anonymized. No individual player profiles or personally identifiable information."
            },
            "active": True
        },
        {
            "vendor_email": "contact@socialdata.ai",
            "name": "SocialData Agent",
            "description": "AI assistant for social media analytics, influencer metrics, and engagement data",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "Social media data collected via official APIs and public data. Compliant with platform terms of service and data protection regulations.",
                "usage_guidelines": "Ideal for brands, agencies, and influencer marketing platforms measuring campaign effectiveness and audience sentiment.",
                "platforms": "Coverage includes Instagram, TikTok, YouTube, Twitter/X, and Facebook across 100M+ influencers and creators.",
                "analytics": "Provides engagement rates, audience demographics, brand affinity scores, and influencer authenticity metrics."
            },
            "active": True
        },
        
        # SPORTS DOMAIN
        {
            "vendor_email": "data@sportstats.pro",
            "name": "SportStats Assistant",
            "description": "AI assistant for professional sports statistics, game results, and player performance data",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "Official statistics from NFL, NBA, MLB, NHL, MLS, and major international leagues. Licensed directly from leagues and governing bodies.",
                "usage_guidelines": "Perfect for sports media, fantasy sports platforms, and sports betting operators requiring authoritative play-by-play data.",
                "data_depth": "Includes advanced metrics like player tracking data, expected goals (xG), win probability, and player impact estimates.",
                "licensing": "Commercial use requires league-approved licensing. Non-commercial/personal use allowed under standard subscription."
            },
            "active": True
        },
        {
            "vendor_email": "sales@oddsdata.io",
            "name": "OddsData Agent",
            "description": "AI assistant for sports betting odds, line movements, and wagering market analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "Odds data from 200+ sportsbooks worldwide updated in real-time. Historical line movement data for modeling market efficiency.",
                "usage_guidelines": "Essential for sports bettors, sportsbook operators, and quant traders developing betting strategies and risk management systems.",
                "data_features": "Includes opening lines, closing lines, line steam alerts, sharp money indicators, and implied probability calculations.",
                "compliance": "Users must comply with local gambling regulations. Data provided for analytical purposes only."
            },
            "active": True
        },
        {
            "vendor_email": "info@athletemetrics.com",
            "name": "AthleteMetrics Advisor",
            "description": "AI assistant for athlete performance data, biometrics, and training analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "Wearable and performance data from professional athletes (with consent) and sports science research. Fully anonymized for privacy.",
                "usage_guidelines": "Designed for sports teams, performance coaches, and sports medicine professionals optimizing training and injury prevention.",
                "metrics": "GPS tracking, heart rate variability, training load, sleep quality, nutrition, and recovery metrics with ML-based injury risk models.",
                "research": "Aggregate data available for sports science research. Individual athlete data restricted to team use only."
            },
            "active": True
        },
        {
            "vendor_email": "contact@leagueinsights.net",
            "name": "LeagueInsights Bot",
            "description": "AI assistant for sports business data, franchise valuations, and league economics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "Business intelligence from league filings, media reports, and proprietary valuations. Covers franchise values, TV deals, and sponsorship rates.",
                "usage_guidelines": "Ideal for sports investment firms, leagues, and teams analyzing franchise valuations, media rights, and business strategy.",
                "data_sources": "Financial data from Forbes, public filings, media rights deals, attendance records, and luxury tax/salary cap information.",
                "insights": "Includes revenue projections, competitive balance metrics, and market opportunity assessments for expansion and relocation decisions."
            },
            "active": True
        },
        
        # RETAIL DOMAIN
        {
            "vendor_email": "data@retailpulse.com",
            "name": "RetailPulse Assistant",
            "description": "AI assistant for point-of-sale data, retail transactions, and store performance analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "POS data from 50,000+ retail locations across grocery, apparel, electronics, and general merchandise. All customer data anonymized.",
                "usage_guidelines": "Essential for retailers, CPG brands, and market research firms analyzing sales trends, market share, and promotional effectiveness.",
                "data_granularity": "Transaction-level data with product UPC, price, quantity, store location, and timestamp. Weekly aggregations available for trend analysis.",
                "insights": "Includes basket analysis, price elasticity, competitive set performance, and same-store sales growth metrics."
            },
            "active": True
        },
        {
            "vendor_email": "sales@ecomanalytics.io",
            "name": "EcomAnalytics Agent",
            "description": "AI assistant for e-commerce data, online shopping behavior, and conversion analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "E-commerce data from 10,000+ online retailers and marketplaces. Session-level clickstream data with full customer journey tracking.",
                "usage_guidelines": "Perfect for e-commerce platforms, digital agencies, and brands optimizing conversion funnels, cart abandonment, and personalization.",
                "data_coverage": "Includes product views, add-to-cart events, checkout steps, payment methods, device types, and referral sources.",
                "analytics": "Provides conversion rate benchmarks, cart abandonment analysis, customer lifetime value predictions, and A/B test results."
            },
            "active": True
        },
        {
            "vendor_email": "info@loyaltymetrics.net",
            "name": "LoyaltyMetrics Advisor",
            "description": "AI assistant for customer loyalty programs, rewards data, and retention analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "Loyalty program data from 500+ brands across retail, hospitality, and services. Member behavior tracking from enrollment through redemption.",
                "usage_guidelines": "Designed for loyalty program managers, CRM teams, and customer analytics professionals measuring engagement and ROI.",
                "metrics": "Points earned/redeemed, tier progression, member engagement scores, program economics, and churn risk predictions.",
                "best_practices": "We provide benchmarking against industry standards and recommendations for reward structure optimization."
            },
            "active": True
        },
        {
            "vendor_email": "contact@inventoryintel.com",
            "name": "InventoryIntel Assistant",
            "description": "AI assistant for inventory management, supply chain data, and stock optimization analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "Real-time inventory data from warehouses, distribution centers, and retail stores. Includes stock levels, replenishment orders, and supplier performance.",
                "usage_guidelines": "Essential for supply chain managers, procurement teams, and logistics professionals optimizing inventory turns and reducing stockouts.",
                "data_coverage": "SKU-level inventory positions, demand forecasts, lead times, fill rates, and warehouse capacity utilization.",
                "forecasting": "ML-powered demand forecasting models considering seasonality, promotions, and market trends with 85%+ accuracy."
            },
            "active": True
        },
        
        # TECHNOLOGY DOMAIN
        {
            "vendor_email": "data@cloudmetrics.io",
            "name": "CloudMetrics Agent",
            "description": "AI assistant for cloud infrastructure data, resource utilization, and cost analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "Multi-cloud monitoring data from AWS, Azure, GCP, and Oracle Cloud. Real-time metrics with 5-minute granularity and historical data retention.",
                "usage_guidelines": "Ideal for DevOps teams, FinOps practitioners, and cloud architects optimizing resource utilization and controlling cloud costs.",
                "integrations": "Native integrations with CloudWatch, Azure Monitor, Google Cloud Operations, and custom metrics via StatsD/Prometheus.",
                "cost_optimization": "Automated rightsizing recommendations, reserved instance analysis, and commitment discount optimization."
            },
            "active": True
        },
        {
            "vendor_email": "info@devopsdata.com",
            "name": "DevOps Intelligence Bot",
            "description": "AI assistant for DevOps metrics, CI/CD pipelines, and software delivery analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "Deployment and pipeline data from Jenkins, GitHub Actions, GitLab CI, CircleCI, and Azure DevOps. Incident data from PagerDuty, Opsgenie.",
                "usage_guidelines": "Perfect for engineering leaders, SREs, and platform teams tracking DORA metrics and improving software delivery performance.",
                "metrics": "Deployment frequency, lead time for changes, MTTR, change failure rate, and custom KPIs aligned with business objectives.",
                "benchmarking": "Compare your team's performance against industry benchmarks (Elite/High/Medium/Low performers) and track improvement over time."
            },
            "active": True
        },
        {
            "vendor_email": "sales@apianalytics.net",
            "name": "API Analytics Assistant",
            "description": "AI assistant for API usage data, endpoint performance, and integration analytics",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "Comprehensive API analytics including request logs, response times, error rates, and consumer behavior. Supports REST, GraphQL, and gRPC.",
                "usage_guidelines": "Essential for API product managers, platform engineers, and developer relations teams optimizing API performance and adoption.",
                "monitoring": "Real-time alerting on latency spikes, error rate increases, and rate limit breaches. Historical trend analysis for capacity planning.",
                "developer_insights": "Track API consumer adoption, integration patterns, SDK usage, and developer onboarding friction points."
            },
            "active": True
        },
        {
            "vendor_email": "contact@usageinsights.com",
            "name": "SaaS Usage Bot",
            "description": "AI assistant for SaaS product analytics, feature adoption, and user engagement data",
            "model_used": "gemini-1.5-flash",
            "config": {
                "vendor_policy": "Product telemetry from SaaS applications tracking user behavior, feature usage, and engagement patterns. Privacy-first with anonymization.",
                "usage_guidelines": "Designed for product managers, growth teams, and customer success professionals optimizing product-market fit and reducing churn.",
                "analytics": "User activity logs, feature adoption funnels, cohort retention, NPS correlation with usage, and predictive churn models.",
                "integrations": "Works with Segment, Mixpanel, Amplitude, and custom event tracking. Supports product-led growth and expansion revenue strategies."
            },
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
        # ============ FINANCE DOMAIN - MarketPulse Data (Vendor 1) ============
        # RELATED DATASETS: Stock Prices + Company Financials (join on ticker)
        {
            "vendor_email": "admin@marketpulse.com",
            "title": "US Stock Market Daily Prices 2020-2024",
            "status": "active",
            "visibility": "public",
            "description": "Daily OHLCV data for all US-listed stocks including NYSE, NASDAQ, and AMEX exchanges",
            "domain": "Finance",
            "dataset_type": "Time-series",
            "granularity": "Daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["stocks", "equities", "NYSE", "NASDAQ", "trading"],
            "entities": ["stocks", "companies", "exchanges"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US"], "regions": ["North America"]},
            "columns": [
                {"name": "ticker", "description": "Stock ticker symbol", "data_type": "VARCHAR(10)", "sample_values": ["AAPL", "MSFT", "GOOGL"]},
                {"name": "trade_date", "description": "Trading date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-01-16"]},
                {"name": "open_price", "description": "Opening price in USD", "data_type": "DECIMAL(10,2)", "sample_values": [150.25, 151.30]},
                {"name": "high_price", "description": "Highest price of the day", "data_type": "DECIMAL(10,2)", "sample_values": [153.50, 154.20]},
                {"name": "low_price", "description": "Lowest price of the day", "data_type": "DECIMAL(10,2)", "sample_values": [149.80, 150.50]},
                {"name": "close_price", "description": "Closing price in USD", "data_type": "DECIMAL(10,2)", "sample_values": [152.10, 153.45]},
                {"name": "volume", "description": "Number of shares traded", "data_type": "BIGINT", "sample_values": [45000000, 42000000]},
                {"name": "adjusted_close", "description": "Split and dividend adjusted closing price", "data_type": "DECIMAL(10,2)", "sample_values": [152.10, 153.45]},
                {"name": "market_cap", "description": "Market capitalization in billions USD", "data_type": "DECIMAL(15,2)", "sample_values": [2500.50, 2520.30]},
                {"name": "exchange", "description": "Stock exchange code", "data_type": "VARCHAR(10)", "sample_values": ["NYSE", "NASDAQ"]},
            ]
        },
        {
            "vendor_email": "admin@marketpulse.com",
            "title": "Company Financial Statements Q1 2020 - Q4 2024",
            "status": "active",
            "visibility": "public",
            "description": "Quarterly and annual financial statements including income statement, balance sheet, and cash flow",
            "domain": "Finance",
            "dataset_type": "Financial",
            "granularity": "Quarterly",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["financials", "earnings", "balance sheet", "cash flow", "fundamentals"],
            "entities": ["companies", "financial reports"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Quarterly"},
            "geographic_coverage": {"countries": ["US"], "regions": ["North America"]},
            "columns": [
                {"name": "ticker", "description": "Stock ticker symbol", "data_type": "VARCHAR(10)", "sample_values": ["AAPL", "MSFT", "GOOGL"]},
                {"name": "fiscal_period", "description": "Fiscal quarter or year", "data_type": "VARCHAR(10)", "sample_values": ["Q1-2024", "Q2-2024", "FY-2023"]},
                {"name": "report_date", "description": "Financial report filing date", "data_type": "DATE", "sample_values": ["2024-04-30", "2024-07-31"]},
                {"name": "revenue", "description": "Total revenue in millions USD", "data_type": "DECIMAL(15,2)", "sample_values": [94000.50, 95500.00]},
                {"name": "net_income", "description": "Net income in millions USD", "data_type": "DECIMAL(15,2)", "sample_values": [23500.00, 24000.00]},
                {"name": "total_assets", "description": "Total assets in millions USD", "data_type": "DECIMAL(15,2)", "sample_values": [350000.00, 355000.00]},
                {"name": "total_liabilities", "description": "Total liabilities in millions USD", "data_type": "DECIMAL(15,2)", "sample_values": [125000.00, 127000.00]},
                {"name": "eps", "description": "Earnings per share", "data_type": "DECIMAL(10,4)", "sample_values": [1.5234, 1.5567]},
                {"name": "pe_ratio", "description": "Price-to-earnings ratio", "data_type": "DECIMAL(8,2)", "sample_values": [28.5, 29.2]},
                {"name": "debt_to_equity", "description": "Debt to equity ratio", "data_type": "DECIMAL(6,2)", "sample_values": [0.85, 0.92]},
            ]
        },
        {
            "vendor_email": "admin@marketpulse.com",
            "title": "Stock Splits and Dividend History",
            "status": "active",
            "visibility": "public",
            "description": "Historical record of stock splits, dividends, and special distributions",
            "domain": "Finance",
            "dataset_type": "Event-based",
            "granularity": "Event-level",
            "pricing_model": "One-time Purchase",
            "license": "Commercial Use Allowed",
            "topics": ["dividends", "stock splits", "corporate actions"],
            "entities": ["stocks", "dividends"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US"], "regions": ["North America"]},
            "columns": [
                {"name": "ticker", "description": "Stock ticker symbol", "data_type": "VARCHAR(10)", "sample_values": ["AAPL", "MSFT", "GOOGL"]},
                {"name": "event_type", "description": "Type of corporate action", "data_type": "VARCHAR(20)", "sample_values": ["dividend", "split", "special_dividend"]},
                {"name": "event_date", "description": "Date of the corporate action", "data_type": "DATE", "sample_values": ["2024-02-15", "2024-05-10"]},
                {"name": "ex_date", "description": "Ex-dividend or ex-split date", "data_type": "DATE", "sample_values": ["2024-02-10", "2024-05-05"]},
                {"name": "payment_date", "description": "Payment date for dividends", "data_type": "DATE", "sample_values": ["2024-03-01", None]},
                {"name": "dividend_amount", "description": "Dividend per share in USD", "data_type": "DECIMAL(6,4)", "sample_values": [0.2400, 0.2500, None]},
                {"name": "split_ratio", "description": "Stock split ratio", "data_type": "VARCHAR(10)", "sample_values": ["2:1", "3:2", None]},
                {"name": "yield_percentage", "description": "Dividend yield percentage", "data_type": "DECIMAL(5,2)", "sample_values": [1.85, 2.10]},
                {"name": "announcement_date", "description": "Corporate action announcement date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-04-20"]},
            ]
        },
        {
            "vendor_email": "admin@marketpulse.com",
            "title": "Insider Trading SEC Form 4 Filings",
            "status": "active",
            "visibility": "public",
            "description": "SEC Form 4 insider trading transactions for public company officers and directors",
            "domain": "Finance",
            "dataset_type": "Transactional",
            "granularity": "Transaction-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["insider trading", "SEC filings", "corporate governance"],
            "entities": ["executives", "insiders", "transactions"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Real-time"},
            "geographic_coverage": {"countries": ["US"], "regions": ["North America"]},
            "columns": [
                {"name": "ticker", "description": "Stock ticker symbol", "data_type": "VARCHAR(10)", "sample_values": ["AAPL", "MSFT", "GOOGL"]},
                {"name": "transaction_date", "description": "Date of insider transaction", "data_type": "DATE", "sample_values": ["2024-01-20", "2024-02-15"]},
                {"name": "filing_date", "description": "SEC Form 4 filing date", "data_type": "DATE", "sample_values": ["2024-01-22", "2024-02-17"]},
                {"name": "insider_name", "description": "Name of insider", "data_type": "VARCHAR(100)", "sample_values": ["John Smith", "Jane Doe"]},
                {"name": "insider_title", "description": "Title or position of insider", "data_type": "VARCHAR(100)", "sample_values": ["CEO", "CFO", "Director"]},
                {"name": "transaction_type", "description": "Type of transaction", "data_type": "VARCHAR(20)", "sample_values": ["Purchase", "Sale", "Option Exercise"]},
                {"name": "shares", "description": "Number of shares traded", "data_type": "INTEGER", "sample_values": [50000, 25000]},
                {"name": "price_per_share", "description": "Transaction price per share", "data_type": "DECIMAL(10,2)", "sample_values": [150.25, 148.50]},
                {"name": "total_value", "description": "Total transaction value in USD", "data_type": "DECIMAL(15,2)", "sample_values": [7512500.00, 3712500.00]},
                {"name": "shares_owned_after", "description": "Shares owned after transaction", "data_type": "INTEGER", "sample_values": [250000, 175000]},
            ]
        },
        {
            "vendor_email": "admin@marketpulse.com",
            "title": "Market Indices and ETF Performance",
            "status": "active",
            "visibility": "public",
            "description": "Daily performance data for major market indices and ETFs including composition and sector weights",
            "domain": "Finance",
            "dataset_type": "Time-series",
            "granularity": "Daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["indices", "ETFs", "benchmarks", "market performance"],
            "entities": ["indices", "ETFs", "sectors"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["North America", "Worldwide"]},
            "columns": [
                {"name": "symbol", "description": "Index or ETF ticker symbol", "data_type": "VARCHAR(10)", "sample_values": ["SPY", "QQQ", "^GSPC"]},
                {"name": "trade_date", "description": "Trading date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-01-16"]},
                {"name": "open_value", "description": "Opening value or price", "data_type": "DECIMAL(10,2)", "sample_values": [4500.25, 4520.30]},
                {"name": "close_value", "description": "Closing value or price", "data_type": "DECIMAL(10,2)", "sample_values": [4515.80, 4530.50]},
                {"name": "daily_return", "description": "Daily return percentage", "data_type": "DECIMAL(6,3)", "sample_values": [0.345, -0.125]},
                {"name": "ytd_return", "description": "Year-to-date return percentage", "data_type": "DECIMAL(6,2)", "sample_values": [12.50, 15.30]},
                {"name": "volume", "description": "Trading volume", "data_type": "BIGINT", "sample_values": [85000000, 82000000]},
                {"name": "vix_level", "description": "VIX volatility index level if applicable", "data_type": "DECIMAL(6,2)", "sample_values": [15.50, 16.20]},
                {"name": "dividend_yield", "description": "Current dividend yield percentage", "data_type": "DECIMAL(5,2)", "sample_values": [1.75, 1.82]},
                {"name": "pe_ratio", "description": "Price-to-earnings ratio for index", "data_type": "DECIMAL(8,2)", "sample_values": [22.5, 23.1]},
            ]
        },
        
        # ============ FINANCE DOMAIN - CryptoStream Analytics (Vendor 2) ============
        # RELATED DATASETS: Crypto Prices + Exchange Volumes (join on coin_symbol)
        {
            "vendor_email": "contact@cryptostream.io",
            "title": "Cryptocurrency Real-Time Price Feed",
            "status": "active",
            "visibility": "public",
            "description": "Minute-by-minute cryptocurrency price data for top 500 coins across major exchanges",
            "domain": "Finance",
            "dataset_type": "Time-series",
            "granularity": "Minute-level",
            "pricing_model": "Usage-based",
            "license": "Commercial Use Allowed",
            "topics": ["cryptocurrency", "bitcoin", "ethereum", "altcoins", "trading"],
            "entities": ["cryptocurrencies", "exchanges", "tokens"],
            "temporal_coverage": {"start_date": "2023-01-01", "end_date": "2024-12-31", "frequency": "Minute"},
            "geographic_coverage": {"countries": ["Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "coin_symbol", "description": "Cryptocurrency ticker symbol", "data_type": "VARCHAR(10)", "sample_values": ["BTC", "ETH", "SOL"]},
                {"name": "timestamp", "description": "Price timestamp in UTC", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 10:00:00", "2024-01-15 10:01:00"]},
                {"name": "price_usd", "description": "Price in USD", "data_type": "DECIMAL(18,8)", "sample_values": [45000.50123456, 3200.75234567]},
                {"name": "price_btc", "description": "Price in Bitcoin", "data_type": "DECIMAL(18,8)", "sample_values": [1.00000000, 0.07112345]},
                {"name": "volume_1h", "description": "1-hour trading volume in USD", "data_type": "DECIMAL(20,2)", "sample_values": [5000000000.00, 1200000000.00]},
                {"name": "market_cap_usd", "description": "Market capitalization in USD", "data_type": "DECIMAL(20,2)", "sample_values": [850000000000.00, 380000000000.00]},
                {"name": "percent_change_1h", "description": "Price change percentage in last hour", "data_type": "DECIMAL(6,3)", "sample_values": [0.523, -0.345]},
                {"name": "percent_change_24h", "description": "Price change percentage in last 24 hours", "data_type": "DECIMAL(6,3)", "sample_values": [2.145, -1.234]},
                {"name": "circulating_supply", "description": "Circulating supply of the coin", "data_type": "DECIMAL(20,2)", "sample_values": [19000000.00, 120000000.00]},
                {"name": "total_supply", "description": "Total maximum supply", "data_type": "DECIMAL(20,2)", "sample_values": [21000000.00, None]},
            ]
        },
        {
            "vendor_email": "contact@cryptostream.io",
            "title": "Cryptocurrency Exchange Volume Rankings",
            "status": "active",
            "visibility": "public",
            "description": "Daily trading volumes and liquidity metrics across cryptocurrency exchanges",
            "domain": "Finance",
            "dataset_type": "Time-series",
            "granularity": "Daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["exchanges", "trading volume", "liquidity", "market depth"],
            "entities": ["exchanges", "trading pairs", "cryptocurrencies"],
            "temporal_coverage": {"start_date": "2023-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "coin_symbol", "description": "Cryptocurrency ticker symbol", "data_type": "VARCHAR(10)", "sample_values": ["BTC", "ETH", "SOL"]},
                {"name": "exchange_name", "description": "Name of cryptocurrency exchange", "data_type": "VARCHAR(50)", "sample_values": ["Binance", "Coinbase", "Kraken"]},
                {"name": "trade_date", "description": "Trading date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-01-16"]},
                {"name": "volume_24h_usd", "description": "24-hour trading volume in USD", "data_type": "DECIMAL(20,2)", "sample_values": [25000000000.00, 8000000000.00]},
                {"name": "volume_24h_btc", "description": "24-hour trading volume in BTC", "data_type": "DECIMAL(18,8)", "sample_values": [555555.12345678, 177777.87654321]},
                {"name": "bid_ask_spread", "description": "Average bid-ask spread percentage", "data_type": "DECIMAL(6,4)", "sample_values": [0.0523, 0.0845]},
                {"name": "market_share", "description": "Exchange market share percentage", "data_type": "DECIMAL(5,2)", "sample_values": [32.50, 15.30]},
                {"name": "number_of_trades", "description": "Number of trades executed", "data_type": "BIGINT", "sample_values": [5000000, 2000000]},
                {"name": "average_trade_size", "description": "Average trade size in USD", "data_type": "DECIMAL(15,2)", "sample_values": [5000.00, 4000.00]},
                {"name": "liquidity_score", "description": "Liquidity score (0-100)", "data_type": "INTEGER", "sample_values": [95, 88]},
            ]
        },
        {
            "vendor_email": "contact@cryptostream.io",
            "title": "Blockchain Network Metrics",
            "status": "active",
            "visibility": "public",
            "description": "On-chain metrics including transaction counts, fees, active addresses, and hash rates",
            "domain": "Finance",
            "dataset_type": "Time-series",
            "granularity": "Hourly",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["blockchain", "on-chain data", "network metrics", "mining"],
            "entities": ["blockchains", "transactions", "addresses"],
            "temporal_coverage": {"start_date": "2023-01-01", "end_date": "2024-12-31", "frequency": "Hourly"},
            "geographic_coverage": {"countries": ["Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "coin_symbol", "description": "Cryptocurrency blockchain symbol", "data_type": "VARCHAR(10)", "sample_values": ["BTC", "ETH", "SOL"]},
                {"name": "timestamp", "description": "Metric timestamp in UTC", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 10:00:00", "2024-01-15 11:00:00"]},
                {"name": "transaction_count", "description": "Number of transactions in the hour", "data_type": "INTEGER", "sample_values": [25000, 180000]},
                {"name": "active_addresses", "description": "Number of unique active addresses", "data_type": "INTEGER", "sample_values": [850000, 450000]},
                {"name": "average_tx_fee_usd", "description": "Average transaction fee in USD", "data_type": "DECIMAL(10,6)", "sample_values": [2.500000, 0.350000]},
                {"name": "hash_rate", "description": "Network hash rate", "data_type": "DECIMAL(20,2)", "sample_values": [350000000.00, 850000.00]},
                {"name": "block_time_seconds", "description": "Average block time in seconds", "data_type": "DECIMAL(6,2)", "sample_values": [600.00, 13.50]},
                {"name": "difficulty", "description": "Mining difficulty", "data_type": "DECIMAL(25,2)", "sample_values": [40000000000000.00, 12000000000.00]},
                {"name": "total_value_locked", "description": "Total value locked in DeFi protocols in USD", "data_type": "DECIMAL(20,2)", "sample_values": [45000000000.00, 38000000000.00]},
            ]
        },
        {
            "vendor_email": "contact@cryptostream.io",
            "title": "DeFi Protocol Analytics",
            "status": "active",
            "visibility": "public",
            "description": "Decentralized finance protocol metrics including TVL, yields, and user activity",
            "domain": "Finance",
            "dataset_type": "Time-series",
            "granularity": "Daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["DeFi", "decentralized finance", "yield farming", "lending"],
            "entities": ["protocols", "smart contracts", "liquidity pools"],
            "temporal_coverage": {"start_date": "2023-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "protocol_name", "description": "Name of DeFi protocol", "data_type": "VARCHAR(50)", "sample_values": ["Uniswap", "Aave", "Compound"]},
                {"name": "blockchain", "description": "Underlying blockchain", "data_type": "VARCHAR(20)", "sample_values": ["Ethereum", "Polygon", "Arbitrum"]},
                {"name": "trade_date", "description": "Date of metrics", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-01-16"]},
                {"name": "tvl_usd", "description": "Total value locked in USD", "data_type": "DECIMAL(20,2)", "sample_values": [5000000000.00, 3000000000.00]},
                {"name": "daily_volume_usd", "description": "Daily trading/lending volume in USD", "data_type": "DECIMAL(20,2)", "sample_values": [2000000000.00, 500000000.00]},
                {"name": "unique_users", "description": "Number of unique addresses interacting", "data_type": "INTEGER", "sample_values": [50000, 25000]},
                {"name": "apy_average", "description": "Average APY percentage across pools", "data_type": "DECIMAL(6,2)", "sample_values": [12.50, 8.75]},
                {"name": "transaction_count", "description": "Number of protocol transactions", "data_type": "INTEGER", "sample_values": [150000, 75000]},
                {"name": "protocol_revenue", "description": "Protocol fees collected in USD", "data_type": "DECIMAL(15,2)", "sample_values": [500000.00, 250000.00]},
                {"name": "market_dominance", "description": "Protocol market share percentage", "data_type": "DECIMAL(5,2)", "sample_values": [25.50, 15.30]},
            ]
        },
        {
            "vendor_email": "contact@cryptostream.io",
            "title": "NFT Market Data and Sales",
            "status": "active",
            "visibility": "public",
            "description": "Non-fungible token sales, floor prices, and collection statistics",
            "domain": "Finance",
            "dataset_type": "Transactional",
            "granularity": "Transaction-level",
            "pricing_model": "Usage-based",
            "license": "Commercial Use Allowed",
            "topics": ["NFT", "digital collectibles", "art", "gaming"],
            "entities": ["collections", "tokens", "marketplaces"],
            "temporal_coverage": {"start_date": "2023-01-01", "end_date": "2024-12-31", "frequency": "Real-time"},
            "geographic_coverage": {"countries": ["Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "collection_name", "description": "NFT collection name", "data_type": "VARCHAR(100)", "sample_values": ["CryptoPunks", "Bored Ape Yacht Club", "Azuki"]},
                {"name": "token_id", "description": "Unique token identifier within collection", "data_type": "VARCHAR(50)", "sample_values": ["1234", "5678", "9012"]},
                {"name": "sale_timestamp", "description": "Timestamp of NFT sale", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 10:30:00", "2024-01-15 14:20:00"]},
                {"name": "sale_price_eth", "description": "Sale price in ETH", "data_type": "DECIMAL(18,8)", "sample_values": [50.50000000, 25.75000000]},
                {"name": "sale_price_usd", "description": "Sale price in USD at time of sale", "data_type": "DECIMAL(15,2)", "sample_values": [150000.00, 75000.00]},
                {"name": "marketplace", "description": "NFT marketplace where sold", "data_type": "VARCHAR(50)", "sample_values": ["OpenSea", "Blur", "LooksRare"]},
                {"name": "seller_address", "description": "Anonymized seller wallet address", "data_type": "VARCHAR(42)", "sample_values": ["0x1234...5678", "0xabcd...efgh"]},
                {"name": "buyer_address", "description": "Anonymized buyer wallet address", "data_type": "VARCHAR(42)", "sample_values": ["0x9876...5432", "0xfedc...ba98"]},
                {"name": "floor_price_eth", "description": "Collection floor price in ETH at time of sale", "data_type": "DECIMAL(18,8)", "sample_values": [45.00000000, 20.00000000]},
                {"name": "rarity_rank", "description": "Token rarity rank within collection", "data_type": "INTEGER", "sample_values": [123, 4567]},
            ]
        },
        {
            "vendor_email": "contact@cryptostream.io",
            "title": "Crypto Whale Wallet Tracking",
            "status": "active",
            "visibility": "public",
            "description": "Large wallet movements and holdings for major cryptocurrencies",
            "domain": "Finance",
            "dataset_type": "Transactional",
            "granularity": "Transaction-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["whale tracking", "large holders", "wallet analysis"],
            "entities": ["wallets", "addresses", "transactions"],
            "temporal_coverage": {"start_date": "2023-01-01", "end_date": "2024-12-31", "frequency": "Real-time"},
            "geographic_coverage": {"countries": ["Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "wallet_address", "description": "Anonymized wallet address", "data_type": "VARCHAR(42)", "sample_values": ["0x1234...5678", "0xabcd...efgh"]},
                {"name": "coin_symbol", "description": "Cryptocurrency symbol", "data_type": "VARCHAR(10)", "sample_values": ["BTC", "ETH", "USDT"]},
                {"name": "transaction_timestamp", "description": "Timestamp of transaction", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 10:30:00", "2024-01-15 14:20:00"]},
                {"name": "transaction_type", "description": "Type of transaction", "data_type": "VARCHAR(20)", "sample_values": ["transfer", "deposit", "withdrawal"]},
                {"name": "amount", "description": "Amount of cryptocurrency moved", "data_type": "DECIMAL(20,8)", "sample_values": [1000.50000000, 5000.25000000]},
                {"name": "amount_usd", "description": "Transaction amount in USD", "data_type": "DECIMAL(20,2)", "sample_values": [45000000.00, 225000000.00]},
                {"name": "from_address", "description": "Source wallet address", "data_type": "VARCHAR(42)", "sample_values": ["0x1234...5678", "0xabcd...efgh"]},
                {"name": "to_address", "description": "Destination wallet address", "data_type": "VARCHAR(42)", "sample_values": ["0x9876...5432", "0xfedc...ba98"]},
                {"name": "wallet_balance_after", "description": "Wallet balance after transaction", "data_type": "DECIMAL(20,8)", "sample_values": [5000.50000000, 25000.75000000]},
                {"name": "wallet_usd_value", "description": "Total wallet value in USD", "data_type": "DECIMAL(20,2)", "sample_values": [225000000.00, 1125000000.00]},
            ]
        },
        
        # ============ FINANCE DOMAIN - QuantEdge Financial Data (Vendor 3) ============
        # RELATED DATASETS: Options Prices + Derivatives Positions (join on underlying_ticker)
        {
            "vendor_email": "info@quantedge.co.uk",
            "title": "Options and Derivatives Market Data",
            "status": "active",
            "visibility": "public",
            "description": "Comprehensive options chain data including Greeks, implied volatility, and open interest",
            "domain": "Finance",
            "dataset_type": "Time-series",
            "granularity": "Real-time",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["options", "derivatives", "volatility", "hedging"],
            "entities": ["options", "contracts", "underlying stocks"],
            "temporal_coverage": {"start_date": "2023-01-01", "end_date": "2024-12-31", "frequency": "Real-time"},
            "geographic_coverage": {"countries": ["US", "UK", "EU"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "underlying_ticker", "description": "Underlying stock ticker symbol", "data_type": "VARCHAR(10)", "sample_values": ["AAPL", "MSFT", "TSLA"]},
                {"name": "contract_symbol", "description": "Options contract identifier", "data_type": "VARCHAR(30)", "sample_values": ["AAPL250117C00150000", "MSFT250117P00350000"]},
                {"name": "quote_timestamp", "description": "Quote timestamp in UTC", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-01-15 14:31:00"]},
                {"name": "option_type", "description": "Call or Put option", "data_type": "VARCHAR(4)", "sample_values": ["CALL", "PUT"]},
                {"name": "strike_price", "description": "Option strike price", "data_type": "DECIMAL(10,2)", "sample_values": [150.00, 350.00]},
                {"name": "expiration_date", "description": "Option expiration date", "data_type": "DATE", "sample_values": ["2025-01-17", "2025-03-21"]},
                {"name": "bid_price", "description": "Bid price for option contract", "data_type": "DECIMAL(8,2)", "sample_values": [5.50, 8.25]},
                {"name": "ask_price", "description": "Ask price for option contract", "data_type": "DECIMAL(8,2)", "sample_values": [5.55, 8.30]},
                {"name": "implied_volatility", "description": "Implied volatility percentage", "data_type": "DECIMAL(6,2)", "sample_values": [28.50, 32.75]},
                {"name": "delta", "description": "Option delta Greek", "data_type": "DECIMAL(6,4)", "sample_values": [0.5234, -0.4521]},
                {"name": "gamma", "description": "Option gamma Greek", "data_type": "DECIMAL(8,6)", "sample_values": [0.012345, 0.008765]},
                {"name": "theta", "description": "Option theta Greek", "data_type": "DECIMAL(8,4)", "sample_values": [-0.0523, -0.0789]},
                {"name": "vega", "description": "Option vega Greek", "data_type": "DECIMAL(8,4)", "sample_values": [0.1234, 0.0987]},
                {"name": "open_interest", "description": "Number of outstanding contracts", "data_type": "INTEGER", "sample_values": [50000, 25000]},
            ]
        },
        {
            "vendor_email": "info@quantedge.co.uk",
            "title": "Institutional Derivatives Positions",
            "status": "active",
            "visibility": "public",
            "description": "Aggregated institutional holdings and positioning data for derivatives instruments",
            "domain": "Finance",
            "dataset_type": "Time-series",
            "granularity": "Daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["institutional", "positioning", "derivatives", "futures"],
            "entities": ["institutions", "positions", "contracts"],
            "temporal_coverage": {"start_date": "2023-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "UK", "EU"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "underlying_ticker", "description": "Underlying asset ticker", "data_type": "VARCHAR(10)", "sample_values": ["AAPL", "MSFT", "TSLA"]},
                {"name": "report_date", "description": "Position report date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-01-16"]},
                {"name": "institution_type", "description": "Type of institution", "data_type": "VARCHAR(30)", "sample_values": ["Hedge Fund", "Bank", "Pension Fund"]},
                {"name": "long_positions", "description": "Number of long contracts held", "data_type": "INTEGER", "sample_values": [500000, 250000]},
                {"name": "short_positions", "description": "Number of short contracts held", "data_type": "INTEGER", "sample_values": [200000, 100000]},
                {"name": "net_position", "description": "Net long or short position", "data_type": "INTEGER", "sample_values": [300000, 150000]},
                {"name": "notional_value_usd", "description": "Total notional value in USD", "data_type": "DECIMAL(20,2)", "sample_values": [45000000000.00, 22500000000.00]},
                {"name": "position_change_pct", "description": "Daily position change percentage", "data_type": "DECIMAL(6,2)", "sample_values": [5.25, -3.15]},
                {"name": "concentration_pct", "description": "Position as percentage of open interest", "data_type": "DECIMAL(5,2)", "sample_values": [12.50, 8.30]},
            ]
        },
        {
            "vendor_email": "info@quantedge.co.uk",
            "title": "Credit Default Swap (CDS) Spreads",
            "status": "active",
            "visibility": "public",
            "description": "Corporate and sovereign CDS spreads with credit ratings and default probabilities",
            "domain": "Finance",
            "dataset_type": "Time-series",
            "granularity": "Daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["credit risk", "CDS", "spreads", "default risk"],
            "entities": ["corporations", "sovereigns", "bonds"],
            "temporal_coverage": {"start_date": "2023-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "UK", "EU", "JP"], "regions": ["North America", "Europe", "Asia"]},
            "columns": [
                {"name": "entity_name", "description": "Name of corporate or sovereign entity", "data_type": "VARCHAR(100)", "sample_values": ["Apple Inc", "Microsoft Corp", "United States"]},
                {"name": "entity_type", "description": "Corporate or Sovereign", "data_type": "VARCHAR(20)", "sample_values": ["Corporate", "Sovereign"]},
                {"name": "trade_date", "description": "Trading date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-01-16"]},
                {"name": "tenor", "description": "CDS tenor in years", "data_type": "VARCHAR(10)", "sample_values": ["1Y", "5Y", "10Y"]},
                {"name": "cds_spread_bps", "description": "CDS spread in basis points", "data_type": "DECIMAL(8,2)", "sample_values": [45.50, 125.75]},
                {"name": "credit_rating", "description": "Credit rating", "data_type": "VARCHAR(10)", "sample_values": ["AAA", "AA+", "BBB-"]},
                {"name": "probability_of_default", "description": "Implied probability of default percentage", "data_type": "DECIMAL(6,4)", "sample_values": [0.7500, 2.1500]},
                {"name": "recovery_rate", "description": "Expected recovery rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [40.00, 35.00]},
                {"name": "spread_change_bps", "description": "Daily spread change in basis points", "data_type": "DECIMAL(6,2)", "sample_values": [2.50, -1.75]},
            ]
        },
        {
            "vendor_email": "info@quantedge.co.uk",
            "title": "Fixed Income Bond Prices and Yields",
            "status": "active",
            "visibility": "public",
            "description": "Government and corporate bond prices, yields, and duration metrics",
            "domain": "Finance",
            "dataset_type": "Time-series",
            "granularity": "Daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["bonds", "fixed income", "yields", "treasuries"],
            "entities": ["bonds", "issuers", "securities"],
            "temporal_coverage": {"start_date": "2023-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "UK", "DE", "JP"], "regions": ["North America", "Europe", "Asia"]},
            "columns": [
                {"name": "isin", "description": "International Securities Identification Number", "data_type": "VARCHAR(12)", "sample_values": ["US912828XG75", "GB00B1VWPC84"]},
                {"name": "issuer_name", "description": "Bond issuer name", "data_type": "VARCHAR(100)", "sample_values": ["US Treasury", "Apple Inc", "UK Gilt"]},
                {"name": "trade_date", "description": "Trading date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-01-16"]},
                {"name": "coupon_rate", "description": "Annual coupon rate percentage", "data_type": "DECIMAL(6,3)", "sample_values": [3.750, 2.500]},
                {"name": "maturity_date", "description": "Bond maturity date", "data_type": "DATE", "sample_values": ["2034-02-15", "2030-05-15"]},
                {"name": "clean_price", "description": "Clean price as percentage of par", "data_type": "DECIMAL(8,4)", "sample_values": [98.7500, 101.2500]},
                {"name": "yield_to_maturity", "description": "Yield to maturity percentage", "data_type": "DECIMAL(6,3)", "sample_values": [4.125, 3.875]},
                {"name": "duration", "description": "Modified duration in years", "data_type": "DECIMAL(6,2)", "sample_values": [8.50, 6.25]},
                {"name": "convexity", "description": "Bond convexity", "data_type": "DECIMAL(8,2)", "sample_values": [85.50, 62.30]},
                {"name": "credit_rating", "description": "Bond credit rating", "data_type": "VARCHAR(10)", "sample_values": ["AAA", "AA+", "A-"]},
            ]
        },
        {
            "vendor_email": "info@quantedge.co.uk",
            "title": "Interest Rate Swap Curves",
            "status": "active",
            "visibility": "public",
            "description": "Interest rate swap curves and forward rates for major currencies",
            "domain": "Finance",
            "dataset_type": "Time-series",
            "granularity": "Daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["interest rates", "swaps", "yield curve", "forward rates"],
            "entities": ["currencies", "swap rates", "tenors"],
            "temporal_coverage": {"start_date": "2023-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "UK", "EU", "JP"], "regions": ["North America", "Europe", "Asia"]},
            "columns": [
                {"name": "currency", "description": "Currency code", "data_type": "VARCHAR(3)", "sample_values": ["USD", "EUR", "GBP"]},
                {"name": "trade_date", "description": "Trading date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-01-16"]},
                {"name": "tenor", "description": "Swap tenor", "data_type": "VARCHAR(10)", "sample_values": ["1Y", "5Y", "10Y", "30Y"]},
                {"name": "swap_rate", "description": "Interest rate swap rate percentage", "data_type": "DECIMAL(6,4)", "sample_values": [4.7500, 4.1250]},
                {"name": "spot_rate", "description": "Spot interest rate percentage", "data_type": "DECIMAL(6,4)", "sample_values": [4.5000, 3.8750]},
                {"name": "forward_rate", "description": "Forward interest rate percentage", "data_type": "DECIMAL(6,4)", "sample_values": [4.8750, 4.2500]},
                {"name": "discount_factor", "description": "Discount factor for tenor", "data_type": "DECIMAL(10,8)", "sample_values": [0.95234567, 0.67891234]},
                {"name": "spread_to_treasury", "description": "Spread to government bond in basis points", "data_type": "DECIMAL(6,2)", "sample_values": [85.50, 72.30]},
                {"name": "daily_change_bps", "description": "Daily rate change in basis points", "data_type": "DECIMAL(6,2)", "sample_values": [5.50, -3.25]},
            ]
        },
        
        # ============ FINANCE DOMAIN - FX Global Markets (Vendor 4) ============
        # RELATED DATASETS: FX Spot Rates + Trade Flows (join on currency_pair)
        {
            "vendor_email": "support@fxglobal.com",
            "title": "Foreign Exchange Spot and Forward Rates",
            "status": "active",
            "visibility": "public",
            "description": "Real-time and historical FX spot rates, forward points, and cross rates for 150+ currency pairs",
            "domain": "Finance",
            "dataset_type": "Time-series",
            "granularity": "Minute-level",
            "pricing_model": "Usage-based",
            "license": "Commercial Use Allowed",
            "topics": ["forex", "FX", "currency", "exchange rates"],
            "entities": ["currencies", "currency pairs", "rates"],
            "temporal_coverage": {"start_date": "2023-01-01", "end_date": "2024-12-31", "frequency": "Minute"},
            "geographic_coverage": {"countries": ["Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "currency_pair", "description": "Currency pair code", "data_type": "VARCHAR(7)", "sample_values": ["EUR/USD", "GBP/USD", "USD/JPY"]},
                {"name": "quote_timestamp", "description": "Quote timestamp in UTC", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 10:00:00", "2024-01-15 10:01:00"]},
                {"name": "bid_rate", "description": "Bid exchange rate", "data_type": "DECIMAL(12,6)", "sample_values": [1.085234, 1.264567]},
                {"name": "ask_rate", "description": "Ask exchange rate", "data_type": "DECIMAL(12,6)", "sample_values": [1.085245, 1.264578]},
                {"name": "mid_rate", "description": "Mid exchange rate", "data_type": "DECIMAL(12,6)", "sample_values": [1.085240, 1.264573]},
                {"name": "spread_pips", "description": "Bid-ask spread in pips", "data_type": "DECIMAL(6,2)", "sample_values": [1.10, 1.10]},
                {"name": "forward_1m", "description": "1-month forward points", "data_type": "DECIMAL(8,2)", "sample_values": [12.50, -8.30]},
                {"name": "forward_3m", "description": "3-month forward points", "data_type": "DECIMAL(8,2)", "sample_values": [38.75, -25.60]},
                {"name": "daily_volatility", "description": "Daily realized volatility percentage", "data_type": "DECIMAL(6,2)", "sample_values": [8.50, 12.30]},
                {"name": "trading_volume", "description": "Hourly trading volume in millions", "data_type": "DECIMAL(15,2)", "sample_values": [25000.00, 18000.00]},
            ]
        },
        {
            "vendor_email": "support@fxglobal.com",
            "title": "International Trade Flows and Balance of Payments",
            "status": "active",
            "visibility": "public",
            "description": "Bilateral trade data, trade balances, and balance of payments statistics by country",
            "domain": "Finance",
            "dataset_type": "Time-series",
            "granularity": "Monthly",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["trade", "imports", "exports", "balance of payments"],
            "entities": ["countries", "trade partners", "commodities"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Monthly"},
            "geographic_coverage": {"countries": ["Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "country_code", "description": "ISO 3166 country code", "data_type": "VARCHAR(3)", "sample_values": ["USA", "CHN", "DEU"]},
                {"name": "currency_pair", "description": "Primary currency pair", "data_type": "VARCHAR(7)", "sample_values": ["USD/CNY", "EUR/USD"]},
                {"name": "report_month", "description": "Trade data month", "data_type": "DATE", "sample_values": ["2024-01-01", "2024-02-01"]},
                {"name": "exports_usd", "description": "Total exports in USD millions", "data_type": "DECIMAL(15,2)", "sample_values": [250000.00, 180000.00]},
                {"name": "imports_usd", "description": "Total imports in USD millions", "data_type": "DECIMAL(15,2)", "sample_values": [280000.00, 160000.00]},
                {"name": "trade_balance_usd", "description": "Trade balance in USD millions", "data_type": "DECIMAL(15,2)", "sample_values": [-30000.00, 20000.00]},
                {"name": "current_account_usd", "description": "Current account balance in USD millions", "data_type": "DECIMAL(15,2)", "sample_values": [-45000.00, 35000.00]},
                {"name": "capital_account_usd", "description": "Capital account balance in USD millions", "data_type": "DECIMAL(15,2)", "sample_values": [50000.00, -30000.00]},
                {"name": "fx_reserves_usd", "description": "Foreign exchange reserves in USD millions", "data_type": "DECIMAL(15,2)", "sample_values": [3000000.00, 500000.00]},
                {"name": "trade_weighted_index", "description": "Trade-weighted currency index", "data_type": "DECIMAL(8,2)", "sample_values": [105.50, 98.30]},
            ]
        },
        {
            "vendor_email": "support@fxglobal.com",
            "title": "Central Bank Policy Rates and Announcements",
            "status": "active",
            "visibility": "public",
            "description": "Central bank policy interest rates, monetary policy decisions, and forward guidance",
            "domain": "Finance",
            "dataset_type": "Event-based",
            "granularity": "Event-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["central banks", "interest rates", "monetary policy"],
            "entities": ["central banks", "policy decisions", "rates"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "UK", "EU", "JP", "CA", "AU"], "regions": ["North America", "Europe", "Asia", "Oceania"]},
            "columns": [
                {"name": "central_bank", "description": "Central bank name", "data_type": "VARCHAR(50)", "sample_values": ["Federal Reserve", "ECB", "Bank of England"]},
                {"name": "currency", "description": "Currency code", "data_type": "VARCHAR(3)", "sample_values": ["USD", "EUR", "GBP"]},
                {"name": "announcement_date", "description": "Policy announcement date", "data_type": "DATE", "sample_values": ["2024-01-31", "2024-03-20"]},
                {"name": "decision_type", "description": "Type of policy decision", "data_type": "VARCHAR(30)", "sample_values": ["Rate Hike", "Rate Cut", "No Change"]},
                {"name": "policy_rate", "description": "New policy rate percentage", "data_type": "DECIMAL(6,3)", "sample_values": [5.250, 4.500]},
                {"name": "rate_change_bps", "description": "Rate change in basis points", "data_type": "DECIMAL(6,2)", "sample_values": [25.00, -50.00, 0.00]},
                {"name": "forward_guidance", "description": "Summary of forward guidance", "data_type": "VARCHAR(500)", "sample_values": ["Higher for longer", "Data dependent"]},
                {"name": "inflation_target", "description": "Stated inflation target percentage", "data_type": "DECIMAL(4,2)", "sample_values": [2.00, 2.00]},
                {"name": "gdp_forecast", "description": "GDP growth forecast percentage", "data_type": "DECIMAL(5,2)", "sample_values": [2.50, 1.80]},
                {"name": "next_meeting_date", "description": "Next scheduled policy meeting date", "data_type": "DATE", "sample_values": ["2024-03-20", "2024-05-01"]},
            ]
        },
        {
            "vendor_email": "support@fxglobal.com",
            "title": "Commodity Prices and Currency Correlations",
            "status": "active",
            "visibility": "public",
            "description": "Major commodity prices (oil, gold, metals) and correlations with currency movements",
            "domain": "Finance",
            "dataset_type": "Time-series",
            "granularity": "Daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["commodities", "oil", "gold", "metals", "correlations"],
            "entities": ["commodities", "currencies", "prices"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "commodity_name", "description": "Commodity name", "data_type": "VARCHAR(50)", "sample_values": ["WTI Crude Oil", "Gold", "Copper"]},
                {"name": "trade_date", "description": "Trading date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-01-16"]},
                {"name": "price_usd", "description": "Commodity price in USD", "data_type": "DECIMAL(10,2)", "sample_values": [75.50, 2050.25]},
                {"name": "daily_change_pct", "description": "Daily price change percentage", "data_type": "DECIMAL(6,2)", "sample_values": [2.50, -1.25]},
                {"name": "currency_impact", "description": "Most correlated currency pair", "data_type": "VARCHAR(7)", "sample_values": ["USD/CAD", "AUD/USD"]},
                {"name": "correlation_30d", "description": "30-day correlation coefficient", "data_type": "DECIMAL(5,4)", "sample_values": [0.7500, -0.6250]},
                {"name": "trading_volume", "description": "Daily trading volume in contracts", "data_type": "INTEGER", "sample_values": [500000, 250000]},
                {"name": "open_interest", "description": "Total open interest in contracts", "data_type": "INTEGER", "sample_values": [2000000, 1500000]},
                {"name": "volatility_30d", "description": "30-day realized volatility percentage", "data_type": "DECIMAL(6,2)", "sample_values": [25.50, 18.30]},
            ]
        },
        {
            "vendor_email": "support@fxglobal.com",
            "title": "Emerging Markets Currency and Sovereign Risk",
            "status": "active",
            "visibility": "public",
            "description": "Emerging market currency data with sovereign credit ratings and risk indicators",
            "domain": "Finance",
            "dataset_type": "Time-series",
            "granularity": "Daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["emerging markets", "sovereign risk", "currencies", "credit ratings"],
            "entities": ["countries", "currencies", "sovereigns"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["BR", "IN", "ZA", "TR", "MX", "ID"], "regions": ["South America", "Asia", "Africa"]},
            "columns": [
                {"name": "country_code", "description": "ISO 3166 country code", "data_type": "VARCHAR(3)", "sample_values": ["BRA", "IND", "ZAF"]},
                {"name": "currency_code", "description": "Currency code", "data_type": "VARCHAR(3)", "sample_values": ["BRL", "INR", "ZAR"]},
                {"name": "trade_date", "description": "Trading date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-01-16"]},
                {"name": "usd_exchange_rate", "description": "Exchange rate vs USD", "data_type": "DECIMAL(12,6)", "sample_values": [4.950000, 83.250000]},
                {"name": "sovereign_cds_bps", "description": "5Y sovereign CDS spread in basis points", "data_type": "DECIMAL(8,2)", "sample_values": [250.50, 180.30]},
                {"name": "credit_rating", "description": "Sovereign credit rating", "data_type": "VARCHAR(10)", "sample_values": ["BB+", "BBB-", "BB"]},
                {"name": "fx_reserves_usd_bn", "description": "FX reserves in USD billions", "data_type": "DECIMAL(10,2)", "sample_values": [350.50, 620.30]},
                {"name": "debt_to_gdp", "description": "Government debt to GDP percentage", "data_type": "DECIMAL(6,2)", "sample_values": [85.50, 70.30]},
                {"name": "inflation_rate", "description": "Annual inflation rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [5.50, 4.80]},
                {"name": "policy_rate", "description": "Central bank policy rate percentage", "data_type": "DECIMAL(6,3)", "sample_values": [11.750, 6.500]},
            ]
        },
        
        # ============ HEALTHCARE DOMAIN - MediVault Health Data (Vendor 1) ============
        # RELATED DATASETS: Patient Records + Treatment Outcomes (join on patient_id)
        {
            "vendor_email": "contact@medivault.com",
            "title": "Electronic Health Records (EHR) Database",
            "status": "active",
            "visibility": "public",
            "description": "Anonymized patient electronic health records with demographics, diagnoses, and visit history",
            "domain": "Healthcare",
            "dataset_type": "Clinical",
            "granularity": "Patient-level",
            "pricing_model": "Subscription",
            "license": "Research Use Only",
            "topics": ["EHR", "patient records", "diagnoses", "medical history"],
            "entities": ["patients", "visits", "diagnoses"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US"], "regions": ["North America"]},
            "columns": [
                {"name": "patient_id", "description": "Anonymized patient identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890", "b2c3d4e5-f6g7-8901-bcde-fg2345678901"]},
                {"name": "age", "description": "Patient age in years", "data_type": "INTEGER", "sample_values": [45, 62]},
                {"name": "gender", "description": "Patient gender", "data_type": "VARCHAR(20)", "sample_values": ["Male", "Female", "Other"]},
                {"name": "race_ethnicity", "description": "Race and ethnicity", "data_type": "VARCHAR(50)", "sample_values": ["White", "Hispanic", "Asian", "Black"]},
                {"name": "primary_diagnosis", "description": "ICD-10 primary diagnosis code", "data_type": "VARCHAR(10)", "sample_values": ["E11.9", "I10", "J44.0"]},
                {"name": "secondary_diagnoses", "description": "List of secondary diagnosis codes", "data_type": "VARCHAR(200)", "sample_values": ["E78.5,Z79.4", "I25.10,E11.9"]},
                {"name": "admission_date", "description": "Hospital admission date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "discharge_date", "description": "Hospital discharge date", "data_type": "DATE", "sample_values": ["2024-01-20", "2024-02-25"]},
                {"name": "length_of_stay", "description": "Length of hospital stay in days", "data_type": "INTEGER", "sample_values": [5, 5]},
                {"name": "total_charges_usd", "description": "Total hospital charges in USD", "data_type": "DECIMAL(10,2)", "sample_values": [25000.00, 45000.00]},
            ]
        },
        {
            "vendor_email": "contact@medivault.com",
            "title": "Patient Treatment Outcomes and Recovery Metrics",
            "status": "active",
            "visibility": "public",
            "description": "Post-treatment outcomes, recovery scores, readmission rates, and quality metrics",
            "domain": "Healthcare",
            "dataset_type": "Clinical",
            "granularity": "Patient-level",
            "pricing_model": "Subscription",
            "license": "Research Use Only",
            "topics": ["outcomes", "recovery", "readmissions", "quality metrics"],
            "entities": ["patients", "treatments", "outcomes"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US"], "regions": ["North America"]},
            "columns": [
                {"name": "patient_id", "description": "Anonymized patient identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890", "b2c3d4e5-f6g7-8901-bcde-fg2345678901"]},
                {"name": "treatment_date", "description": "Date of treatment", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "treatment_type", "description": "Type of treatment administered", "data_type": "VARCHAR(100)", "sample_values": ["Surgery", "Medication", "Physical Therapy"]},
                {"name": "primary_procedure", "description": "Primary procedure code (CPT)", "data_type": "VARCHAR(10)", "sample_values": ["33533", "99213", "97110"]},
                {"name": "outcome_score", "description": "Recovery outcome score (0-100)", "data_type": "INTEGER", "sample_values": [85, 92, 78]},
                {"name": "readmitted", "description": "Whether patient was readmitted within 30 days", "data_type": "BOOLEAN", "sample_values": [False, True, False]},
                {"name": "readmission_date", "description": "Date of readmission if applicable", "data_type": "DATE", "sample_values": [None, "2024-03-15", None]},
                {"name": "complications", "description": "Post-treatment complications", "data_type": "VARCHAR(200)", "sample_values": ["None", "Infection", "Bleeding"]},
                {"name": "patient_satisfaction", "description": "Patient satisfaction score (1-10)", "data_type": "INTEGER", "sample_values": [9, 7, 8]},
                {"name": "mortality_risk_score", "description": "30-day mortality risk score", "data_type": "DECIMAL(5,2)", "sample_values": [2.50, 15.30, 5.75]},
            ]
        },
        {
            "vendor_email": "contact@medivault.com",
            "title": "Hospital Quality and Performance Metrics",
            "status": "active",
            "visibility": "public",
            "description": "Hospital-level quality indicators, safety metrics, and performance benchmarks",
            "domain": "Healthcare",
            "dataset_type": "Aggregate",
            "granularity": "Hospital-level",
            "pricing_model": "One-time Purchase",
            "license": "Commercial Use Allowed",
            "topics": ["quality", "safety", "performance", "benchmarks"],
            "entities": ["hospitals", "facilities", "departments"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Quarterly"},
            "geographic_coverage": {"countries": ["US"], "regions": ["North America"]},
            "columns": [
                {"name": "hospital_id", "description": "CMS hospital identifier", "data_type": "VARCHAR(10)", "sample_values": ["010001", "010023", "050141"]},
                {"name": "hospital_name", "description": "Hospital name", "data_type": "VARCHAR(100)", "sample_values": ["City General Hospital", "Memorial Medical Center"]},
                {"name": "quarter", "description": "Reporting quarter", "data_type": "VARCHAR(7)", "sample_values": ["Q1-2024", "Q2-2024"]},
                {"name": "bed_count", "description": "Number of licensed beds", "data_type": "INTEGER", "sample_values": [250, 450, 800]},
                {"name": "mortality_rate", "description": "30-day mortality rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [8.50, 12.30, 6.75]},
                {"name": "readmission_rate", "description": "30-day readmission rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [15.20, 18.50, 12.80]},
                {"name": "infection_rate", "description": "Hospital-acquired infection rate per 1000 days", "data_type": "DECIMAL(6,2)", "sample_values": [2.50, 3.75, 1.80]},
                {"name": "patient_satisfaction", "description": "Average patient satisfaction score (0-10)", "data_type": "DECIMAL(3,1)", "sample_values": [8.5, 7.2, 9.1]},
                {"name": "average_los", "description": "Average length of stay in days", "data_type": "DECIMAL(4,1)", "sample_values": [4.5, 5.2, 3.8]},
                {"name": "cms_star_rating", "description": "CMS star rating (1-5)", "data_type": "INTEGER", "sample_values": [4, 3, 5]},
            ]
        },
        {
            "vendor_email": "contact@medivault.com",
            "title": "Medical Imaging and Diagnostic Test Results",
            "status": "active",
            "visibility": "public",
            "description": "Anonymized medical imaging reports and diagnostic test results with findings",
            "domain": "Healthcare",
            "dataset_type": "Clinical",
            "granularity": "Test-level",
            "pricing_model": "Usage-based",
            "license": "Research Use Only",
            "topics": ["imaging", "radiology", "diagnostics", "lab results"],
            "entities": ["patients", "tests", "findings"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US"], "regions": ["North America"]},
            "columns": [
                {"name": "patient_id", "description": "Anonymized patient identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "test_date", "description": "Date of diagnostic test", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "test_type", "description": "Type of diagnostic test", "data_type": "VARCHAR(50)", "sample_values": ["CT Scan", "MRI", "X-Ray", "Blood Test"]},
                {"name": "body_part", "description": "Anatomical region examined", "data_type": "VARCHAR(50)", "sample_values": ["Chest", "Brain", "Abdomen"]},
                {"name": "findings", "description": "Summary of test findings", "data_type": "VARCHAR(500)", "sample_values": ["No acute findings", "Small nodule detected", "Normal range"]},
                {"name": "abnormal_flag", "description": "Whether test results are abnormal", "data_type": "BOOLEAN", "sample_values": [False, True, False]},
                {"name": "radiologist_name", "description": "Anonymized radiologist identifier", "data_type": "VARCHAR(50)", "sample_values": ["RAD_001", "RAD_045"]},
                {"name": "urgency_level", "description": "Result urgency level", "data_type": "VARCHAR(20)", "sample_values": ["Routine", "Urgent", "STAT"]},
                {"name": "follow_up_required", "description": "Whether follow-up is recommended", "data_type": "BOOLEAN", "sample_values": [False, True, False]},
            ]
        },
        {
            "vendor_email": "contact@medivault.com",
            "title": "Prescription Drug History and Medication Records",
            "status": "active",
            "visibility": "public",
            "description": "Patient medication histories, prescriptions, adherence rates, and drug interactions",
            "domain": "Healthcare",
            "dataset_type": "Transactional",
            "granularity": "Prescription-level",
            "pricing_model": "Subscription",
            "license": "Research Use Only",
            "topics": ["prescriptions", "medications", "adherence", "pharmacy"],
            "entities": ["patients", "prescriptions", "drugs"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US"], "regions": ["North America"]},
            "columns": [
                {"name": "patient_id", "description": "Anonymized patient identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "prescription_date", "description": "Date prescription was written", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "drug_name", "description": "Generic drug name", "data_type": "VARCHAR(100)", "sample_values": ["Metformin", "Lisinopril", "Atorvastatin"]},
                {"name": "ndc_code", "description": "National Drug Code", "data_type": "VARCHAR(11)", "sample_values": ["00002-3238-01", "00378-0201-05"]},
                {"name": "dosage", "description": "Drug dosage and strength", "data_type": "VARCHAR(50)", "sample_values": ["500mg", "10mg", "20mg"]},
                {"name": "quantity", "description": "Number of units prescribed", "data_type": "INTEGER", "sample_values": [30, 90, 60]},
                {"name": "refills_allowed", "description": "Number of refills authorized", "data_type": "INTEGER", "sample_values": [3, 5, 0]},
                {"name": "prescriber_id", "description": "Anonymized prescriber identifier", "data_type": "VARCHAR(20)", "sample_values": ["DOC_1234", "DOC_5678"]},
                {"name": "adherence_rate", "description": "Medication adherence rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [85.50, 92.30, 68.75]},
                {"name": "cost_usd", "description": "Prescription cost in USD", "data_type": "DECIMAL(8,2)", "sample_values": [25.50, 150.00, 75.25]},
            ]
        },
        
        # ============ HEALTHCARE DOMAIN - ClinicalData Intelligence (Vendor 2) ============
        # RELATED DATASETS: Clinical Trials + Adverse Events (join on trial_id)
        {
            "vendor_email": "info@clinicaldata.io",
            "title": "Clinical Trial Registry and Protocol Data",
            "status": "active",
            "visibility": "public",
            "description": "Comprehensive clinical trial protocols, enrollment data, and study design information",
            "domain": "Healthcare",
            "dataset_type": "Clinical",
            "granularity": "Trial-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["clinical trials", "drug development", "research", "protocols"],
            "entities": ["trials", "studies", "interventions"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "UK", "EU", "Global"], "regions": ["North America", "Europe", "Worldwide"]},
            "columns": [
                {"name": "trial_id", "description": "ClinicalTrials.gov NCT number", "data_type": "VARCHAR(20)", "sample_values": ["NCT04567890", "NCT03456789"]},
                {"name": "trial_title", "description": "Official trial title", "data_type": "VARCHAR(500)", "sample_values": ["Phase 3 Study of Drug X in Type 2 Diabetes", "Safety Study of Biologic Y"]},
                {"name": "sponsor", "description": "Trial sponsor organization", "data_type": "VARCHAR(200)", "sample_values": ["Pfizer Inc", "Novartis", "NIH"]},
                {"name": "phase", "description": "Clinical trial phase", "data_type": "VARCHAR(20)", "sample_values": ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]},
                {"name": "study_type", "description": "Type of clinical study", "data_type": "VARCHAR(50)", "sample_values": ["Interventional", "Observational"]},
                {"name": "condition", "description": "Medical condition being studied", "data_type": "VARCHAR(200)", "sample_values": ["Type 2 Diabetes", "Breast Cancer", "Hypertension"]},
                {"name": "intervention", "description": "Treatment or intervention being tested", "data_type": "VARCHAR(200)", "sample_values": ["Drug X 10mg daily", "Placebo", "Biologic Y"]},
                {"name": "enrollment", "description": "Number of participants enrolled", "data_type": "INTEGER", "sample_values": [500, 1000, 250]},
                {"name": "start_date", "description": "Trial start date", "data_type": "DATE", "sample_values": ["2022-01-15", "2021-06-20"]},
                {"name": "completion_date", "description": "Expected or actual completion date", "data_type": "DATE", "sample_values": ["2025-12-31", "2024-08-15"]},
                {"name": "status", "description": "Current trial status", "data_type": "VARCHAR(50)", "sample_values": ["Recruiting", "Completed", "Active, not recruiting"]},
            ]
        },
        {
            "vendor_email": "info@clinicaldata.io",
            "title": "Clinical Trial Adverse Events and Safety Data",
            "status": "active",
            "visibility": "public",
            "description": "Adverse event reports, safety signals, and pharmacovigilance data from clinical trials",
            "domain": "Healthcare",
            "dataset_type": "Clinical",
            "granularity": "Event-level",
            "pricing_model": "Subscription",
            "license": "Research Use Only",
            "topics": ["adverse events", "safety", "pharmacovigilance", "side effects"],
            "entities": ["trials", "events", "participants"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "UK", "EU", "Global"], "regions": ["North America", "Europe", "Worldwide"]},
            "columns": [
                {"name": "trial_id", "description": "ClinicalTrials.gov NCT number", "data_type": "VARCHAR(20)", "sample_values": ["NCT04567890", "NCT03456789"]},
                {"name": "event_date", "description": "Date adverse event occurred", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "subject_id", "description": "Anonymized subject identifier", "data_type": "VARCHAR(20)", "sample_values": ["SUB_001", "SUB_002"]},
                {"name": "treatment_arm", "description": "Treatment arm assignment", "data_type": "VARCHAR(50)", "sample_values": ["Drug X", "Placebo", "Control"]},
                {"name": "event_type", "description": "Type of adverse event", "data_type": "VARCHAR(100)", "sample_values": ["Headache", "Nausea", "Elevated liver enzymes"]},
                {"name": "severity", "description": "Event severity grade", "data_type": "VARCHAR(20)", "sample_values": ["Mild", "Moderate", "Severe", "Life-threatening"]},
                {"name": "serious", "description": "Whether event is classified as serious", "data_type": "BOOLEAN", "sample_values": [False, True, False]},
                {"name": "causality", "description": "Relationship to study drug", "data_type": "VARCHAR(50)", "sample_values": ["Definitely Related", "Probably Related", "Unrelated"]},
                {"name": "outcome", "description": "Event outcome", "data_type": "VARCHAR(50)", "sample_values": ["Recovered", "Recovering", "Fatal", "Permanent Damage"]},
                {"name": "reported_by", "description": "Who reported the event", "data_type": "VARCHAR(50)", "sample_values": ["Investigator", "Subject", "Sponsor"]},
            ]
        },
        {
            "vendor_email": "info@clinicaldata.io",
            "title": "Drug Efficacy and Endpoint Analysis",
            "status": "active",
            "visibility": "public",
            "description": "Clinical trial endpoints, efficacy outcomes, and statistical analysis results",
            "domain": "Healthcare",
            "dataset_type": "Clinical",
            "granularity": "Trial-level",
            "pricing_model": "One-time Purchase",
            "license": "Commercial Use Allowed",
            "topics": ["efficacy", "endpoints", "outcomes", "statistical analysis"],
            "entities": ["trials", "endpoints", "results"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "UK", "EU", "Global"], "regions": ["North America", "Europe", "Worldwide"]},
            "columns": [
                {"name": "trial_id", "description": "ClinicalTrials.gov NCT number", "data_type": "VARCHAR(20)", "sample_values": ["NCT04567890", "NCT03456789"]},
                {"name": "primary_endpoint", "description": "Primary efficacy endpoint", "data_type": "VARCHAR(300)", "sample_values": ["HbA1c reduction from baseline", "Overall survival"]},
                {"name": "treatment_arm", "description": "Treatment group", "data_type": "VARCHAR(50)", "sample_values": ["Drug X 10mg", "Drug X 20mg", "Placebo"]},
                {"name": "n_subjects", "description": "Number of subjects in arm", "data_type": "INTEGER", "sample_values": [250, 255, 245]},
                {"name": "mean_result", "description": "Mean endpoint result", "data_type": "DECIMAL(10,4)", "sample_values": [-1.2500, -0.7500, -0.3500]},
                {"name": "std_deviation", "description": "Standard deviation of results", "data_type": "DECIMAL(10,4)", "sample_values": [0.8500, 0.9200, 0.7800]},
                {"name": "p_value", "description": "Statistical p-value", "data_type": "DECIMAL(10,8)", "sample_values": [0.00012345, 0.04500000, 0.15678900]},
                {"name": "confidence_interval", "description": "95% confidence interval", "data_type": "VARCHAR(50)", "sample_values": ["(-1.45, -1.05)", "(-0.95, -0.55)"]},
                {"name": "met_endpoint", "description": "Whether primary endpoint was met", "data_type": "BOOLEAN", "sample_values": [True, True, False]},
                {"name": "analysis_date", "description": "Date of statistical analysis", "data_type": "DATE", "sample_values": ["2024-06-15", "2024-08-20"]},
            ]
        },
        {
            "vendor_email": "info@clinicaldata.io",
            "title": "Biomarker and Laboratory Test Results",
            "status": "active",
            "visibility": "public",
            "description": "Laboratory biomarker measurements and clinical chemistry results from trials",
            "domain": "Healthcare",
            "dataset_type": "Clinical",
            "granularity": "Subject-level",
            "pricing_model": "Subscription",
            "license": "Research Use Only",
            "topics": ["biomarkers", "lab tests", "clinical chemistry", "diagnostics"],
            "entities": ["subjects", "biomarkers", "tests"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "UK", "EU", "Global"], "regions": ["North America", "Europe", "Worldwide"]},
            "columns": [
                {"name": "trial_id", "description": "ClinicalTrials.gov NCT number", "data_type": "VARCHAR(20)", "sample_values": ["NCT04567890", "NCT03456789"]},
                {"name": "subject_id", "description": "Anonymized subject identifier", "data_type": "VARCHAR(20)", "sample_values": ["SUB_001", "SUB_002"]},
                {"name": "visit_date", "description": "Date of study visit", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "biomarker_name", "description": "Name of biomarker or lab test", "data_type": "VARCHAR(100)", "sample_values": ["HbA1c", "LDL Cholesterol", "C-Reactive Protein"]},
                {"name": "test_result", "description": "Numeric test result", "data_type": "DECIMAL(10,4)", "sample_values": [7.2500, 125.5000, 3.8500]},
                {"name": "unit", "description": "Unit of measurement", "data_type": "VARCHAR(20)", "sample_values": ["%", "mg/dL", "mg/L"]},
                {"name": "normal_range_low", "description": "Lower bound of normal range", "data_type": "DECIMAL(10,4)", "sample_values": [4.0000, 70.0000, 0.0000]},
                {"name": "normal_range_high", "description": "Upper bound of normal range", "data_type": "DECIMAL(10,4)", "sample_values": [5.6000, 130.0000, 3.0000]},
                {"name": "abnormal_flag", "description": "Whether result is outside normal range", "data_type": "BOOLEAN", "sample_values": [True, False, True]},
                {"name": "change_from_baseline", "description": "Change from baseline value", "data_type": "DECIMAL(10,4)", "sample_values": [-1.2500, -25.5000, -2.1500]},
            ]
        },
        {
            "vendor_email": "info@clinicaldata.io",
            "title": "Patient-Reported Outcomes and Quality of Life",
            "status": "active",
            "visibility": "public",
            "description": "Patient-reported outcome measures (PROMs) and quality of life assessments",
            "domain": "Healthcare",
            "dataset_type": "Clinical",
            "granularity": "Subject-level",
            "pricing_model": "Subscription",
            "license": "Research Use Only",
            "topics": ["PRO", "quality of life", "patient satisfaction", "symptoms"],
            "entities": ["subjects", "assessments", "questionnaires"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "UK", "EU", "Global"], "regions": ["North America", "Europe", "Worldwide"]},
            "columns": [
                {"name": "trial_id", "description": "ClinicalTrials.gov NCT number", "data_type": "VARCHAR(20)", "sample_values": ["NCT04567890", "NCT03456789"]},
                {"name": "subject_id", "description": "Anonymized subject identifier", "data_type": "VARCHAR(20)", "sample_values": ["SUB_001", "SUB_002"]},
                {"name": "assessment_date", "description": "Date of PRO assessment", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "instrument", "description": "PRO instrument name", "data_type": "VARCHAR(100)", "sample_values": ["SF-36", "EQ-5D", "FACT-G"]},
                {"name": "domain", "description": "Domain being assessed", "data_type": "VARCHAR(50)", "sample_values": ["Physical Function", "Mental Health", "Pain"]},
                {"name": "score", "description": "Domain or total score", "data_type": "DECIMAL(6,2)", "sample_values": [75.50, 82.30, 68.75]},
                {"name": "minimal_score", "description": "Minimum possible score", "data_type": "DECIMAL(6,2)", "sample_values": [0.00, 0.00]},
                {"name": "maximal_score", "description": "Maximum possible score", "data_type": "DECIMAL(6,2)", "sample_values": [100.00, 100.00]},
                {"name": "clinically_meaningful_change", "description": "Minimum clinically important difference", "data_type": "DECIMAL(6,2)", "sample_values": [5.00, 7.50]},
                {"name": "change_from_baseline", "description": "Change from baseline score", "data_type": "DECIMAL(6,2)", "sample_values": [12.50, -5.30, 8.75]},
            ]
        },
        
        # ============ HEALTHCARE DOMAIN - PharmaLytics Global (Vendor 3) ============
        # RELATED DATASETS: Drug Prescriptions + Drug Interactions (join on drug_name/ndc_code)
        {
            "vendor_email": "sales@pharmalytics.com",
            "title": "Prescription Drug Sales and Market Share Data",
            "status": "active",
            "visibility": "public",
            "description": "Pharmaceutical prescription volumes, market share, and revenue data by drug and therapeutic class",
            "domain": "Healthcare",
            "dataset_type": "Transactional",
            "granularity": "Monthly",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["prescriptions", "pharma sales", "market share", "revenue"],
            "entities": ["drugs", "manufacturers", "therapeutic classes"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Monthly"},
            "geographic_coverage": {"countries": ["US", "UK", "EU"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "drug_name", "description": "Generic or brand drug name", "data_type": "VARCHAR(100)", "sample_values": ["Lipitor", "Metformin", "Humira"]},
                {"name": "ndc_code", "description": "National Drug Code", "data_type": "VARCHAR(11)", "sample_values": ["00002-3238-01", "00378-0201-05"]},
                {"name": "manufacturer", "description": "Drug manufacturer name", "data_type": "VARCHAR(100)", "sample_values": ["Pfizer", "Novartis", "AbbVie"]},
                {"name": "therapeutic_class", "description": "Therapeutic drug classification", "data_type": "VARCHAR(100)", "sample_values": ["Statins", "Antidiabetics", "Biologics"]},
                {"name": "month", "description": "Reporting month", "data_type": "DATE", "sample_values": ["2024-01-01", "2024-02-01"]},
                {"name": "prescription_count", "description": "Number of prescriptions filled", "data_type": "INTEGER", "sample_values": [500000, 750000, 1200000]},
                {"name": "total_revenue_usd", "description": "Total revenue in USD", "data_type": "DECIMAL(15,2)", "sample_values": [25000000.00, 45000000.00, 85000000.00]},
                {"name": "market_share_pct", "description": "Market share percentage within class", "data_type": "DECIMAL(5,2)", "sample_values": [25.50, 18.30, 42.75]},
                {"name": "average_price_usd", "description": "Average prescription price in USD", "data_type": "DECIMAL(8,2)", "sample_values": [50.00, 60.00, 70.83]},
                {"name": "generic_available", "description": "Whether generic version is available", "data_type": "BOOLEAN", "sample_values": [True, True, False]},
            ]
        },
        {
            "vendor_email": "sales@pharmalytics.com",
            "title": "Drug Interaction Database and Safety Alerts",
            "status": "active",
            "visibility": "public",
            "description": "Comprehensive drug-drug interactions, contraindications, and safety warnings",
            "domain": "Healthcare",
            "dataset_type": "Reference",
            "granularity": "Drug-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["drug interactions", "contraindications", "safety", "warnings"],
            "entities": ["drugs", "interactions", "warnings"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Updated continuously"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["North America", "Worldwide"]},
            "columns": [
                {"name": "drug_name_1", "description": "First drug in interaction", "data_type": "VARCHAR(100)", "sample_values": ["Warfarin", "Aspirin", "Simvastatin"]},
                {"name": "ndc_code_1", "description": "NDC code for first drug", "data_type": "VARCHAR(11)", "sample_values": ["00002-3238-01", "00378-0201-05"]},
                {"name": "drug_name_2", "description": "Second drug in interaction", "data_type": "VARCHAR(100)", "sample_values": ["Aspirin", "Ibuprofen", "Gemfibrozil"]},
                {"name": "ndc_code_2", "description": "NDC code for second drug", "data_type": "VARCHAR(11)", "sample_values": ["00456-7890-01", "00123-4567-08"]},
                {"name": "interaction_severity", "description": "Severity of drug interaction", "data_type": "VARCHAR(20)", "sample_values": ["Major", "Moderate", "Minor", "Contraindicated"]},
                {"name": "interaction_type", "description": "Type of interaction mechanism", "data_type": "VARCHAR(100)", "sample_values": ["Pharmacokinetic", "Pharmacodynamic", "Additive Effect"]},
                {"name": "clinical_effect", "description": "Expected clinical effect of interaction", "data_type": "VARCHAR(500)", "sample_values": ["Increased bleeding risk", "Reduced drug effectiveness", "Liver toxicity"]},
                {"name": "recommendation", "description": "Clinical management recommendation", "data_type": "VARCHAR(500)", "sample_values": ["Avoid combination", "Monitor closely", "Dose adjustment required"]},
                {"name": "evidence_level", "description": "Strength of evidence", "data_type": "VARCHAR(20)", "sample_values": ["High", "Moderate", "Low", "Theoretical"]},
                {"name": "last_updated", "description": "Date interaction data was last updated", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-03-20"]},
            ]
        },
        {
            "vendor_email": "sales@pharmalytics.com",
            "title": "FDA Drug Approval and Labeling Database",
            "status": "active",
            "visibility": "public",
            "description": "FDA drug approvals, label changes, safety communications, and regulatory actions",
            "domain": "Healthcare",
            "dataset_type": "Regulatory",
            "granularity": "Drug-level",
            "pricing_model": "One-time Purchase",
            "license": "Commercial Use Allowed",
            "topics": ["FDA approvals", "drug labels", "regulatory", "safety communications"],
            "entities": ["drugs", "approvals", "labels"],
            "temporal_coverage": {"start_date": "2000-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US"], "regions": ["North America"]},
            "columns": [
                {"name": "drug_name", "description": "Drug trade or generic name", "data_type": "VARCHAR(100)", "sample_values": ["Keytruda", "Ozempic", "Eliquis"]},
                {"name": "ndc_code", "description": "National Drug Code", "data_type": "VARCHAR(11)", "sample_values": ["00002-3238-01", "00378-0201-05"]},
                {"name": "application_number", "description": "FDA application number (NDA/BLA)", "data_type": "VARCHAR(20)", "sample_values": ["NDA 125555", "BLA 761034"]},
                {"name": "approval_date", "description": "FDA approval date", "data_type": "DATE", "sample_values": ["2014-09-04", "2017-12-05"]},
                {"name": "approval_type", "description": "Type of FDA approval", "data_type": "VARCHAR(50)", "sample_values": ["New Molecular Entity", "New Indication", "Priority Review"]},
                {"name": "indication", "description": "Approved indication", "data_type": "VARCHAR(500)", "sample_values": ["Treatment of metastatic melanoma", "Type 2 diabetes management"]},
                {"name": "sponsor", "description": "Drug sponsor/manufacturer", "data_type": "VARCHAR(100)", "sample_values": ["Merck", "Novo Nordisk", "Bristol Myers Squibb"]},
                {"name": "orphan_drug", "description": "Whether designated as orphan drug", "data_type": "BOOLEAN", "sample_values": [False, False, True]},
                {"name": "breakthrough_therapy", "description": "Whether designated as breakthrough therapy", "data_type": "BOOLEAN", "sample_values": [True, False, False]},
                {"name": "boxed_warning", "description": "Whether label includes boxed warning", "data_type": "BOOLEAN", "sample_values": [False, False, True]},
            ]
        },
        {
            "vendor_email": "sales@pharmalytics.com",
            "title": "Pharmaceutical Pricing and Reimbursement Data",
            "status": "active",
            "visibility": "public",
            "description": "Drug pricing trends, insurance reimbursement rates, and pharmacy benefit data",
            "domain": "Healthcare",
            "dataset_type": "Transactional",
            "granularity": "Monthly",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["drug pricing", "reimbursement", "insurance", "pharmacy benefit"],
            "entities": ["drugs", "payers", "pharmacies"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Monthly"},
            "geographic_coverage": {"countries": ["US"], "regions": ["North America"]},
            "columns": [
                {"name": "drug_name", "description": "Generic or brand drug name", "data_type": "VARCHAR(100)", "sample_values": ["Lipitor", "Metformin", "Humira"]},
                {"name": "ndc_code", "description": "National Drug Code", "data_type": "VARCHAR(11)", "sample_values": ["00002-3238-01", "00378-0201-05"]},
                {"name": "month", "description": "Pricing month", "data_type": "DATE", "sample_values": ["2024-01-01", "2024-02-01"]},
                {"name": "average_wholesale_price", "description": "AWP in USD", "data_type": "DECIMAL(10,2)", "sample_values": [150.00, 25.00, 5000.00]},
                {"name": "wholesale_acquisition_cost", "description": "WAC in USD", "data_type": "DECIMAL(10,2)", "sample_values": [125.00, 20.00, 4500.00]},
                {"name": "average_reimbursement", "description": "Average insurance reimbursement in USD", "data_type": "DECIMAL(10,2)", "sample_values": [100.00, 15.00, 4000.00]},
                {"name": "patient_copay_avg", "description": "Average patient copay in USD", "data_type": "DECIMAL(8,2)", "sample_values": [10.00, 5.00, 50.00]},
                {"name": "formulary_tier", "description": "Common formulary tier placement", "data_type": "VARCHAR(20)", "sample_values": ["Tier 1", "Tier 2", "Tier 3", "Specialty"]},
                {"name": "price_change_pct", "description": "Month-over-month price change percentage", "data_type": "DECIMAL(6,2)", "sample_values": [2.50, -1.25, 0.00]},
            ]
        },
        {
            "vendor_email": "sales@pharmalytics.com",
            "title": "Clinical Guidelines and Treatment Protocols",
            "status": "active",
            "visibility": "public",
            "description": "Evidence-based clinical practice guidelines and treatment protocols by condition",
            "domain": "Healthcare",
            "dataset_type": "Reference",
            "granularity": "Guideline-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["clinical guidelines", "treatment protocols", "best practices", "evidence-based medicine"],
            "entities": ["guidelines", "conditions", "treatments"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Updated continuously"},
            "geographic_coverage": {"countries": ["US", "UK", "EU"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "guideline_id", "description": "Unique guideline identifier", "data_type": "VARCHAR(50)", "sample_values": ["ADA-2024-T2D", "AHA-2023-HTN"]},
                {"name": "condition", "description": "Medical condition", "data_type": "VARCHAR(200)", "sample_values": ["Type 2 Diabetes", "Hypertension", "Breast Cancer"]},
                {"name": "issuing_organization", "description": "Organization that issued guideline", "data_type": "VARCHAR(100)", "sample_values": ["American Diabetes Association", "American Heart Association"]},
                {"name": "publication_date", "description": "Guideline publication date", "data_type": "DATE", "sample_values": ["2024-01-15", "2023-11-20"]},
                {"name": "first_line_treatment", "description": "Recommended first-line treatment", "data_type": "VARCHAR(300)", "sample_values": ["Metformin + lifestyle modification", "ACE inhibitor or ARB"]},
                {"name": "second_line_treatment", "description": "Recommended second-line treatment", "data_type": "VARCHAR(300)", "sample_values": ["Add GLP-1 agonist or SGLT2 inhibitor", "Add calcium channel blocker"]},
                {"name": "target_population", "description": "Patient population guideline applies to", "data_type": "VARCHAR(300)", "sample_values": ["Adults with newly diagnosed T2D", "Adults with stage 1-2 hypertension"]},
                {"name": "evidence_grade", "description": "Strength of evidence", "data_type": "VARCHAR(10)", "sample_values": ["A", "B", "C"]},
                {"name": "last_updated", "description": "Date guideline was last updated", "data_type": "DATE", "sample_values": ["2024-01-15", "2023-11-20"]},
            ]
        },
        
        # ============ HEALTHCARE DOMAIN - HealthMetrics Institute (Vendor 4) ============
        # RELATED DATASETS: Disease Surveillance + Vaccination Coverage (join on geography/time period)
        {
            "vendor_email": "support@healthmetrics.org",
            "title": "Disease Surveillance and Outbreak Tracking",
            "status": "active",
            "visibility": "public",
            "description": "Real-time infectious disease surveillance data, outbreak alerts, and epidemiological metrics",
            "domain": "Healthcare",
            "dataset_type": "Time-series",
            "granularity": "Weekly",
            "pricing_model": "Free",
            "license": "Public Domain",
            "topics": ["epidemiology", "disease surveillance", "outbreaks", "public health"],
            "entities": ["diseases", "cases", "regions"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Weekly"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["North America", "Worldwide"]},
            "columns": [
                {"name": "disease_name", "description": "Name of disease or condition", "data_type": "VARCHAR(100)", "sample_values": ["Influenza", "COVID-19", "Measles"]},
                {"name": "week_ending", "description": "Week ending date", "data_type": "DATE", "sample_values": ["2024-01-20", "2024-01-27"]},
                {"name": "country", "description": "Country code", "data_type": "VARCHAR(3)", "sample_values": ["USA", "GBR", "CAN"]},
                {"name": "state_province", "description": "State or province", "data_type": "VARCHAR(100)", "sample_values": ["California", "Texas", "Ontario"]},
                {"name": "new_cases", "description": "Number of new cases reported", "data_type": "INTEGER", "sample_values": [5000, 12000, 150]},
                {"name": "cumulative_cases", "description": "Cumulative cases to date", "data_type": "INTEGER", "sample_values": [250000, 1500000, 5000]},
                {"name": "hospitalizations", "description": "Number of hospitalizations", "data_type": "INTEGER", "sample_values": [500, 1200, 25]},
                {"name": "deaths", "description": "Number of deaths reported", "data_type": "INTEGER", "sample_values": [50, 150, 2]},
                {"name": "incidence_rate", "description": "Cases per 100,000 population", "data_type": "DECIMAL(8,2)", "sample_values": [12.50, 30.75, 0.50]},
                {"name": "reproduction_number", "description": "Effective reproduction number (R-effective)", "data_type": "DECIMAL(4,2)", "sample_values": [1.25, 0.85, 1.50]},
            ]
        },
        {
            "vendor_email": "support@healthmetrics.org",
            "title": "Vaccination Coverage and Immunization Rates",
            "status": "active",
            "visibility": "public",
            "description": "Vaccination coverage rates, immunization schedules, and vaccine hesitancy data",
            "domain": "Healthcare",
            "dataset_type": "Time-series",
            "granularity": "Monthly",
            "pricing_model": "Free",
            "license": "Public Domain",
            "topics": ["vaccination", "immunization", "vaccines", "public health"],
            "entities": ["vaccines", "populations", "regions"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Monthly"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["North America", "Worldwide"]},
            "columns": [
                {"name": "vaccine_name", "description": "Vaccine name", "data_type": "VARCHAR(100)", "sample_values": ["MMR", "COVID-19 mRNA", "Influenza"]},
                {"name": "month", "description": "Reporting month", "data_type": "DATE", "sample_values": ["2024-01-01", "2024-02-01"]},
                {"name": "country", "description": "Country code", "data_type": "VARCHAR(3)", "sample_values": ["USA", "GBR", "CAN"]},
                {"name": "state_province", "description": "State or province", "data_type": "VARCHAR(100)", "sample_values": ["California", "Texas", "Ontario"]},
                {"name": "age_group", "description": "Age group", "data_type": "VARCHAR(20)", "sample_values": ["0-4", "5-17", "18-64", "65+"]},
                {"name": "doses_administered", "description": "Number of vaccine doses administered", "data_type": "INTEGER", "sample_values": [500000, 1200000, 250000]},
                {"name": "population", "description": "Total population in age group", "data_type": "INTEGER", "sample_values": [2000000, 5000000, 1000000]},
                {"name": "coverage_rate_pct", "description": "Vaccination coverage rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [85.50, 92.30, 68.75]},
                {"name": "fully_vaccinated_pct", "description": "Percentage fully vaccinated", "data_type": "DECIMAL(5,2)", "sample_values": [75.50, 82.30, 58.75]},
                {"name": "hesitancy_rate_pct", "description": "Estimated vaccine hesitancy rate", "data_type": "DECIMAL(5,2)", "sample_values": [15.50, 8.30, 25.75]},
            ]
        },
        {
            "vendor_email": "support@healthmetrics.org",
            "title": "Chronic Disease Prevalence and Risk Factors",
            "status": "active",
            "visibility": "public",
            "description": "Population-level chronic disease prevalence, risk factors, and health behaviors",
            "domain": "Healthcare",
            "dataset_type": "Survey",
            "granularity": "Annual",
            "pricing_model": "Free",
            "license": "Public Domain",
            "topics": ["chronic disease", "prevalence", "risk factors", "health behaviors"],
            "entities": ["populations", "diseases", "risk factors"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Annual"},
            "geographic_coverage": {"countries": ["US"], "regions": ["North America"]},
            "columns": [
                {"name": "year", "description": "Survey year", "data_type": "INTEGER", "sample_values": [2022, 2023, 2024]},
                {"name": "state", "description": "US state", "data_type": "VARCHAR(50)", "sample_values": ["California", "Texas", "New York"]},
                {"name": "disease", "description": "Chronic disease or condition", "data_type": "VARCHAR(100)", "sample_values": ["Diabetes", "Hypertension", "Obesity", "Heart Disease"]},
                {"name": "prevalence_pct", "description": "Disease prevalence percentage", "data_type": "DECIMAL(5,2)", "sample_values": [12.50, 32.30, 42.75]},
                {"name": "age_group", "description": "Age group", "data_type": "VARCHAR(20)", "sample_values": ["18-44", "45-64", "65+"]},
                {"name": "gender", "description": "Gender", "data_type": "VARCHAR(20)", "sample_values": ["Male", "Female", "All"]},
                {"name": "obesity_rate_pct", "description": "Obesity prevalence percentage", "data_type": "DECIMAL(5,2)", "sample_values": [35.50, 42.30, 28.75]},
                {"name": "smoking_rate_pct", "description": "Current smoking rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [15.50, 18.30, 12.75]},
                {"name": "physical_inactivity_pct", "description": "Physical inactivity rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [25.50, 32.30, 18.75]},
                {"name": "sample_size", "description": "Survey sample size", "data_type": "INTEGER", "sample_values": [5000, 10000, 15000]},
            ]
        },
        {
            "vendor_email": "support@healthmetrics.org",
            "title": "Healthcare Access and Utilization Metrics",
            "status": "active",
            "visibility": "public",
            "description": "Healthcare access, utilization rates, insurance coverage, and health disparities data",
            "domain": "Healthcare",
            "dataset_type": "Survey",
            "granularity": "Annual",
            "pricing_model": "Free",
            "license": "Public Domain",
            "topics": ["healthcare access", "utilization", "insurance", "disparities"],
            "entities": ["populations", "services", "regions"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Annual"},
            "geographic_coverage": {"countries": ["US"], "regions": ["North America"]},
            "columns": [
                {"name": "year", "description": "Survey year", "data_type": "INTEGER", "sample_values": [2022, 2023, 2024]},
                {"name": "state", "description": "US state", "data_type": "VARCHAR(50)", "sample_values": ["California", "Texas", "New York"]},
                {"name": "insurance_coverage_pct", "description": "Percentage with health insurance", "data_type": "DECIMAL(5,2)", "sample_values": [92.50, 88.30, 95.75]},
                {"name": "uninsured_rate_pct", "description": "Uninsured rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [7.50, 11.70, 4.25]},
                {"name": "primary_care_visits_avg", "description": "Average primary care visits per person per year", "data_type": "DECIMAL(4,2)", "sample_values": [3.5, 4.2, 2.8]},
                {"name": "er_visits_per_1000", "description": "Emergency room visits per 1000 population", "data_type": "DECIMAL(6,2)", "sample_values": [450.50, 520.30, 380.75]},
                {"name": "preventive_care_pct", "description": "Percentage receiving preventive care", "data_type": "DECIMAL(5,2)", "sample_values": [65.50, 72.30, 58.75]},
                {"name": "delayed_care_cost_pct", "description": "Percentage who delayed care due to cost", "data_type": "DECIMAL(5,2)", "sample_values": [15.50, 22.30, 8.75]},
                {"name": "has_usual_provider_pct", "description": "Percentage with usual source of care", "data_type": "DECIMAL(5,2)", "sample_values": [75.50, 82.30, 68.75]},
                {"name": "sample_size", "description": "Survey sample size", "data_type": "INTEGER", "sample_values": [10000, 15000, 20000]},
            ]
        },
        {
            "vendor_email": "support@healthmetrics.org",
            "title": "Mental Health and Substance Abuse Statistics",
            "status": "active",
            "visibility": "public",
            "description": "Mental health disorder prevalence, substance abuse rates, and treatment access data",
            "domain": "Healthcare",
            "dataset_type": "Survey",
            "granularity": "Annual",
            "pricing_model": "Free",
            "license": "Public Domain",
            "topics": ["mental health", "substance abuse", "addiction", "treatment access"],
            "entities": ["populations", "disorders", "treatments"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Annual"},
            "geographic_coverage": {"countries": ["US"], "regions": ["North America"]},
            "columns": [
                {"name": "year", "description": "Survey year", "data_type": "INTEGER", "sample_values": [2022, 2023, 2024]},
                {"name": "state", "description": "US state", "data_type": "VARCHAR(50)", "sample_values": ["California", "Texas", "New York"]},
                {"name": "age_group", "description": "Age group", "data_type": "VARCHAR(20)", "sample_values": ["18-25", "26-49", "50+"]},
                {"name": "depression_prevalence_pct", "description": "Depression prevalence percentage", "data_type": "DECIMAL(5,2)", "sample_values": [18.50, 15.30, 12.75]},
                {"name": "anxiety_prevalence_pct", "description": "Anxiety disorder prevalence percentage", "data_type": "DECIMAL(5,2)", "sample_values": [22.50, 19.30, 16.75]},
                {"name": "substance_abuse_pct", "description": "Substance use disorder prevalence percentage", "data_type": "DECIMAL(5,2)", "sample_values": [8.50, 12.30, 5.75]},
                {"name": "opioid_misuse_pct", "description": "Opioid misuse rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [3.50, 5.30, 2.75]},
                {"name": "received_treatment_pct", "description": "Percentage who received mental health treatment", "data_type": "DECIMAL(5,2)", "sample_values": [45.50, 52.30, 38.75]},
                {"name": "unmet_need_pct", "description": "Percentage with unmet mental health need", "data_type": "DECIMAL(5,2)", "sample_values": [35.50, 42.30, 28.75]},
                {"name": "sample_size", "description": "Survey sample size", "data_type": "INTEGER", "sample_values": [15000, 20000, 25000]},
            ]
        },
        
        # ============ ENTERTAINMENT & MEDIA DOMAIN - StreamVault Media Analytics (Vendor 1) ============
        # RELATED DATASETS: Music Streaming + Artist Profiles (join on artist_id), Song Streams + User Listening (join on track_id/user_id)
        {
            "vendor_email": "data@streamvault.com",
            "title": "Music Streaming Data - Songs and Plays",
            "status": "active",
            "visibility": "public",
            "description": "Comprehensive music streaming data including song plays, skip rates, playlist additions, and user engagement metrics",
            "domain": "Entertainment & Media",
            "dataset_type": "Time-series",
            "granularity": "Daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["music streaming", "song plays", "user engagement", "playlists"],
            "entities": ["songs", "artists", "users", "playlists"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "UK", "CA", "AU", "Global"], "regions": ["North America", "Europe", "Asia", "Worldwide"]},
            "columns": [
                {"name": "track_id", "description": "Unique song/track identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "artist_id", "description": "Artist identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "track_name", "description": "Song title", "data_type": "VARCHAR(200)", "sample_values": ["Blinding Lights", "Shape of You", "Dance Monkey"]},
                {"name": "artist_name", "description": "Artist or band name", "data_type": "VARCHAR(200)", "sample_values": ["The Weeknd", "Ed Sheeran", "Tones and I"]},
                {"name": "date", "description": "Streaming date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "total_streams", "description": "Total number of streams", "data_type": "INTEGER", "sample_values": [5000000, 3500000, 8200000]},
                {"name": "unique_listeners", "description": "Number of unique listeners", "data_type": "INTEGER", "sample_values": [2500000, 1800000, 4100000]},
                {"name": "skip_rate_pct", "description": "Percentage of streams skipped before 30 seconds", "data_type": "DECIMAL(5,2)", "sample_values": [15.50, 22.30, 8.75]},
                {"name": "playlist_adds", "description": "Number of playlist additions", "data_type": "INTEGER", "sample_values": [150000, 85000, 220000]},
                {"name": "average_completion_pct", "description": "Average percentage of song completed", "data_type": "DECIMAL(5,2)", "sample_values": [85.50, 78.30, 92.75]},
            ]
        },
        {
            "vendor_email": "data@streamvault.com",
            "title": "Artist Profile and Performance Metrics",
            "status": "active",
            "visibility": "public",
            "description": "Artist-level metrics including follower counts, monthly listeners, top markets, and career analytics",
            "domain": "Entertainment & Media",
            "dataset_type": "Profile",
            "granularity": "Artist-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["artists", "followers", "listeners", "analytics"],
            "entities": ["artists", "albums", "markets"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "UK", "CA", "AU", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "artist_id", "description": "Artist identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "artist_name", "description": "Artist or band name", "data_type": "VARCHAR(200)", "sample_values": ["The Weeknd", "Ed Sheeran", "Taylor Swift"]},
                {"name": "date", "description": "Snapshot date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "follower_count", "description": "Total followers", "data_type": "INTEGER", "sample_values": [50000000, 35000000, 82000000]},
                {"name": "monthly_listeners", "description": "Monthly listeners", "data_type": "INTEGER", "sample_values": [75000000, 45000000, 95000000]},
                {"name": "top_country", "description": "Country with most listeners", "data_type": "VARCHAR(3)", "sample_values": ["USA", "GBR", "BRA"]},
                {"name": "genre_primary", "description": "Primary genre", "data_type": "VARCHAR(50)", "sample_values": ["Pop", "R&B", "Country"]},
                {"name": "total_tracks", "description": "Total tracks released", "data_type": "INTEGER", "sample_values": [250, 180, 420]},
                {"name": "verified", "description": "Whether artist is verified", "data_type": "BOOLEAN", "sample_values": [True, True, True]},
                {"name": "popularity_score", "description": "Popularity score (0-100)", "data_type": "INTEGER", "sample_values": [95, 88, 99]},
            ]
        },
        {
            "vendor_email": "data@streamvault.com",
            "title": "Podcast Analytics and Listener Engagement",
            "status": "active",
            "visibility": "public",
            "description": "Podcast episode performance, listener demographics, completion rates, and subscription metrics",
            "domain": "Entertainment & Media",
            "dataset_type": "Time-series",
            "granularity": "Episode-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["podcasts", "episodes", "listeners", "engagement"],
            "entities": ["podcasts", "episodes", "listeners"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "UK", "CA", "AU"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "podcast_id", "description": "Unique podcast identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "episode_id", "description": "Unique episode identifier", "data_type": "UUID", "sample_values": ["d4e5f6a7-b8c9-0123-def1-234567890123"]},
                {"name": "podcast_name", "description": "Podcast show name", "data_type": "VARCHAR(200)", "sample_values": ["The Daily", "Joe Rogan Experience", "Crime Junkie"]},
                {"name": "episode_title", "description": "Episode title", "data_type": "VARCHAR(300)", "sample_values": ["Breaking News Special", "Interview with Elon Musk"]},
                {"name": "publish_date", "description": "Episode publish date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "total_listens", "description": "Total episode listens", "data_type": "INTEGER", "sample_values": [1500000, 850000, 2200000]},
                {"name": "unique_listeners", "description": "Unique listeners", "data_type": "INTEGER", "sample_values": [1200000, 700000, 1800000]},
                {"name": "average_completion_pct", "description": "Average completion percentage", "data_type": "DECIMAL(5,2)", "sample_values": [75.50, 82.30, 68.75]},
                {"name": "episode_length_minutes", "description": "Episode duration in minutes", "data_type": "INTEGER", "sample_values": [30, 180, 45]},
                {"name": "subscriber_count", "description": "Podcast subscriber count at publish date", "data_type": "INTEGER", "sample_values": [5000000, 12000000, 3500000]},
            ]
        },
        {
            "vendor_email": "data@streamvault.com",
            "title": "Video Content Streaming and Engagement",
            "status": "active",
            "visibility": "public",
            "description": "Video streaming platform data including views, watch time, engagement metrics, and content performance",
            "domain": "Entertainment & Media",
            "dataset_type": "Time-series",
            "granularity": "Video-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["video streaming", "views", "watch time", "engagement"],
            "entities": ["videos", "channels", "viewers"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "UK", "CA", "AU", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "video_id", "description": "Unique video identifier", "data_type": "UUID", "sample_values": ["e5f6a7b8-c9d0-1234-ef12-345678901234"]},
                {"name": "channel_id", "description": "Channel identifier", "data_type": "UUID", "sample_values": ["f6a7b8c9-d0e1-2345-f123-456789012345"]},
                {"name": "video_title", "description": "Video title", "data_type": "VARCHAR(300)", "sample_values": ["How to Code in Python", "Top 10 Travel Destinations", "Music Video - Latest Hit"]},
                {"name": "channel_name", "description": "Channel name", "data_type": "VARCHAR(200)", "sample_values": ["Tech Tutorials", "Travel Vlogger", "VEVO Music"]},
                {"name": "upload_date", "description": "Video upload date", "data_type": "DATE", "sample_values": ["2024-01-10", "2024-02-15"]},
                {"name": "total_views", "description": "Total video views", "data_type": "INTEGER", "sample_values": [5000000, 2500000, 15000000]},
                {"name": "watch_time_hours", "description": "Total watch time in hours", "data_type": "INTEGER", "sample_values": [250000, 125000, 750000]},
                {"name": "likes", "description": "Number of likes", "data_type": "INTEGER", "sample_values": [150000, 85000, 450000]},
                {"name": "comments", "description": "Number of comments", "data_type": "INTEGER", "sample_values": [5000, 3500, 12000]},
                {"name": "average_view_duration_seconds", "description": "Average view duration", "data_type": "INTEGER", "sample_values": [180, 240, 150]},
            ]
        },
        {
            "vendor_email": "data@streamvault.com",
            "title": "User Listening and Viewing Behavior",
            "status": "active",
            "visibility": "public",
            "description": "Anonymized user behavior data including listening/viewing patterns, preferences, and engagement trends",
            "domain": "Entertainment & Media",
            "dataset_type": "Behavioral",
            "granularity": "User-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["user behavior", "preferences", "engagement", "patterns"],
            "entities": ["users", "sessions", "content"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "UK", "CA", "AU"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "user_id", "description": "Anonymized user identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "track_id", "description": "Content identifier (song/video/episode)", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "session_date", "description": "Session date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "content_type", "description": "Type of content", "data_type": "VARCHAR(20)", "sample_values": ["music", "video", "podcast"]},
                {"name": "play_duration_seconds", "description": "Total play duration", "data_type": "INTEGER", "sample_values": [180, 240, 3600]},
                {"name": "device_type", "description": "Device used", "data_type": "VARCHAR(50)", "sample_values": ["mobile", "desktop", "smart_speaker", "tv"]},
                {"name": "country", "description": "User country", "data_type": "VARCHAR(3)", "sample_values": ["USA", "GBR", "CAN"]},
                {"name": "subscription_tier", "description": "User subscription level", "data_type": "VARCHAR(20)", "sample_values": ["free", "premium", "family"]},
                {"name": "completed", "description": "Whether content was completed", "data_type": "BOOLEAN", "sample_values": [True, False, True]},
            ]
        },
        
        # ============ ENTERTAINMENT & MEDIA DOMAIN - CineMetrics Intelligence (Vendor 2) ============
        # RELATED DATASETS: Box Office + Movie Details (join on movie_id), TV Ratings + Show Details (join on show_id)
        {
            "vendor_email": "sales@cinemetrics.io",
            "title": "Box Office Performance Data",
            "status": "active",
            "visibility": "public",
            "description": "Daily box office revenue, ticket sales, theater counts, and market performance for theatrical releases",
            "domain": "Entertainment & Media",
            "dataset_type": "Time-series",
            "granularity": "Daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["box office", "movies", "revenue", "ticket sales"],
            "entities": ["movies", "theaters", "studios"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["North America", "Worldwide"]},
            "columns": [
                {"name": "movie_id", "description": "Unique movie identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "movie_title", "description": "Film title", "data_type": "VARCHAR(300)", "sample_values": ["Oppenheimer", "Barbie", "Avatar: The Way of Water"]},
                {"name": "release_date", "description": "Theatrical release date", "data_type": "DATE", "sample_values": ["2023-07-21", "2023-07-21", "2022-12-16"]},
                {"name": "date", "description": "Box office date", "data_type": "DATE", "sample_values": ["2023-07-22", "2023-07-23"]},
                {"name": "daily_gross_usd", "description": "Daily box office revenue in USD", "data_type": "DECIMAL(15,2)", "sample_values": [15000000.00, 25000000.00, 45000000.00]},
                {"name": "cumulative_gross_usd", "description": "Cumulative box office in USD", "data_type": "DECIMAL(15,2)", "sample_values": [150000000.00, 250000000.00, 850000000.00]},
                {"name": "theater_count", "description": "Number of theaters showing", "data_type": "INTEGER", "sample_values": [3500, 4200, 4800]},
                {"name": "per_theater_average_usd", "description": "Average revenue per theater", "data_type": "DECIMAL(10,2)", "sample_values": [4285.71, 5952.38, 9375.00]},
                {"name": "rank", "description": "Daily box office rank", "data_type": "INTEGER", "sample_values": [1, 2, 3]},
                {"name": "days_in_release", "description": "Number of days since release", "data_type": "INTEGER", "sample_values": [1, 10, 30]},
            ]
        },
        {
            "vendor_email": "sales@cinemetrics.io",
            "title": "Movie Details and Production Information",
            "status": "active",
            "visibility": "public",
            "description": "Comprehensive movie metadata including cast, crew, budget, genre, ratings, and production details",
            "domain": "Entertainment & Media",
            "dataset_type": "Reference",
            "granularity": "Movie-level",
            "pricing_model": "One-time Purchase",
            "license": "Commercial Use Allowed",
            "topics": ["movies", "cast", "crew", "budget", "production"],
            "entities": ["movies", "actors", "directors", "studios"],
            "temporal_coverage": {"start_date": "1900-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "movie_id", "description": "Unique movie identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "movie_title", "description": "Film title", "data_type": "VARCHAR(300)", "sample_values": ["Oppenheimer", "Barbie", "The Godfather"]},
                {"name": "release_date", "description": "Theatrical release date", "data_type": "DATE", "sample_values": ["2023-07-21", "1972-03-24"]},
                {"name": "director", "description": "Director name", "data_type": "VARCHAR(200)", "sample_values": ["Christopher Nolan", "Greta Gerwig", "Francis Ford Coppola"]},
                {"name": "studio", "description": "Production studio", "data_type": "VARCHAR(200)", "sample_values": ["Universal Pictures", "Warner Bros", "Paramount"]},
                {"name": "production_budget_usd", "description": "Production budget in USD", "data_type": "DECIMAL(15,2)", "sample_values": [100000000.00, 145000000.00, 6000000.00]},
                {"name": "genre", "description": "Primary genre", "data_type": "VARCHAR(50)", "sample_values": ["Drama", "Comedy", "Action", "Thriller"]},
                {"name": "runtime_minutes", "description": "Film runtime in minutes", "data_type": "INTEGER", "sample_values": [180, 114, 175]},
                {"name": "mpaa_rating", "description": "MPAA rating", "data_type": "VARCHAR(10)", "sample_values": ["R", "PG-13", "PG", "G"]},
                {"name": "imdb_rating", "description": "IMDb user rating (0-10)", "data_type": "DECIMAL(3,1)", "sample_values": [8.5, 7.0, 9.2]},
            ]
        },
        {
            "vendor_email": "sales@cinemetrics.io",
            "title": "Television Ratings and Viewership Data",
            "status": "active",
            "visibility": "public",
            "description": "TV show ratings, viewership numbers, demographic breakdowns, and episode-level performance metrics",
            "domain": "Entertainment & Media",
            "dataset_type": "Time-series",
            "granularity": "Episode-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["television", "ratings", "viewership", "demographics"],
            "entities": ["shows", "episodes", "networks"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US"], "regions": ["North America"]},
            "columns": [
                {"name": "show_id", "description": "Unique show identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "episode_id", "description": "Unique episode identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "show_title", "description": "TV show title", "data_type": "VARCHAR(200)", "sample_values": ["Game of Thrones", "The Office", "Breaking Bad"]},
                {"name": "air_date", "description": "Episode air date", "data_type": "DATE", "sample_values": ["2023-01-15", "2023-02-20"]},
                {"name": "network", "description": "TV network", "data_type": "VARCHAR(50)", "sample_values": ["HBO", "NBC", "AMC", "Netflix"]},
                {"name": "total_viewers_millions", "description": "Total viewers in millions", "data_type": "DECIMAL(6,2)", "sample_values": [12.50, 8.30, 15.75]},
                {"name": "rating_18_49", "description": "Rating among adults 18-49", "data_type": "DECIMAL(4,2)", "sample_values": [4.5, 3.2, 6.8]},
                {"name": "share_18_49", "description": "Share percentage among adults 18-49", "data_type": "DECIMAL(4,1)", "sample_values": [12.5, 8.3, 18.7]},
                {"name": "season_number", "description": "Season number", "data_type": "INTEGER", "sample_values": [1, 5, 8]},
                {"name": "episode_number", "description": "Episode number in season", "data_type": "INTEGER", "sample_values": [1, 10, 16]},
            ]
        },
        {
            "vendor_email": "sales@cinemetrics.io",
            "title": "Audience Demographics and Preferences",
            "status": "active",
            "visibility": "public",
            "description": "Movie and TV audience demographic breakdowns, sentiment analysis, and preference trends",
            "domain": "Entertainment & Media",
            "dataset_type": "Survey",
            "granularity": "Content-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["demographics", "audience", "preferences", "sentiment"],
            "entities": ["audiences", "content", "demographics"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Weekly"},
            "geographic_coverage": {"countries": ["US", "UK", "CA"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "content_id", "description": "Movie or show identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "content_title", "description": "Movie or show title", "data_type": "VARCHAR(300)", "sample_values": ["Barbie", "The Last of Us", "Oppenheimer"]},
                {"name": "content_type", "description": "Type of content", "data_type": "VARCHAR(20)", "sample_values": ["movie", "tv_series"]},
                {"name": "survey_date", "description": "Survey date", "data_type": "DATE", "sample_values": ["2023-08-01", "2024-01-15"]},
                {"name": "age_group", "description": "Audience age group", "data_type": "VARCHAR(20)", "sample_values": ["18-24", "25-34", "35-49", "50+"]},
                {"name": "gender", "description": "Audience gender", "data_type": "VARCHAR(20)", "sample_values": ["Male", "Female", "Non-binary", "All"]},
                {"name": "audience_share_pct", "description": "Percentage of audience in demographic", "data_type": "DECIMAL(5,2)", "sample_values": [35.50, 42.30, 18.75]},
                {"name": "sentiment_score", "description": "Sentiment score (0-100)", "data_type": "INTEGER", "sample_values": [85, 72, 91]},
                {"name": "recommendation_pct", "description": "Percentage who would recommend", "data_type": "DECIMAL(5,2)", "sample_values": [85.50, 72.30, 91.75]},
            ]
        },
        
        # ============ ENTERTAINMENT & MEDIA DOMAIN - GameLytics Pro (Vendor 3) ============
        # RELATED DATASETS: Game Sessions + Player Profiles (join on player_id), In-Game Purchases + Player Profiles (join on player_id)
        {
            "vendor_email": "info@gamelytics.net",
            "title": "Video Game Player Sessions and Engagement",
            "status": "active",
            "visibility": "public",
            "description": "Player session data including playtime, progression, achievements, and engagement metrics across gaming platforms",
            "domain": "Entertainment & Media",
            "dataset_type": "Time-series",
            "granularity": "Session-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["gaming", "player sessions", "engagement", "playtime"],
            "entities": ["players", "sessions", "games"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "UK", "JP", "KR", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "session_id", "description": "Unique session identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "player_id", "description": "Anonymized player identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "game_id", "description": "Game identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "game_title", "description": "Game name", "data_type": "VARCHAR(200)", "sample_values": ["Fortnite", "Call of Duty", "League of Legends"]},
                {"name": "session_start", "description": "Session start timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "session_duration_minutes", "description": "Session length in minutes", "data_type": "INTEGER", "sample_values": [45, 120, 30]},
                {"name": "platform", "description": "Gaming platform", "data_type": "VARCHAR(50)", "sample_values": ["PlayStation 5", "Xbox Series X", "PC", "Mobile"]},
                {"name": "achievements_earned", "description": "Number of achievements earned", "data_type": "INTEGER", "sample_values": [3, 0, 1]},
                {"name": "level_reached", "description": "Highest level reached in session", "data_type": "INTEGER", "sample_values": [25, 50, 100]},
                {"name": "multiplayer", "description": "Whether session included multiplayer", "data_type": "BOOLEAN", "sample_values": [True, False, True]},
            ]
        },
        {
            "vendor_email": "info@gamelytics.net",
            "title": "Player Profile and Demographic Data",
            "status": "active",
            "visibility": "public",
            "description": "Player profiles including demographics, preferences, spending patterns, and lifetime value metrics",
            "domain": "Entertainment & Media",
            "dataset_type": "Profile",
            "granularity": "Player-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["player profiles", "demographics", "spending", "lifetime value"],
            "entities": ["players", "profiles"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Updated continuously"},
            "geographic_coverage": {"countries": ["US", "UK", "JP", "KR", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "player_id", "description": "Anonymized player identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "account_created_date", "description": "Account creation date", "data_type": "DATE", "sample_values": ["2020-03-15", "2021-07-22"]},
                {"name": "country", "description": "Player country", "data_type": "VARCHAR(3)", "sample_values": ["USA", "GBR", "JPN", "KOR"]},
                {"name": "age_group", "description": "Player age group", "data_type": "VARCHAR(20)", "sample_values": ["13-17", "18-24", "25-34", "35+"]},
                {"name": "gender", "description": "Player gender", "data_type": "VARCHAR(20)", "sample_values": ["Male", "Female", "Non-binary", "Prefer not to say"]},
                {"name": "total_playtime_hours", "description": "Lifetime playtime in hours", "data_type": "INTEGER", "sample_values": [500, 1200, 2500]},
                {"name": "total_spent_usd", "description": "Lifetime spending in USD", "data_type": "DECIMAL(10,2)", "sample_values": [150.00, 450.00, 1200.00]},
                {"name": "preferred_genre", "description": "Most played game genre", "data_type": "VARCHAR(50)", "sample_values": ["FPS", "RPG", "Strategy", "Sports"]},
                {"name": "subscription_tier", "description": "Subscription level", "data_type": "VARCHAR(50)", "sample_values": ["Free", "Basic", "Premium", "Ultimate"]},
                {"name": "lifetime_value_usd", "description": "Estimated lifetime value", "data_type": "DECIMAL(10,2)", "sample_values": [200.00, 600.00, 1500.00]},
            ]
        },
        {
            "vendor_email": "info@gamelytics.net",
            "title": "In-Game Purchases and Monetization Data",
            "status": "active",
            "visibility": "public",
            "description": "In-game purchase transactions, virtual goods sales, and monetization metrics across gaming titles",
            "domain": "Entertainment & Media",
            "dataset_type": "Transactional",
            "granularity": "Transaction-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["in-game purchases", "monetization", "virtual goods", "transactions"],
            "entities": ["players", "transactions", "items"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "UK", "JP", "KR", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "transaction_id", "description": "Unique transaction identifier", "data_type": "UUID", "sample_values": ["d4e5f6a7-b8c9-0123-def1-234567890123"]},
                {"name": "player_id", "description": "Anonymized player identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "game_id", "description": "Game identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "transaction_date", "description": "Purchase date", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "item_name", "description": "Purchased item name", "data_type": "VARCHAR(200)", "sample_values": ["Battle Pass", "Legendary Skin", "Loot Box"]},
                {"name": "item_category", "description": "Item category", "data_type": "VARCHAR(50)", "sample_values": ["Subscription", "Cosmetic", "Power-up", "Currency"]},
                {"name": "price_usd", "description": "Purchase price in USD", "data_type": "DECIMAL(8,2)", "sample_values": [9.99, 19.99, 4.99]},
                {"name": "payment_method", "description": "Payment method used", "data_type": "VARCHAR(50)", "sample_values": ["Credit Card", "PayPal", "In-game Currency", "Gift Card"]},
                {"name": "platform", "description": "Platform of purchase", "data_type": "VARCHAR(50)", "sample_values": ["PlayStation 5", "Xbox Series X", "PC", "Mobile"]},
                {"name": "refunded", "description": "Whether transaction was refunded", "data_type": "BOOLEAN", "sample_values": [False, False, True]},
            ]
        },
        {
            "vendor_email": "info@gamelytics.net",
            "title": "Esports Tournament and Competition Data",
            "status": "active",
            "visibility": "public",
            "description": "Esports tournament results, prize pools, team performance, and competitive gaming analytics",
            "domain": "Entertainment & Media",
            "dataset_type": "Event-based",
            "granularity": "Match-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["esports", "tournaments", "competitions", "teams"],
            "entities": ["tournaments", "teams", "players", "matches"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "KR", "CN", "EU", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "tournament_id", "description": "Unique tournament identifier", "data_type": "UUID", "sample_values": ["e5f6a7b8-c9d0-1234-ef12-345678901234"]},
                {"name": "tournament_name", "description": "Tournament name", "data_type": "VARCHAR(200)", "sample_values": ["The International", "League Worlds", "CS:GO Major"]},
                {"name": "game_title", "description": "Game being competed in", "data_type": "VARCHAR(200)", "sample_values": ["Dota 2", "League of Legends", "Counter-Strike"]},
                {"name": "event_date", "description": "Event date", "data_type": "DATE", "sample_values": ["2023-10-15", "2024-08-20"]},
                {"name": "location", "description": "Tournament location", "data_type": "VARCHAR(100)", "sample_values": ["Seattle, USA", "Seoul, South Korea", "Shanghai, China"]},
                {"name": "prize_pool_usd", "description": "Total prize pool in USD", "data_type": "DECIMAL(15,2)", "sample_values": [40000000.00, 2500000.00, 1000000.00]},
                {"name": "winning_team", "description": "Tournament winner", "data_type": "VARCHAR(100)", "sample_values": ["Team Liquid", "T1", "FaZe Clan"]},
                {"name": "first_place_prize_usd", "description": "First place prize in USD", "data_type": "DECIMAL(12,2)", "sample_values": [18000000.00, 1000000.00, 500000.00]},
                {"name": "viewership_peak", "description": "Peak concurrent viewers", "data_type": "INTEGER", "sample_values": [5000000, 2500000, 1200000]},
                {"name": "matches_played", "description": "Total matches in tournament", "data_type": "INTEGER", "sample_values": [120, 85, 60]},
            ]
        },
        {
            "vendor_email": "info@gamelytics.net",
            "title": "Game Performance and Technical Metrics",
            "status": "active",
            "visibility": "public",
            "description": "Game performance data including crash rates, load times, frame rates, and technical issue tracking",
            "domain": "Entertainment & Media",
            "dataset_type": "Telemetry",
            "granularity": "Session-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["performance", "technical metrics", "crashes", "optimization"],
            "entities": ["sessions", "devices", "games"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "session_id", "description": "Unique session identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "game_id", "description": "Game identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "session_date", "description": "Session date", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00"]},
                {"name": "platform", "description": "Gaming platform", "data_type": "VARCHAR(50)", "sample_values": ["PlayStation 5", "Xbox Series X", "PC", "Mobile"]},
                {"name": "average_fps", "description": "Average frames per second", "data_type": "DECIMAL(6,2)", "sample_values": [60.00, 120.00, 30.00]},
                {"name": "load_time_seconds", "description": "Average load time in seconds", "data_type": "DECIMAL(6,2)", "sample_values": [15.50, 8.30, 25.75]},
                {"name": "crashed", "description": "Whether session ended in crash", "data_type": "BOOLEAN", "sample_values": [False, False, True]},
                {"name": "latency_ms", "description": "Network latency in milliseconds", "data_type": "INTEGER", "sample_values": [25, 50, 150]},
                {"name": "gpu_model", "description": "Graphics card model", "data_type": "VARCHAR(100)", "sample_values": ["NVIDIA RTX 4090", "AMD RX 7900", "Integrated"]},
            ]
        },
        
        # ============ ENTERTAINMENT & MEDIA DOMAIN - SocialData Insights (Vendor 4) ============
        # RELATED DATASETS: Social Media Posts + Influencer Profiles (join on influencer_id), Post Engagement + Influencer Profiles (join on influencer_id)
        {
            "vendor_email": "contact@socialdata.ai",
            "title": "Social Media Post Performance and Engagement",
            "status": "active",
            "visibility": "public",
            "description": "Social media post metrics including likes, shares, comments, reach, and engagement rates across platforms",
            "domain": "Entertainment & Media",
            "dataset_type": "Time-series",
            "granularity": "Post-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["social media", "engagement", "posts", "reach"],
            "entities": ["posts", "users", "platforms"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "UK", "CA", "AU", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "post_id", "description": "Unique post identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "influencer_id", "description": "Account/influencer identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "platform", "description": "Social media platform", "data_type": "VARCHAR(50)", "sample_values": ["Instagram", "TikTok", "Twitter/X", "Facebook"]},
                {"name": "post_date", "description": "Post timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "content_type", "description": "Type of content", "data_type": "VARCHAR(50)", "sample_values": ["photo", "video", "carousel", "story", "reel"]},
                {"name": "likes", "description": "Number of likes", "data_type": "INTEGER", "sample_values": [150000, 85000, 450000]},
                {"name": "comments", "description": "Number of comments", "data_type": "INTEGER", "sample_values": [5000, 3500, 12000]},
                {"name": "shares", "description": "Number of shares/retweets", "data_type": "INTEGER", "sample_values": [2500, 1800, 8000]},
                {"name": "reach", "description": "Total reach/impressions", "data_type": "INTEGER", "sample_values": [5000000, 2500000, 15000000]},
                {"name": "engagement_rate_pct", "description": "Engagement rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [5.50, 8.30, 3.75]},
            ]
        },
        {
            "vendor_email": "contact@socialdata.ai",
            "title": "Influencer Profile and Audience Analytics",
            "status": "active",
            "visibility": "public",
            "description": "Influencer profiles with follower counts, audience demographics, engagement trends, and credibility scores",
            "domain": "Entertainment & Media",
            "dataset_type": "Profile",
            "granularity": "Influencer-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["influencers", "followers", "audience", "demographics"],
            "entities": ["influencers", "audiences", "platforms"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "UK", "CA", "AU", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "influencer_id", "description": "Account/influencer identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "platform", "description": "Social media platform", "data_type": "VARCHAR(50)", "sample_values": ["Instagram", "TikTok", "YouTube", "Twitter/X"]},
                {"name": "username", "description": "Account username", "data_type": "VARCHAR(100)", "sample_values": ["@influencer_name", "@content_creator", "@celebrity"]},
                {"name": "follower_count", "description": "Total followers", "data_type": "INTEGER", "sample_values": [5000000, 2500000, 15000000]},
                {"name": "following_count", "description": "Total following", "data_type": "INTEGER", "sample_values": [1000, 500, 250]},
                {"name": "category", "description": "Influencer category", "data_type": "VARCHAR(50)", "sample_values": ["Fashion", "Fitness", "Gaming", "Food", "Travel"]},
                {"name": "average_engagement_rate", "description": "Average engagement rate", "data_type": "DECIMAL(5,2)", "sample_values": [5.50, 8.30, 3.75]},
                {"name": "verified", "description": "Whether account is verified", "data_type": "BOOLEAN", "sample_values": [True, True, False]},
                {"name": "audience_country_top", "description": "Top audience country", "data_type": "VARCHAR(3)", "sample_values": ["USA", "GBR", "BRA"]},
                {"name": "credibility_score", "description": "Influencer credibility score (0-100)", "data_type": "INTEGER", "sample_values": [85, 72, 91]},
            ]
        },
        {
            "vendor_email": "contact@socialdata.ai",
            "title": "Brand Campaign Performance and ROI",
            "status": "active",
            "visibility": "public",
            "description": "Influencer marketing campaign metrics, brand mentions, ROI tracking, and sponsorship performance data",
            "domain": "Entertainment & Media",
            "dataset_type": "Campaign",
            "granularity": "Campaign-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["campaigns", "brand marketing", "ROI", "sponsorships"],
            "entities": ["campaigns", "brands", "influencers"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "UK", "CA", "AU", "EU"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "campaign_id", "description": "Unique campaign identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "brand_name", "description": "Brand name", "data_type": "VARCHAR(200)", "sample_values": ["Nike", "Coca-Cola", "Apple"]},
                {"name": "influencer_id", "description": "Influencer identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "campaign_start_date", "description": "Campaign start date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-03-20"]},
                {"name": "campaign_end_date", "description": "Campaign end date", "data_type": "DATE", "sample_values": ["2024-02-15", "2024-04-20"]},
                {"name": "budget_usd", "description": "Campaign budget in USD", "data_type": "DECIMAL(12,2)", "sample_values": [50000.00, 150000.00, 500000.00]},
                {"name": "total_reach", "description": "Total campaign reach", "data_type": "INTEGER", "sample_values": [25000000, 15000000, 85000000]},
                {"name": "total_engagement", "description": "Total campaign engagement", "data_type": "INTEGER", "sample_values": [1500000, 850000, 5200000]},
                {"name": "conversions", "description": "Number of conversions tracked", "data_type": "INTEGER", "sample_values": [5000, 12000, 35000]},
                {"name": "roi_pct", "description": "Return on investment percentage", "data_type": "DECIMAL(6,2)", "sample_values": [250.00, 180.00, 450.00]},
            ]
        },
        {
            "vendor_email": "contact@socialdata.ai",
            "title": "Trending Topics and Viral Content Analysis",
            "status": "active",
            "visibility": "public",
            "description": "Real-time trending topics, hashtag performance, viral content tracking, and sentiment analysis",
            "domain": "Entertainment & Media",
            "dataset_type": "Time-series",
            "granularity": "Hourly",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["trending", "viral content", "hashtags", "sentiment"],
            "entities": ["hashtags", "topics", "content"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Hourly"},
            "geographic_coverage": {"countries": ["US", "UK", "CA", "AU", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "topic_id", "description": "Unique topic identifier", "data_type": "UUID", "sample_values": ["d4e5f6a7-b8c9-0123-def1-234567890123"]},
                {"name": "hashtag", "description": "Trending hashtag", "data_type": "VARCHAR(100)", "sample_values": ["#Oscars2024", "#TechNews", "#FitnessMotivation"]},
                {"name": "timestamp", "description": "Trending timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:00:00", "2024-02-20 18:00:00"]},
                {"name": "platform", "description": "Social media platform", "data_type": "VARCHAR(50)", "sample_values": ["Twitter/X", "Instagram", "TikTok"]},
                {"name": "mention_count", "description": "Number of mentions", "data_type": "INTEGER", "sample_values": [500000, 250000, 1200000]},
                {"name": "reach_estimate", "description": "Estimated reach", "data_type": "INTEGER", "sample_values": [50000000, 25000000, 120000000]},
                {"name": "sentiment_score", "description": "Sentiment score (-100 to 100)", "data_type": "INTEGER", "sample_values": [75, -25, 50]},
                {"name": "trending_rank", "description": "Trending rank position", "data_type": "INTEGER", "sample_values": [1, 5, 10]},
                {"name": "category", "description": "Topic category", "data_type": "VARCHAR(50)", "sample_values": ["Entertainment", "Sports", "News", "Technology"]},
            ]
        },
        {
            "vendor_email": "contact@socialdata.ai",
            "title": "Digital Publishing and Content Performance",
            "status": "active",
            "visibility": "public",
            "description": "Digital article performance, readership metrics, content engagement, and publishing analytics",
            "domain": "Entertainment & Media",
            "dataset_type": "Time-series",
            "granularity": "Article-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["digital publishing", "articles", "readership", "content performance"],
            "entities": ["articles", "publishers", "readers"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "UK", "CA", "AU"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "article_id", "description": "Unique article identifier", "data_type": "UUID", "sample_values": ["e5f6a7b8-c9d0-1234-ef12-345678901234"]},
                {"name": "publisher", "description": "Publisher name", "data_type": "VARCHAR(200)", "sample_values": ["New York Times", "The Guardian", "TechCrunch"]},
                {"name": "publish_date", "description": "Publication date", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 08:00:00", "2024-02-20 12:30:00"]},
                {"name": "category", "description": "Article category", "data_type": "VARCHAR(50)", "sample_values": ["News", "Opinion", "Technology", "Sports", "Entertainment"]},
                {"name": "pageviews", "description": "Total pageviews", "data_type": "INTEGER", "sample_values": [500000, 250000, 1200000]},
                {"name": "unique_visitors", "description": "Unique visitors", "data_type": "INTEGER", "sample_values": [400000, 200000, 1000000]},
                {"name": "average_time_on_page_seconds", "description": "Average time spent reading", "data_type": "INTEGER", "sample_values": [180, 240, 120]},
                {"name": "social_shares", "description": "Total social media shares", "data_type": "INTEGER", "sample_values": [5000, 12000, 25000]},
                {"name": "comments", "description": "Number of comments", "data_type": "INTEGER", "sample_values": [150, 350, 800]},
                {"name": "bounce_rate_pct", "description": "Bounce rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [35.50, 42.30, 28.75]},
            ]
        },
        
        # ============ SPORTS DOMAIN - SportStats Global (Vendor 1) ============
        # RELATED DATASETS: Game Results + Player Statistics (join on game_id/player_id), Team Standings + Team Performance (join on team_id)
        {
            "vendor_email": "data@sportstats.pro",
            "title": "Professional Sports Game Results and Scores",
            "status": "active",
            "visibility": "public",
            "description": "Comprehensive game results, scores, and match outcomes across NFL, NBA, MLB, NHL, and soccer leagues",
            "domain": "Sports",
            "dataset_type": "Time-series",
            "granularity": "Game-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["game results", "scores", "sports", "leagues"],
            "entities": ["games", "teams", "leagues"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "CA", "UK", "Global"], "regions": ["North America", "Europe", "Worldwide"]},
            "columns": [
                {"name": "game_id", "description": "Unique game identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "league", "description": "Sports league", "data_type": "VARCHAR(50)", "sample_values": ["NFL", "NBA", "MLB", "NHL", "Premier League"]},
                {"name": "season", "description": "Season year", "data_type": "VARCHAR(20)", "sample_values": ["2023-24", "2024", "2023"]},
                {"name": "game_date", "description": "Game date", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 19:00:00", "2024-02-20 13:00:00"]},
                {"name": "home_team_id", "description": "Home team identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "away_team_id", "description": "Away team identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "home_team_name", "description": "Home team name", "data_type": "VARCHAR(100)", "sample_values": ["Los Angeles Lakers", "New York Yankees", "Manchester United"]},
                {"name": "away_team_name", "description": "Away team name", "data_type": "VARCHAR(100)", "sample_values": ["Boston Celtics", "Boston Red Sox", "Liverpool"]},
                {"name": "home_score", "description": "Home team final score", "data_type": "INTEGER", "sample_values": [105, 28, 3]},
                {"name": "away_score", "description": "Away team final score", "data_type": "INTEGER", "sample_values": [98, 24, 1]},
                {"name": "attendance", "description": "Game attendance", "data_type": "INTEGER", "sample_values": [18500, 65000, 75000]},
            ]
        },
        {
            "vendor_email": "data@sportstats.pro",
            "title": "Player Statistics and Performance Metrics",
            "status": "active",
            "visibility": "public",
            "description": "Individual player statistics including points, assists, rebounds, goals, and performance metrics by game",
            "domain": "Sports",
            "dataset_type": "Time-series",
            "granularity": "Player-game-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["player stats", "performance", "athletes", "statistics"],
            "entities": ["players", "games", "teams"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "CA", "Global"], "regions": ["North America", "Worldwide"]},
            "columns": [
                {"name": "player_id", "description": "Unique player identifier", "data_type": "UUID", "sample_values": ["d4e5f6a7-b8c9-0123-def1-234567890123"]},
                {"name": "game_id", "description": "Game identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "player_name", "description": "Player full name", "data_type": "VARCHAR(100)", "sample_values": ["LeBron James", "Patrick Mahomes", "Lionel Messi"]},
                {"name": "team_id", "description": "Team identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "position", "description": "Player position", "data_type": "VARCHAR(50)", "sample_values": ["Forward", "Quarterback", "Midfielder", "Center"]},
                {"name": "minutes_played", "description": "Minutes or time played", "data_type": "DECIMAL(6,2)", "sample_values": [35.5, 48.0, 90.0]},
                {"name": "points_scored", "description": "Points, goals, or runs scored", "data_type": "INTEGER", "sample_values": [28, 3, 2]},
                {"name": "assists", "description": "Assists", "data_type": "INTEGER", "sample_values": [8, 2, 1]},
                {"name": "rebounds_or_tackles", "description": "Rebounds, tackles, or defensive stats", "data_type": "INTEGER", "sample_values": [10, 7, 5]},
                {"name": "performance_rating", "description": "Overall performance rating", "data_type": "DECIMAL(4,1)", "sample_values": [8.5, 7.2, 9.1]},
            ]
        },
        {
            "vendor_email": "data@sportstats.pro",
            "title": "Team Standings and Season Records",
            "status": "active",
            "visibility": "public",
            "description": "Team standings, win-loss records, rankings, and season performance across professional sports leagues",
            "domain": "Sports",
            "dataset_type": "Time-series",
            "granularity": "Daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["standings", "rankings", "records", "teams"],
            "entities": ["teams", "leagues", "seasons"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "CA", "Global"], "regions": ["North America", "Worldwide"]},
            "columns": [
                {"name": "team_id", "description": "Unique team identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "team_name", "description": "Team name", "data_type": "VARCHAR(100)", "sample_values": ["Boston Celtics", "Kansas City Chiefs", "Real Madrid"]},
                {"name": "league", "description": "Sports league", "data_type": "VARCHAR(50)", "sample_values": ["NBA", "NFL", "La Liga", "Premier League"]},
                {"name": "season", "description": "Season year", "data_type": "VARCHAR(20)", "sample_values": ["2023-24", "2024", "2023"]},
                {"name": "date", "description": "Standings date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-03-20"]},
                {"name": "wins", "description": "Number of wins", "data_type": "INTEGER", "sample_values": [45, 12, 25]},
                {"name": "losses", "description": "Number of losses", "data_type": "INTEGER", "sample_values": [15, 4, 8]},
                {"name": "win_percentage", "description": "Win percentage", "data_type": "DECIMAL(5,3)", "sample_values": [0.750, 0.857, 0.758]},
                {"name": "points_for", "description": "Total points scored", "data_type": "INTEGER", "sample_values": [6500, 425, 85]},
                {"name": "points_against", "description": "Total points allowed", "data_type": "INTEGER", "sample_values": [5800, 320, 42]},
                {"name": "rank", "description": "Current rank in league/division", "data_type": "INTEGER", "sample_values": [1, 2, 3]},
            ]
        },
        {
            "vendor_email": "data@sportstats.pro",
            "title": "Historical Sports Records and Archives",
            "status": "active",
            "visibility": "public",
            "description": "Historical sports data, records, championships, and archival statistics dating back decades",
            "domain": "Sports",
            "dataset_type": "Reference",
            "granularity": "Event-level",
            "pricing_model": "One-time Purchase",
            "license": "Commercial Use Allowed",
            "topics": ["history", "records", "championships", "archives"],
            "entities": ["teams", "players", "championships"],
            "temporal_coverage": {"start_date": "1900-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "record_id", "description": "Unique record identifier", "data_type": "UUID", "sample_values": ["e5f6a7b8-c9d0-1234-ef12-345678901234"]},
                {"name": "record_type", "description": "Type of record", "data_type": "VARCHAR(100)", "sample_values": ["Championship", "Individual Record", "Team Record"]},
                {"name": "sport", "description": "Sport", "data_type": "VARCHAR(50)", "sample_values": ["Basketball", "Football", "Baseball", "Soccer"]},
                {"name": "year", "description": "Year of record", "data_type": "INTEGER", "sample_values": [1995, 2008, 2023]},
                {"name": "player_or_team", "description": "Player or team name", "data_type": "VARCHAR(200)", "sample_values": ["Michael Jordan", "Chicago Bulls", "Brazil National Team"]},
                {"name": "achievement", "description": "Achievement description", "data_type": "VARCHAR(500)", "sample_values": ["NBA Championship", "Most points in a season", "World Cup Victory"]},
                {"name": "value", "description": "Numeric value of record", "data_type": "DECIMAL(10,2)", "sample_values": [100.00, 72.00, 7.00]},
                {"name": "league", "description": "League or competition", "data_type": "VARCHAR(100)", "sample_values": ["NBA", "NFL", "FIFA World Cup", "Premier League"]},
                {"name": "location", "description": "Location of achievement", "data_type": "VARCHAR(200)", "sample_values": ["Chicago, IL", "New York, NY", "Rio de Janeiro, Brazil"]},
            ]
        },
        {
            "vendor_email": "data@sportstats.pro",
            "title": "College and Amateur Sports Statistics",
            "status": "active",
            "visibility": "public",
            "description": "NCAA and amateur sports statistics including college basketball, football, and Olympic sports data",
            "domain": "Sports",
            "dataset_type": "Time-series",
            "granularity": "Game-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["college sports", "NCAA", "amateur", "Olympics"],
            "entities": ["teams", "players", "colleges"],
            "temporal_coverage": {"start_date": "2010-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US"], "regions": ["North America"]},
            "columns": [
                {"name": "game_id", "description": "Unique game identifier", "data_type": "UUID", "sample_values": ["f6a7b8c9-d0e1-2345-f123-456789012345"]},
                {"name": "sport", "description": "Sport name", "data_type": "VARCHAR(50)", "sample_values": ["Basketball", "Football", "Soccer", "Track & Field"]},
                {"name": "competition", "description": "Competition name", "data_type": "VARCHAR(100)", "sample_values": ["NCAA Division I", "March Madness", "College Football Playoff"]},
                {"name": "game_date", "description": "Game or event date", "data_type": "DATE", "sample_values": ["2024-03-15", "2024-11-20"]},
                {"name": "home_team", "description": "Home team/school name", "data_type": "VARCHAR(200)", "sample_values": ["Duke University", "Alabama", "UCLA"]},
                {"name": "away_team", "description": "Away team/school name", "data_type": "VARCHAR(200)", "sample_values": ["UNC", "Georgia", "USC"]},
                {"name": "home_score", "description": "Home team score", "data_type": "INTEGER", "sample_values": [78, 35, 2]},
                {"name": "away_score", "description": "Away team score", "data_type": "INTEGER", "sample_values": [72, 28, 1]},
                {"name": "conference", "description": "Athletic conference", "data_type": "VARCHAR(100)", "sample_values": ["ACC", "SEC", "Big Ten", "Pac-12"]},
                {"name": "attendance", "description": "Event attendance", "data_type": "INTEGER", "sample_values": [9500, 102000, 35000]},
            ]
        },
        
        # ============ SPORTS DOMAIN - OddsData Analytics (Vendor 2) ============
        # RELATED DATASETS: Betting Odds + Game Results (join on game_id), Betting Lines + Wager Volume (join on game_id)
        {
            "vendor_email": "sales@oddsdata.io",
            "title": "Sports Betting Odds and Lines",
            "status": "active",
            "visibility": "public",
            "description": "Real-time and historical betting odds, point spreads, moneylines, and over/under lines from global sportsbooks",
            "domain": "Sports",
            "dataset_type": "Time-series",
            "granularity": "Minute-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["betting odds", "sports betting", "lines", "spreads"],
            "entities": ["games", "sportsbooks", "odds"],
            "temporal_coverage": {"start_date": "2018-01-01", "end_date": "2024-12-31", "frequency": "Minute-level"},
            "geographic_coverage": {"countries": ["US", "UK", "Global"], "regions": ["North America", "Europe", "Worldwide"]},
            "columns": [
                {"name": "odds_id", "description": "Unique odds record identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "game_id", "description": "Game identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "sportsbook", "description": "Sportsbook name", "data_type": "VARCHAR(100)", "sample_values": ["DraftKings", "FanDuel", "BetMGM", "Bet365"]},
                {"name": "timestamp", "description": "Odds timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 18:45:00", "2024-02-20 14:30:00"]},
                {"name": "home_team", "description": "Home team name", "data_type": "VARCHAR(100)", "sample_values": ["Los Angeles Lakers", "Kansas City Chiefs"]},
                {"name": "away_team", "description": "Away team name", "data_type": "VARCHAR(100)", "sample_values": ["Boston Celtics", "San Francisco 49ers"]},
                {"name": "home_moneyline", "description": "Home team moneyline odds", "data_type": "INTEGER", "sample_values": [-150, -200, 120]},
                {"name": "away_moneyline", "description": "Away team moneyline odds", "data_type": "INTEGER", "sample_values": [130, 170, -140]},
                {"name": "point_spread", "description": "Point spread", "data_type": "DECIMAL(4,1)", "sample_values": [-3.5, 7.0, -1.5]},
                {"name": "over_under", "description": "Total points over/under line", "data_type": "DECIMAL(5,1)", "sample_values": [220.5, 48.5, 2.5]},
            ]
        },
        {
            "vendor_email": "sales@oddsdata.io",
            "title": "Betting Market Movement and Line History",
            "status": "active",
            "visibility": "public",
            "description": "Historical betting line movements, odds changes, and market dynamics tracking across sportsbooks",
            "domain": "Sports",
            "dataset_type": "Time-series",
            "granularity": "Minute-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["line movement", "odds history", "market dynamics", "betting trends"],
            "entities": ["games", "odds", "markets"],
            "temporal_coverage": {"start_date": "2018-01-01", "end_date": "2024-12-31", "frequency": "Minute-level"},
            "geographic_coverage": {"countries": ["US", "UK", "Global"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "movement_id", "description": "Unique movement record identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "game_id", "description": "Game identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "timestamp", "description": "Movement timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 18:45:00", "2024-02-20 14:30:00"]},
                {"name": "bet_type", "description": "Type of bet", "data_type": "VARCHAR(50)", "sample_values": ["Moneyline", "Spread", "Total", "Prop"]},
                {"name": "opening_line", "description": "Opening line value", "data_type": "DECIMAL(6,2)", "sample_values": [-150.00, -3.5, 220.5]},
                {"name": "current_line", "description": "Current line value", "data_type": "DECIMAL(6,2)", "sample_values": [-175.00, -4.5, 218.5]},
                {"name": "line_movement", "description": "Movement amount", "data_type": "DECIMAL(6,2)", "sample_values": [-25.00, -1.0, -2.0]},
                {"name": "movement_pct", "description": "Percentage movement", "data_type": "DECIMAL(5,2)", "sample_values": [16.67, 28.57, 0.91]},
                {"name": "sharp_money_indicator", "description": "Sharp money detected flag", "data_type": "BOOLEAN", "sample_values": [True, False, True]},
                {"name": "steam_move", "description": "Steam move detected flag", "data_type": "BOOLEAN", "sample_values": [False, True, False]},
            ]
        },
        {
            "vendor_email": "sales@oddsdata.io",
            "title": "Wagering Volume and Handle Data",
            "status": "active",
            "visibility": "public",
            "description": "Sports betting handle, wagering volume, and betting percentages by game and market",
            "domain": "Sports",
            "dataset_type": "Time-series",
            "granularity": "Game-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["betting volume", "handle", "wagering", "betting percentages"],
            "entities": ["games", "wagers", "markets"],
            "temporal_coverage": {"start_date": "2018-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "UK"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "handle_id", "description": "Unique handle record identifier", "data_type": "UUID", "sample_values": ["d4e5f6a7-b8c9-0123-def1-234567890123"]},
                {"name": "game_id", "description": "Game identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "market", "description": "Betting market", "data_type": "VARCHAR(50)", "sample_values": ["Moneyline", "Spread", "Total", "Props"]},
                {"name": "total_handle_usd", "description": "Total wagering handle in USD", "data_type": "DECIMAL(15,2)", "sample_values": [5000000.00, 2500000.00, 8500000.00]},
                {"name": "bet_count", "description": "Number of bets placed", "data_type": "INTEGER", "sample_values": [150000, 85000, 250000]},
                {"name": "home_bet_pct", "description": "Percentage of bets on home team", "data_type": "DECIMAL(5,2)", "sample_values": [55.50, 42.30, 68.75]},
                {"name": "away_bet_pct", "description": "Percentage of bets on away team", "data_type": "DECIMAL(5,2)", "sample_values": [44.50, 57.70, 31.25]},
                {"name": "home_money_pct", "description": "Percentage of money on home team", "data_type": "DECIMAL(5,2)", "sample_values": [62.50, 38.30, 72.75]},
                {"name": "away_money_pct", "description": "Percentage of money on away team", "data_type": "DECIMAL(5,2)", "sample_values": [37.50, 61.70, 27.25]},
                {"name": "average_bet_size_usd", "description": "Average bet size", "data_type": "DECIMAL(8,2)", "sample_values": [33.33, 29.41, 34.00]},
            ]
        },
        {
            "vendor_email": "sales@oddsdata.io",
            "title": "Player Prop Betting Markets",
            "status": "active",
            "visibility": "public",
            "description": "Player proposition betting lines including points, rebounds, passing yards, and performance props",
            "domain": "Sports",
            "dataset_type": "Time-series",
            "granularity": "Player-game-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["prop bets", "player props", "betting markets", "propositions"],
            "entities": ["players", "games", "props"],
            "temporal_coverage": {"start_date": "2018-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "UK"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "prop_id", "description": "Unique prop bet identifier", "data_type": "UUID", "sample_values": ["e5f6a7b8-c9d0-1234-ef12-345678901234"]},
                {"name": "game_id", "description": "Game identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "player_name", "description": "Player name", "data_type": "VARCHAR(100)", "sample_values": ["LeBron James", "Patrick Mahomes", "Connor McDavid"]},
                {"name": "prop_type", "description": "Type of proposition", "data_type": "VARCHAR(100)", "sample_values": ["Points", "Passing Yards", "Rebounds", "Goals", "Assists"]},
                {"name": "line", "description": "Prop line value", "data_type": "DECIMAL(6,1)", "sample_values": [25.5, 275.5, 8.5, 0.5, 2.5]},
                {"name": "over_odds", "description": "Odds for over", "data_type": "INTEGER", "sample_values": [-110, -120, 105]},
                {"name": "under_odds", "description": "Odds for under", "data_type": "INTEGER", "sample_values": [-110, 100, -125]},
                {"name": "sportsbook", "description": "Sportsbook offering prop", "data_type": "VARCHAR(100)", "sample_values": ["DraftKings", "FanDuel", "BetMGM"]},
                {"name": "actual_result", "description": "Actual result if game completed", "data_type": "DECIMAL(6,1)", "sample_values": [28.0, 312.0, 7.0]},
                {"name": "bet_outcome", "description": "Outcome of bet", "data_type": "VARCHAR(20)", "sample_values": ["Over", "Under", "Push", "Pending"]},
            ]
        },
        {
            "vendor_email": "sales@oddsdata.io",
            "title": "Futures and Season-Long Betting Odds",
            "status": "active",
            "visibility": "public",
            "description": "Futures betting odds including championship winners, MVP awards, and season-long proposition markets",
            "domain": "Sports",
            "dataset_type": "Time-series",
            "granularity": "Daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["futures betting", "championships", "MVP", "season odds"],
            "entities": ["teams", "players", "awards"],
            "temporal_coverage": {"start_date": "2018-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "UK", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "futures_id", "description": "Unique futures bet identifier", "data_type": "UUID", "sample_values": ["f6a7b8c9-d0e1-2345-f123-456789012345"]},
                {"name": "market_type", "description": "Type of futures market", "data_type": "VARCHAR(100)", "sample_values": ["Championship Winner", "MVP", "Rookie of the Year", "Division Winner"]},
                {"name": "sport", "description": "Sport", "data_type": "VARCHAR(50)", "sample_values": ["Basketball", "Football", "Baseball", "Hockey"]},
                {"name": "season", "description": "Season year", "data_type": "VARCHAR(20)", "sample_values": ["2023-24", "2024", "2024-25"]},
                {"name": "date", "description": "Odds date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-06-20"]},
                {"name": "team_or_player", "description": "Team or player name", "data_type": "VARCHAR(200)", "sample_values": ["Boston Celtics", "Nikola Jokic", "Kansas City Chiefs"]},
                {"name": "odds", "description": "Betting odds", "data_type": "INTEGER", "sample_values": [450, 300, 1200]},
                {"name": "implied_probability_pct", "description": "Implied probability percentage", "data_type": "DECIMAL(5,2)", "sample_values": [18.18, 25.00, 7.69]},
                {"name": "sportsbook", "description": "Sportsbook", "data_type": "VARCHAR(100)", "sample_values": ["DraftKings", "FanDuel", "Caesars"]},
            ]
        },
        
        # ============ SPORTS DOMAIN - AthleteMetrics Performance (Vendor 3) ============
        # RELATED DATASETS: Athlete Biometrics + Training Load (join on athlete_id), Performance Tests + Injury Records (join on athlete_id)
        {
            "vendor_email": "info@athletemetrics.com",
            "title": "Athlete Biometric and Physical Performance Data",
            "status": "active",
            "visibility": "public",
            "description": "Athlete biometric measurements, body composition, fitness testing, and physical performance metrics",
            "domain": "Sports",
            "dataset_type": "Time-series",
            "granularity": "Athlete-level",
            "pricing_model": "Subscription",
            "license": "Research Use Only",
            "topics": ["biometrics", "athlete performance", "fitness", "body composition"],
            "entities": ["athletes", "measurements", "tests"],
            "temporal_coverage": {"start_date": "2018-01-01", "end_date": "2024-12-31", "frequency": "Weekly"},
            "geographic_coverage": {"countries": ["US", "CA", "EU"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "athlete_id", "description": "Anonymized athlete identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "measurement_date", "description": "Measurement date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "sport", "description": "Sport", "data_type": "VARCHAR(50)", "sample_values": ["Basketball", "Football", "Soccer", "Track"]},
                {"name": "position", "description": "Player position", "data_type": "VARCHAR(50)", "sample_values": ["Forward", "Quarterback", "Midfielder"]},
                {"name": "height_cm", "description": "Height in centimeters", "data_type": "DECIMAL(5,2)", "sample_values": [198.12, 188.50, 175.26]},
                {"name": "weight_kg", "description": "Weight in kilograms", "data_type": "DECIMAL(5,2)", "sample_values": [95.50, 102.30, 78.75]},
                {"name": "body_fat_pct", "description": "Body fat percentage", "data_type": "DECIMAL(4,2)", "sample_values": [8.50, 12.30, 6.75]},
                {"name": "vo2_max", "description": "VO2 max (ml/kg/min)", "data_type": "DECIMAL(5,2)", "sample_values": [55.50, 62.30, 68.75]},
                {"name": "vertical_jump_cm", "description": "Vertical jump in centimeters", "data_type": "DECIMAL(5,2)", "sample_values": [75.50, 82.30, 68.75]},
                {"name": "sprint_time_40yd_sec", "description": "40-yard dash time in seconds", "data_type": "DECIMAL(4,2)", "sample_values": [4.45, 4.38, 4.62]},
            ]
        },
        {
            "vendor_email": "info@athletemetrics.com",
            "title": "Training Load and Workload Monitoring",
            "status": "active",
            "visibility": "public",
            "description": "Athlete training load, workload metrics, GPS tracking, and practice intensity data",
            "domain": "Sports",
            "dataset_type": "Time-series",
            "granularity": "Session-level",
            "pricing_model": "Subscription",
            "license": "Research Use Only",
            "topics": ["training load", "workload", "GPS tracking", "practice intensity"],
            "entities": ["athletes", "sessions", "workload"],
            "temporal_coverage": {"start_date": "2018-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "CA", "EU"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "session_id", "description": "Unique training session identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "athlete_id", "description": "Anonymized athlete identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "session_date", "description": "Training session date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "session_type", "description": "Type of training session", "data_type": "VARCHAR(50)", "sample_values": ["Practice", "Game", "Recovery", "Strength Training"]},
                {"name": "duration_minutes", "description": "Session duration in minutes", "data_type": "INTEGER", "sample_values": [90, 120, 45]},
                {"name": "distance_covered_km", "description": "Total distance covered in kilometers", "data_type": "DECIMAL(6,2)", "sample_values": [8.50, 12.30, 5.75]},
                {"name": "high_speed_running_km", "description": "High-speed running distance", "data_type": "DECIMAL(5,2)", "sample_values": [1.50, 2.30, 0.75]},
                {"name": "sprint_count", "description": "Number of sprints", "data_type": "INTEGER", "sample_values": [15, 22, 8]},
                {"name": "training_load_au", "description": "Training load (arbitrary units)", "data_type": "INTEGER", "sample_values": [450, 680, 220]},
                {"name": "acute_chronic_ratio", "description": "Acute to chronic workload ratio", "data_type": "DECIMAL(4,2)", "sample_values": [1.25, 0.85, 1.50]},
            ]
        },
        {
            "vendor_email": "info@athletemetrics.com",
            "title": "Injury Tracking and Medical Records",
            "status": "active",
            "visibility": "public",
            "description": "Athlete injury history, medical records, recovery timelines, and return-to-play data",
            "domain": "Sports",
            "dataset_type": "Event-based",
            "granularity": "Injury-level",
            "pricing_model": "Subscription",
            "license": "Research Use Only",
            "topics": ["injuries", "medical records", "recovery", "return to play"],
            "entities": ["athletes", "injuries", "medical"],
            "temporal_coverage": {"start_date": "2018-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "CA", "EU"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "injury_id", "description": "Unique injury record identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "athlete_id", "description": "Anonymized athlete identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "injury_date", "description": "Date of injury", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-03-20"]},
                {"name": "injury_type", "description": "Type of injury", "data_type": "VARCHAR(100)", "sample_values": ["ACL Tear", "Ankle Sprain", "Hamstring Strain", "Concussion"]},
                {"name": "body_part", "description": "Affected body part", "data_type": "VARCHAR(50)", "sample_values": ["Knee", "Ankle", "Hamstring", "Head"]},
                {"name": "severity", "description": "Injury severity", "data_type": "VARCHAR(20)", "sample_values": ["Minor", "Moderate", "Major", "Season-ending"]},
                {"name": "games_missed", "description": "Number of games missed", "data_type": "INTEGER", "sample_values": [0, 5, 25, 60]},
                {"name": "return_date", "description": "Return to play date", "data_type": "DATE", "sample_values": ["2024-01-20", "2024-05-15"]},
                {"name": "recovery_days", "description": "Days to recovery", "data_type": "INTEGER", "sample_values": [5, 60, 180]},
                {"name": "surgery_required", "description": "Whether surgery was required", "data_type": "BOOLEAN", "sample_values": [False, True, False]},
            ]
        },
        {
            "vendor_email": "info@athletemetrics.com",
            "title": "Sleep and Recovery Monitoring",
            "status": "active",
            "visibility": "public",
            "description": "Athlete sleep quality, recovery metrics, heart rate variability, and wellness data",
            "domain": "Sports",
            "dataset_type": "Time-series",
            "granularity": "Daily",
            "pricing_model": "Subscription",
            "license": "Research Use Only",
            "topics": ["sleep", "recovery", "wellness", "heart rate variability"],
            "entities": ["athletes", "sleep", "recovery"],
            "temporal_coverage": {"start_date": "2018-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "CA", "EU"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "athlete_id", "description": "Anonymized athlete identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "date", "description": "Monitoring date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "sleep_duration_hours", "description": "Total sleep duration in hours", "data_type": "DECIMAL(4,2)", "sample_values": [7.50, 8.30, 6.75]},
                {"name": "sleep_quality_score", "description": "Sleep quality score (0-100)", "data_type": "INTEGER", "sample_values": [85, 72, 91]},
                {"name": "resting_heart_rate", "description": "Resting heart rate (bpm)", "data_type": "INTEGER", "sample_values": [52, 58, 48]},
                {"name": "hrv_ms", "description": "Heart rate variability in milliseconds", "data_type": "DECIMAL(6,2)", "sample_values": [75.50, 82.30, 68.75]},
                {"name": "readiness_score", "description": "Recovery readiness score (0-100)", "data_type": "INTEGER", "sample_values": [85, 72, 91]},
                {"name": "perceived_fatigue", "description": "Athlete-reported fatigue (1-10)", "data_type": "INTEGER", "sample_values": [3, 7, 2]},
                {"name": "muscle_soreness", "description": "Muscle soreness rating (1-10)", "data_type": "INTEGER", "sample_values": [4, 8, 2]},
                {"name": "wellness_score", "description": "Overall wellness score (0-100)", "data_type": "INTEGER", "sample_values": [85, 72, 91]},
            ]
        },
        {
            "vendor_email": "info@athletemetrics.com",
            "title": "Nutrition and Hydration Tracking",
            "status": "active",
            "visibility": "public",
            "description": "Athlete nutrition intake, hydration levels, supplement usage, and dietary compliance data",
            "domain": "Sports",
            "dataset_type": "Time-series",
            "granularity": "Daily",
            "pricing_model": "Subscription",
            "license": "Research Use Only",
            "topics": ["nutrition", "hydration", "diet", "supplements"],
            "entities": ["athletes", "meals", "supplements"],
            "temporal_coverage": {"start_date": "2018-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "CA", "EU"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "athlete_id", "description": "Anonymized athlete identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "date", "description": "Tracking date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "total_calories", "description": "Total caloric intake", "data_type": "INTEGER", "sample_values": [3500, 4200, 2800]},
                {"name": "protein_grams", "description": "Protein intake in grams", "data_type": "INTEGER", "sample_values": [180, 220, 150]},
                {"name": "carbs_grams", "description": "Carbohydrate intake in grams", "data_type": "INTEGER", "sample_values": [450, 520, 350]},
                {"name": "fat_grams", "description": "Fat intake in grams", "data_type": "INTEGER", "sample_values": [100, 120, 85]},
                {"name": "hydration_liters", "description": "Water intake in liters", "data_type": "DECIMAL(4,2)", "sample_values": [3.50, 4.20, 2.80]},
                {"name": "urine_specific_gravity", "description": "Hydration status measure", "data_type": "DECIMAL(5,3)", "sample_values": [1.010, 1.020, 1.005]},
                {"name": "supplement_compliance_pct", "description": "Supplement adherence percentage", "data_type": "DECIMAL(5,2)", "sample_values": [95.00, 82.00, 100.00]},
            ]
        },
        
        # ============ SPORTS DOMAIN - LeagueInsights Data (Vendor 4) ============
        # RELATED DATASETS: Franchise Valuations + Revenue Data (join on franchise_id), TV Ratings + League Popularity (join on league/season)
        {
            "vendor_email": "contact@leagueinsights.net",
            "title": "Sports Franchise Valuations and Ownership",
            "status": "active",
            "visibility": "public",
            "description": "Professional sports franchise valuations, ownership data, and financial performance metrics",
            "domain": "Sports",
            "dataset_type": "Reference",
            "granularity": "Franchise-level",
            "pricing_model": "One-time Purchase",
            "license": "Commercial Use Allowed",
            "topics": ["franchise valuations", "ownership", "team finances", "business"],
            "entities": ["franchises", "owners", "valuations"],
            "temporal_coverage": {"start_date": "2010-01-01", "end_date": "2024-12-31", "frequency": "Annual"},
            "geographic_coverage": {"countries": ["US", "CA", "Global"], "regions": ["North America", "Worldwide"]},
            "columns": [
                {"name": "franchise_id", "description": "Unique franchise identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "team_name", "description": "Team name", "data_type": "VARCHAR(100)", "sample_values": ["Dallas Cowboys", "New York Yankees", "Real Madrid"]},
                {"name": "league", "description": "Sports league", "data_type": "VARCHAR(50)", "sample_values": ["NFL", "MLB", "NBA", "Premier League"]},
                {"name": "year", "description": "Valuation year", "data_type": "INTEGER", "sample_values": [2022, 2023, 2024]},
                {"name": "valuation_usd_millions", "description": "Franchise valuation in millions USD", "data_type": "DECIMAL(10,2)", "sample_values": [8000.00, 6500.00, 5200.00]},
                {"name": "owner", "description": "Primary owner name", "data_type": "VARCHAR(200)", "sample_values": ["Jerry Jones", "Steinbrenner Family", "Florentino Pérez"]},
                {"name": "purchase_price_usd_millions", "description": "Original purchase price", "data_type": "DECIMAL(10,2)", "sample_values": [140.00, 1200.00, 75.00]},
                {"name": "purchase_year", "description": "Year of purchase", "data_type": "INTEGER", "sample_values": [1989, 1973, 2000]},
                {"name": "stadium", "description": "Home stadium name", "data_type": "VARCHAR(200)", "sample_values": ["AT&T Stadium", "Yankee Stadium", "Santiago Bernabéu"]},
                {"name": "championships_won", "description": "Total championships", "data_type": "INTEGER", "sample_values": [5, 27, 14]},
            ]
        },
        {
            "vendor_email": "contact@leagueinsights.net",
            "title": "League Revenue and Financial Performance",
            "status": "active",
            "visibility": "public",
            "description": "League-wide revenue, TV deals, sponsorships, and financial performance data",
            "domain": "Sports",
            "dataset_type": "Time-series",
            "granularity": "Annual",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["league revenue", "TV deals", "sponsorships", "financial performance"],
            "entities": ["leagues", "teams", "sponsors"],
            "temporal_coverage": {"start_date": "2010-01-01", "end_date": "2024-12-31", "frequency": "Annual"},
            "geographic_coverage": {"countries": ["US", "CA", "Global"], "regions": ["North America", "Worldwide"]},
            "columns": [
                {"name": "franchise_id", "description": "Unique franchise identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "team_name", "description": "Team name", "data_type": "VARCHAR(100)", "sample_values": ["Golden State Warriors", "Manchester United", "Los Angeles Dodgers"]},
                {"name": "league", "description": "Sports league", "data_type": "VARCHAR(50)", "sample_values": ["NBA", "Premier League", "MLB"]},
                {"name": "year", "description": "Financial year", "data_type": "INTEGER", "sample_values": [2022, 2023, 2024]},
                {"name": "total_revenue_usd_millions", "description": "Total revenue in millions USD", "data_type": "DECIMAL(10,2)", "sample_values": [750.00, 650.00, 550.00]},
                {"name": "ticket_revenue_usd_millions", "description": "Ticket sales revenue", "data_type": "DECIMAL(10,2)", "sample_values": [150.00, 120.00, 95.00]},
                {"name": "media_rights_usd_millions", "description": "Media rights revenue", "data_type": "DECIMAL(10,2)", "sample_values": [250.00, 200.00, 180.00]},
                {"name": "sponsorship_usd_millions", "description": "Sponsorship revenue", "data_type": "DECIMAL(10,2)", "sample_values": [150.00, 130.00, 110.00]},
                {"name": "merchandise_usd_millions", "description": "Merchandise revenue", "data_type": "DECIMAL(10,2)", "sample_values": [50.00, 45.00, 38.00]},
                {"name": "operating_income_usd_millions", "description": "Operating income", "data_type": "DECIMAL(10,2)", "sample_values": [125.00, 95.00, 75.00]},
            ]
        },
        {
            "vendor_email": "contact@leagueinsights.net",
            "title": "Sports Broadcasting and TV Ratings",
            "status": "active",
            "visibility": "public",
            "description": "TV ratings, viewership data, streaming metrics, and broadcast audience analytics",
            "domain": "Sports",
            "dataset_type": "Time-series",
            "granularity": "Game-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["TV ratings", "viewership", "broadcasting", "streaming"],
            "entities": ["games", "broadcasts", "viewers"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "CA", "UK"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "broadcast_id", "description": "Unique broadcast identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "game_id", "description": "Game identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "broadcast_date", "description": "Broadcast date", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 19:00:00", "2024-02-20 13:00:00"]},
                {"name": "network", "description": "Broadcasting network", "data_type": "VARCHAR(100)", "sample_values": ["ESPN", "NBC", "CBS", "Fox", "Sky Sports"]},
                {"name": "league", "description": "Sports league", "data_type": "VARCHAR(50)", "sample_values": ["NFL", "NBA", "Premier League"]},
                {"name": "total_viewers_millions", "description": "Total viewers in millions", "data_type": "DECIMAL(6,2)", "sample_values": [25.50, 15.30, 8.75]},
                {"name": "rating_18_49", "description": "Rating among adults 18-49", "data_type": "DECIMAL(4,2)", "sample_values": [8.5, 5.2, 3.8]},
                {"name": "streaming_viewers_millions", "description": "Streaming viewers in millions", "data_type": "DECIMAL(6,2)", "sample_values": [5.50, 3.30, 2.75]},
                {"name": "peak_viewership_millions", "description": "Peak concurrent viewers", "data_type": "DECIMAL(6,2)", "sample_values": [32.50, 18.30, 12.75]},
                {"name": "market_share_pct", "description": "Market share percentage", "data_type": "DECIMAL(5,2)", "sample_values": [45.50, 32.30, 18.75]},
            ]
        },
        {
            "vendor_email": "contact@leagueinsights.net",
            "title": "Attendance and Ticket Sales Analytics",
            "status": "active",
            "visibility": "public",
            "description": "Game attendance, ticket sales, pricing, and venue capacity utilization data",
            "domain": "Sports",
            "dataset_type": "Time-series",
            "granularity": "Game-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["attendance", "ticket sales", "pricing", "venues"],
            "entities": ["games", "venues", "tickets"],
            "temporal_coverage": {"start_date": "2015-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "CA", "Global"], "regions": ["North America", "Worldwide"]},
            "columns": [
                {"name": "game_id", "description": "Unique game identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "venue", "description": "Venue name", "data_type": "VARCHAR(200)", "sample_values": ["Madison Square Garden", "Wembley Stadium", "Fenway Park"]},
                {"name": "game_date", "description": "Game date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "attendance", "description": "Game attendance", "data_type": "INTEGER", "sample_values": [20000, 75000, 37000]},
                {"name": "capacity", "description": "Venue capacity", "data_type": "INTEGER", "sample_values": [20789, 90000, 37755]},
                {"name": "capacity_pct", "description": "Capacity utilization percentage", "data_type": "DECIMAL(5,2)", "sample_values": [96.20, 83.33, 98.00]},
                {"name": "average_ticket_price_usd", "description": "Average ticket price", "data_type": "DECIMAL(8,2)", "sample_values": [125.00, 85.00, 55.00]},
                {"name": "total_gate_revenue_usd", "description": "Total gate revenue", "data_type": "DECIMAL(12,2)", "sample_values": [2500000.00, 6375000.00, 2035000.00]},
                {"name": "premium_seats_sold", "description": "Premium/VIP seats sold", "data_type": "INTEGER", "sample_values": [2000, 5000, 1500]},
                {"name": "sellout", "description": "Whether game was sold out", "data_type": "BOOLEAN", "sample_values": [False, True, True]},
            ]
        },
        {
            "vendor_email": "contact@leagueinsights.net",
            "title": "Fan Engagement and Social Media Metrics",
            "status": "active",
            "visibility": "public",
            "description": "Team and league social media engagement, fan sentiment, and digital content performance",
            "domain": "Sports",
            "dataset_type": "Time-series",
            "granularity": "Daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["fan engagement", "social media", "sentiment", "digital content"],
            "entities": ["teams", "fans", "social media"],
            "temporal_coverage": {"start_date": "2018-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "team_id", "description": "Unique team identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "team_name", "description": "Team name", "data_type": "VARCHAR(100)", "sample_values": ["Real Madrid", "Lakers", "Patriots"]},
                {"name": "date", "description": "Metrics date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "total_followers", "description": "Total social media followers", "data_type": "INTEGER", "sample_values": [150000000, 35000000, 25000000]},
                {"name": "daily_engagement", "description": "Daily engagement (likes, shares, comments)", "data_type": "INTEGER", "sample_values": [5000000, 1200000, 850000]},
                {"name": "engagement_rate_pct", "description": "Engagement rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [3.33, 3.43, 3.40]},
                {"name": "sentiment_score", "description": "Fan sentiment score (-100 to 100)", "data_type": "INTEGER", "sample_values": [75, -25, 50]},
                {"name": "mentions", "description": "Social media mentions", "data_type": "INTEGER", "sample_values": [500000, 250000, 180000]},
                {"name": "video_views", "description": "Video content views", "data_type": "INTEGER", "sample_values": [25000000, 12000000, 8500000]},
            ]
        },
        
        # ============ RETAIL DOMAIN - RetailPulse Analytics (Vendor 1) ============
        # RELATED DATASETS: Transactions + Customer Profiles (join on customer_id), Store Sales + Store Performance (join on store_id)
        {
            "vendor_email": "data@retailpulse.com",
            "title": "Point-of-Sale Transaction Data",
            "status": "active",
            "visibility": "public",
            "description": "Comprehensive POS transaction data including purchases, payment methods, timestamps, and basket-level details",
            "domain": "Retail",
            "dataset_type": "Transactional",
            "granularity": "Transaction-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["transactions", "point of sale", "purchases", "payments"],
            "entities": ["transactions", "customers", "products", "stores"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Real-time"},
            "geographic_coverage": {"countries": ["US", "CA", "UK"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "transaction_id", "description": "Unique transaction identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "customer_id", "description": "Customer identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "store_id", "description": "Store identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "transaction_timestamp", "description": "Transaction date and time", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "total_amount_usd", "description": "Total transaction amount in USD", "data_type": "DECIMAL(10,2)", "sample_values": [125.50, 85.30, 450.75]},
                {"name": "item_count", "description": "Number of items purchased", "data_type": "INTEGER", "sample_values": [5, 3, 12]},
                {"name": "payment_method", "description": "Payment method used", "data_type": "VARCHAR(50)", "sample_values": ["Credit Card", "Debit Card", "Cash", "Mobile Payment", "Gift Card"]},
                {"name": "discount_amount_usd", "description": "Total discount applied", "data_type": "DECIMAL(10,2)", "sample_values": [12.50, 0.00, 45.00]},
                {"name": "loyalty_points_earned", "description": "Loyalty points earned", "data_type": "INTEGER", "sample_values": [125, 85, 450]},
                {"name": "channel", "description": "Sales channel", "data_type": "VARCHAR(50)", "sample_values": ["In-store", "Online", "Mobile App", "Kiosk"]},
            ]
        },
        {
            "vendor_email": "data@retailpulse.com",
            "title": "Customer Profile and Demographics",
            "status": "active",
            "visibility": "public",
            "description": "Customer demographic data, shopping preferences, lifetime value, and segmentation information",
            "domain": "Retail",
            "dataset_type": "Profile",
            "granularity": "Customer-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["customers", "demographics", "segmentation", "lifetime value"],
            "entities": ["customers", "segments"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Updated continuously"},
            "geographic_coverage": {"countries": ["US", "CA", "UK"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "customer_id", "description": "Unique customer identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "registration_date", "description": "Customer registration date", "data_type": "DATE", "sample_values": ["2020-03-15", "2021-07-22"]},
                {"name": "age_group", "description": "Customer age group", "data_type": "VARCHAR(20)", "sample_values": ["18-24", "25-34", "35-49", "50-64", "65+"]},
                {"name": "gender", "description": "Customer gender", "data_type": "VARCHAR(20)", "sample_values": ["Male", "Female", "Non-binary", "Prefer not to say"]},
                {"name": "zip_code", "description": "Customer zip code", "data_type": "VARCHAR(10)", "sample_values": ["10001", "90210", "60601"]},
                {"name": "total_purchases", "description": "Lifetime purchase count", "data_type": "INTEGER", "sample_values": [50, 125, 300]},
                {"name": "lifetime_value_usd", "description": "Customer lifetime value in USD", "data_type": "DECIMAL(10,2)", "sample_values": [5000.00, 12500.00, 30000.00]},
                {"name": "average_basket_size_usd", "description": "Average basket size", "data_type": "DECIMAL(8,2)", "sample_values": [100.00, 100.00, 100.00]},
                {"name": "preferred_category", "description": "Most purchased category", "data_type": "VARCHAR(100)", "sample_values": ["Electronics", "Clothing", "Home & Garden", "Groceries"]},
                {"name": "customer_segment", "description": "Customer segment classification", "data_type": "VARCHAR(50)", "sample_values": ["High Value", "Frequent Buyer", "Occasional", "At Risk", "Dormant"]},
            ]
        },
        {
            "vendor_email": "data@retailpulse.com",
            "title": "Store Performance and Sales Metrics",
            "status": "active",
            "visibility": "public",
            "description": "Store-level sales performance, traffic, conversion rates, and operational metrics",
            "domain": "Retail",
            "dataset_type": "Time-series",
            "granularity": "Store-daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["store performance", "sales metrics", "traffic", "conversion"],
            "entities": ["stores", "sales", "traffic"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "CA", "UK"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "store_id", "description": "Unique store identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "store_name", "description": "Store name or number", "data_type": "VARCHAR(100)", "sample_values": ["Manhattan 5th Ave", "Chicago Downtown", "Seattle Pike Place"]},
                {"name": "date", "description": "Business date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "daily_sales_usd", "description": "Total daily sales in USD", "data_type": "DECIMAL(12,2)", "sample_values": [50000.00, 75000.00, 125000.00]},
                {"name": "transaction_count", "description": "Number of transactions", "data_type": "INTEGER", "sample_values": [500, 750, 1250]},
                {"name": "foot_traffic", "description": "Store foot traffic count", "data_type": "INTEGER", "sample_values": [2000, 3000, 5000]},
                {"name": "conversion_rate_pct", "description": "Conversion rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [25.00, 25.00, 25.00]},
                {"name": "average_transaction_value", "description": "Average transaction value", "data_type": "DECIMAL(8,2)", "sample_values": [100.00, 100.00, 100.00]},
                {"name": "returns_count", "description": "Number of returns", "data_type": "INTEGER", "sample_values": [25, 38, 63]},
                {"name": "employee_count", "description": "Number of employees working", "data_type": "INTEGER", "sample_values": [15, 20, 30]},
            ]
        },
        {
            "vendor_email": "data@retailpulse.com",
            "title": "Product Sales and Performance Analytics",
            "status": "active",
            "visibility": "public",
            "description": "Product-level sales data, inventory turnover, pricing, and performance metrics",
            "domain": "Retail",
            "dataset_type": "Time-series",
            "granularity": "Product-daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["product sales", "inventory turnover", "pricing", "SKU performance"],
            "entities": ["products", "SKUs", "categories"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "CA", "UK"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "product_id", "description": "Unique product identifier", "data_type": "UUID", "sample_values": ["d4e5f6a7-b8c9-0123-def1-234567890123"]},
                {"name": "sku", "description": "Stock keeping unit", "data_type": "VARCHAR(50)", "sample_values": ["ELEC-LAP-001", "CLTH-SHR-025", "HOME-FUR-150"]},
                {"name": "product_name", "description": "Product name", "data_type": "VARCHAR(200)", "sample_values": ["Laptop 15-inch", "Men's Dress Shirt", "Dining Table"]},
                {"name": "category", "description": "Product category", "data_type": "VARCHAR(100)", "sample_values": ["Electronics", "Clothing", "Home & Garden", "Groceries"]},
                {"name": "date", "description": "Sales date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "units_sold", "description": "Number of units sold", "data_type": "INTEGER", "sample_values": [50, 125, 300]},
                {"name": "revenue_usd", "description": "Total revenue in USD", "data_type": "DECIMAL(12,2)", "sample_values": [50000.00, 6250.00, 90000.00]},
                {"name": "current_price_usd", "description": "Current selling price", "data_type": "DECIMAL(8,2)", "sample_values": [999.99, 49.99, 299.99]},
                {"name": "cost_usd", "description": "Product cost", "data_type": "DECIMAL(8,2)", "sample_values": [600.00, 20.00, 150.00]},
                {"name": "margin_pct", "description": "Profit margin percentage", "data_type": "DECIMAL(5,2)", "sample_values": [40.00, 60.00, 50.00]},
            ]
        },
        {
            "vendor_email": "data@retailpulse.com",
            "title": "Seasonal and Promotional Campaign Performance",
            "status": "active",
            "visibility": "public",
            "description": "Promotional campaign effectiveness, seasonal trends, discount impact, and marketing ROI data",
            "domain": "Retail",
            "dataset_type": "Campaign",
            "granularity": "Campaign-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["promotions", "campaigns", "seasonal trends", "marketing ROI"],
            "entities": ["campaigns", "promotions", "discounts"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "CA", "UK"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "campaign_id", "description": "Unique campaign identifier", "data_type": "UUID", "sample_values": ["e5f6a7b8-c9d0-1234-ef12-345678901234"]},
                {"name": "campaign_name", "description": "Campaign name", "data_type": "VARCHAR(200)", "sample_values": ["Black Friday 2024", "Summer Sale", "Back to School"]},
                {"name": "start_date", "description": "Campaign start date", "data_type": "DATE", "sample_values": ["2024-11-24", "2024-06-01", "2024-08-01"]},
                {"name": "end_date", "description": "Campaign end date", "data_type": "DATE", "sample_values": ["2024-11-27", "2024-08-31", "2024-09-15"]},
                {"name": "discount_type", "description": "Type of discount", "data_type": "VARCHAR(50)", "sample_values": ["Percentage Off", "Dollar Amount", "Buy One Get One", "Free Shipping"]},
                {"name": "average_discount_pct", "description": "Average discount percentage", "data_type": "DECIMAL(5,2)", "sample_values": [25.00, 15.00, 50.00]},
                {"name": "total_revenue_usd", "description": "Total campaign revenue", "data_type": "DECIMAL(15,2)", "sample_values": [5000000.00, 2500000.00, 1500000.00]},
                {"name": "transactions", "description": "Number of transactions", "data_type": "INTEGER", "sample_values": [50000, 25000, 15000]},
                {"name": "marketing_spend_usd", "description": "Marketing spend in USD", "data_type": "DECIMAL(12,2)", "sample_values": [250000.00, 125000.00, 75000.00]},
                {"name": "roi_pct", "description": "Return on investment percentage", "data_type": "DECIMAL(6,2)", "sample_values": [1900.00, 1900.00, 1900.00]},
            ]
        },
        
        # ============ RETAIL DOMAIN - EcomAnalytics Pro (Vendor 2) ============
        # RELATED DATASETS: Online Sessions + Cart Abandonment (join on session_id), Product Views + Purchase Conversion (join on product_id)
        {
            "vendor_email": "sales@ecomanalytics.io",
            "title": "E-commerce Website Session Data",
            "status": "active",
            "visibility": "public",
            "description": "Website session analytics including page views, session duration, bounce rates, and user journey tracking",
            "domain": "Retail",
            "dataset_type": "Time-series",
            "granularity": "Session-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["website analytics", "sessions", "user behavior", "e-commerce"],
            "entities": ["sessions", "users", "pages"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Real-time"},
            "geographic_coverage": {"countries": ["US", "CA", "UK", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "session_id", "description": "Unique session identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "user_id", "description": "Anonymized user identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "session_start", "description": "Session start timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "session_duration_seconds", "description": "Session duration in seconds", "data_type": "INTEGER", "sample_values": [300, 600, 1200]},
                {"name": "page_views", "description": "Number of pages viewed", "data_type": "INTEGER", "sample_values": [5, 10, 20]},
                {"name": "device_type", "description": "Device type", "data_type": "VARCHAR(50)", "sample_values": ["Desktop", "Mobile", "Tablet"]},
                {"name": "browser", "description": "Web browser", "data_type": "VARCHAR(50)", "sample_values": ["Chrome", "Safari", "Firefox", "Edge"]},
                {"name": "referrer_source", "description": "Traffic source", "data_type": "VARCHAR(100)", "sample_values": ["Google", "Facebook", "Direct", "Email", "Instagram"]},
                {"name": "converted", "description": "Whether session resulted in purchase", "data_type": "BOOLEAN", "sample_values": [True, False, True]},
                {"name": "bounce", "description": "Whether session bounced", "data_type": "BOOLEAN", "sample_values": [False, True, False]},
            ]
        },
        {
            "vendor_email": "sales@ecomanalytics.io",
            "title": "Shopping Cart Abandonment Analysis",
            "status": "active",
            "visibility": "public",
            "description": "Cart abandonment data including items left in cart, abandonment stage, and recovery metrics",
            "domain": "Retail",
            "dataset_type": "Event-based",
            "granularity": "Cart-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["cart abandonment", "checkout funnel", "recovery", "conversion optimization"],
            "entities": ["carts", "users", "products"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "CA", "UK", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "cart_id", "description": "Unique cart identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "session_id", "description": "Session identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "user_id", "description": "Anonymized user identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "cart_created_timestamp", "description": "Cart creation timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "cart_value_usd", "description": "Total cart value in USD", "data_type": "DECIMAL(10,2)", "sample_values": [125.50, 85.30, 450.75]},
                {"name": "item_count", "description": "Number of items in cart", "data_type": "INTEGER", "sample_values": [3, 5, 8]},
                {"name": "abandonment_stage", "description": "Stage where cart was abandoned", "data_type": "VARCHAR(50)", "sample_values": ["Cart Page", "Shipping Info", "Payment Info", "Review Order"]},
                {"name": "recovery_email_sent", "description": "Whether recovery email was sent", "data_type": "BOOLEAN", "sample_values": [True, True, False]},
                {"name": "recovered", "description": "Whether cart was recovered", "data_type": "BOOLEAN", "sample_values": [False, True, False]},
                {"name": "time_to_recovery_hours", "description": "Hours until recovery (if recovered)", "data_type": "DECIMAL(6,2)", "sample_values": [24.50, 48.30, 12.75]},
            ]
        },
        {
            "vendor_email": "sales@ecomanalytics.io",
            "title": "Product Page Views and Engagement",
            "status": "active",
            "visibility": "public",
            "description": "Product page analytics including views, engagement, add-to-cart rates, and conversion metrics",
            "domain": "Retail",
            "dataset_type": "Time-series",
            "granularity": "Product-daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["product analytics", "page views", "engagement", "conversion"],
            "entities": ["products", "pages", "users"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "CA", "UK", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "product_id", "description": "Unique product identifier", "data_type": "UUID", "sample_values": ["d4e5f6a7-b8c9-0123-def1-234567890123"]},
                {"name": "date", "description": "Analytics date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "page_views", "description": "Product page views", "data_type": "INTEGER", "sample_values": [5000, 12000, 25000]},
                {"name": "unique_visitors", "description": "Unique visitors to product page", "data_type": "INTEGER", "sample_values": [4000, 10000, 20000]},
                {"name": "average_time_on_page_seconds", "description": "Average time on page", "data_type": "INTEGER", "sample_values": [90, 120, 180]},
                {"name": "add_to_cart_count", "description": "Number of add-to-cart actions", "data_type": "INTEGER", "sample_values": [500, 1200, 2500]},
                {"name": "add_to_cart_rate_pct", "description": "Add-to-cart rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [10.00, 10.00, 10.00]},
                {"name": "purchases", "description": "Number of purchases", "data_type": "INTEGER", "sample_values": [250, 600, 1250]},
                {"name": "conversion_rate_pct", "description": "Conversion rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [5.00, 5.00, 5.00]},
                {"name": "wishlist_adds", "description": "Number of wishlist additions", "data_type": "INTEGER", "sample_values": [150, 360, 750]},
            ]
        },
        {
            "vendor_email": "sales@ecomanalytics.io",
            "title": "Customer Reviews and Ratings Data",
            "status": "active",
            "visibility": "public",
            "description": "Product reviews, ratings, sentiment analysis, and customer feedback metrics",
            "domain": "Retail",
            "dataset_type": "Time-series",
            "granularity": "Review-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["reviews", "ratings", "sentiment", "customer feedback"],
            "entities": ["reviews", "products", "customers"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "CA", "UK", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "review_id", "description": "Unique review identifier", "data_type": "UUID", "sample_values": ["e5f6a7b8-c9d0-1234-ef12-345678901234"]},
                {"name": "product_id", "description": "Product identifier", "data_type": "UUID", "sample_values": ["d4e5f6a7-b8c9-0123-def1-234567890123"]},
                {"name": "customer_id", "description": "Customer identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "review_date", "description": "Review submission date", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "rating", "description": "Star rating (1-5)", "data_type": "INTEGER", "sample_values": [5, 4, 3, 2, 1]},
                {"name": "verified_purchase", "description": "Whether reviewer purchased product", "data_type": "BOOLEAN", "sample_values": [True, True, False]},
                {"name": "helpful_votes", "description": "Number of helpful votes", "data_type": "INTEGER", "sample_values": [50, 125, 300]},
                {"name": "sentiment_score", "description": "Sentiment score (-100 to 100)", "data_type": "INTEGER", "sample_values": [85, -25, 50]},
                {"name": "review_length_chars", "description": "Review text length in characters", "data_type": "INTEGER", "sample_values": [250, 500, 1200]},
                {"name": "contains_images", "description": "Whether review includes images", "data_type": "BOOLEAN", "sample_values": [True, False, True]},
            ]
        },
        {
            "vendor_email": "sales@ecomanalytics.io",
            "title": "Search and Discovery Analytics",
            "status": "active",
            "visibility": "public",
            "description": "Site search data, query analysis, search result performance, and discovery patterns",
            "domain": "Retail",
            "dataset_type": "Time-series",
            "granularity": "Search-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["site search", "search analytics", "discovery", "query analysis"],
            "entities": ["searches", "queries", "results"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Real-time"},
            "geographic_coverage": {"countries": ["US", "CA", "UK", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "search_id", "description": "Unique search identifier", "data_type": "UUID", "sample_values": ["f6a7b8c9-d0e1-2345-f123-456789012345"]},
                {"name": "session_id", "description": "Session identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "search_timestamp", "description": "Search timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "search_query", "description": "Search query text", "data_type": "VARCHAR(500)", "sample_values": ["wireless headphones", "winter jacket", "kitchen mixer"]},
                {"name": "results_count", "description": "Number of results returned", "data_type": "INTEGER", "sample_values": [150, 50, 0]},
                {"name": "clicked_result_position", "description": "Position of clicked result (if any)", "data_type": "INTEGER", "sample_values": [1, 3, 5]},
                {"name": "search_to_purchase", "description": "Whether search led to purchase", "data_type": "BOOLEAN", "sample_values": [True, False, True]},
                {"name": "refinements_used", "description": "Number of filter refinements applied", "data_type": "INTEGER", "sample_values": [0, 2, 5]},
                {"name": "zero_results", "description": "Whether search returned zero results", "data_type": "BOOLEAN", "sample_values": [False, False, True]},
            ]
        },
        
        # ============ RETAIL DOMAIN - LoyaltyMetrics Intelligence (Vendor 3) ============
        # RELATED DATASETS: Loyalty Members + Points Transactions (join on member_id), Member Tiers + Redemption Behavior (join on member_id)
        {
            "vendor_email": "info@loyaltymetrics.net",
            "title": "Loyalty Program Member Profiles",
            "status": "active",
            "visibility": "public",
            "description": "Loyalty program member data including enrollment, tier status, lifetime points, and engagement metrics",
            "domain": "Retail",
            "dataset_type": "Profile",
            "granularity": "Member-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["loyalty programs", "members", "rewards", "engagement"],
            "entities": ["members", "tiers", "programs"],
            "temporal_coverage": {"start_date": "2018-01-01", "end_date": "2024-12-31", "frequency": "Updated continuously"},
            "geographic_coverage": {"countries": ["US", "CA", "UK"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "member_id", "description": "Unique member identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "enrollment_date", "description": "Program enrollment date", "data_type": "DATE", "sample_values": ["2020-03-15", "2021-07-22"]},
                {"name": "tier", "description": "Current membership tier", "data_type": "VARCHAR(50)", "sample_values": ["Bronze", "Silver", "Gold", "Platinum"]},
                {"name": "lifetime_points_earned", "description": "Total points earned", "data_type": "INTEGER", "sample_values": [5000, 15000, 50000]},
                {"name": "current_points_balance", "description": "Current points balance", "data_type": "INTEGER", "sample_values": [1500, 5000, 12000]},
                {"name": "points_redeemed", "description": "Total points redeemed", "data_type": "INTEGER", "sample_values": [3500, 10000, 38000]},
                {"name": "total_spend_usd", "description": "Lifetime spend in USD", "data_type": "DECIMAL(12,2)", "sample_values": [5000.00, 15000.00, 50000.00]},
                {"name": "average_visit_frequency_days", "description": "Average days between visits", "data_type": "INTEGER", "sample_values": [30, 15, 7]},
                {"name": "last_activity_date", "description": "Last activity date", "data_type": "DATE", "sample_values": ["2024-11-15", "2024-12-01"]},
                {"name": "active_status", "description": "Whether member is active", "data_type": "BOOLEAN", "sample_values": [True, True, False]},
            ]
        },
        {
            "vendor_email": "info@loyaltymetrics.net",
            "title": "Points Earn and Burn Transactions",
            "status": "active",
            "visibility": "public",
            "description": "Loyalty points transaction history including points earned, redeemed, expired, and adjusted",
            "domain": "Retail",
            "dataset_type": "Transactional",
            "granularity": "Transaction-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["points transactions", "earn and burn", "redemptions", "loyalty"],
            "entities": ["transactions", "members", "points"],
            "temporal_coverage": {"start_date": "2018-01-01", "end_date": "2024-12-31", "frequency": "Real-time"},
            "geographic_coverage": {"countries": ["US", "CA", "UK"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "transaction_id", "description": "Unique transaction identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "member_id", "description": "Member identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "transaction_timestamp", "description": "Transaction timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "transaction_type", "description": "Type of transaction", "data_type": "VARCHAR(50)", "sample_values": ["Earn", "Redeem", "Expire", "Bonus", "Adjustment"]},
                {"name": "points_amount", "description": "Points amount (positive or negative)", "data_type": "INTEGER", "sample_values": [100, -500, 250, -100]},
                {"name": "purchase_amount_usd", "description": "Associated purchase amount", "data_type": "DECIMAL(10,2)", "sample_values": [100.00, 0.00, 250.00]},
                {"name": "redemption_value_usd", "description": "Cash value of redemption", "data_type": "DECIMAL(10,2)", "sample_values": [0.00, 5.00, 0.00]},
                {"name": "expiration_date", "description": "Points expiration date", "data_type": "DATE", "sample_values": ["2025-01-15", "2025-02-20"]},
                {"name": "store_id", "description": "Store identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "channel", "description": "Transaction channel", "data_type": "VARCHAR(50)", "sample_values": ["In-store", "Online", "Mobile App"]},
            ]
        },
        {
            "vendor_email": "info@loyaltymetrics.net",
            "title": "Reward Redemption Catalog and Preferences",
            "status": "active",
            "visibility": "public",
            "description": "Reward catalog data including redemption options, popularity, and member preferences",
            "domain": "Retail",
            "dataset_type": "Reference",
            "granularity": "Reward-level",
            "pricing_model": "One-time Purchase",
            "license": "Commercial Use Allowed",
            "topics": ["rewards catalog", "redemptions", "preferences", "benefits"],
            "entities": ["rewards", "redemptions", "members"],
            "temporal_coverage": {"start_date": "2018-01-01", "end_date": "2024-12-31", "frequency": "Updated continuously"},
            "geographic_coverage": {"countries": ["US", "CA", "UK"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "reward_id", "description": "Unique reward identifier", "data_type": "UUID", "sample_values": ["d4e5f6a7-b8c9-0123-def1-234567890123"]},
                {"name": "reward_name", "description": "Reward name", "data_type": "VARCHAR(200)", "sample_values": ["$10 Off Coupon", "Free Shipping", "Gift Card"]},
                {"name": "reward_type", "description": "Type of reward", "data_type": "VARCHAR(50)", "sample_values": ["Discount", "Gift Card", "Product", "Experience"]},
                {"name": "points_required", "description": "Points required for redemption", "data_type": "INTEGER", "sample_values": [1000, 2500, 5000]},
                {"name": "cash_value_usd", "description": "Cash value of reward", "data_type": "DECIMAL(8,2)", "sample_values": [10.00, 25.00, 50.00]},
                {"name": "redemptions_ytd", "description": "Year-to-date redemptions", "data_type": "INTEGER", "sample_values": [5000, 12000, 25000]},
                {"name": "availability", "description": "Reward availability status", "data_type": "VARCHAR(50)", "sample_values": ["Available", "Limited Quantity", "Out of Stock", "Expired"]},
                {"name": "tier_requirement", "description": "Minimum tier required", "data_type": "VARCHAR(50)", "sample_values": ["Bronze", "Silver", "Gold", "Platinum", "All Tiers"]},
                {"name": "average_rating", "description": "Average member rating (1-5)", "data_type": "DECIMAL(3,2)", "sample_values": [4.50, 4.75, 3.80]},
            ]
        },
        {
            "vendor_email": "info@loyaltymetrics.net",
            "title": "Member Engagement and Campaign Response",
            "status": "active",
            "visibility": "public",
            "description": "Loyalty program engagement metrics, email campaign responses, and promotional effectiveness",
            "domain": "Retail",
            "dataset_type": "Campaign",
            "granularity": "Campaign-member",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["engagement", "campaigns", "email marketing", "promotions"],
            "entities": ["campaigns", "members", "responses"],
            "temporal_coverage": {"start_date": "2018-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "CA", "UK"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "campaign_id", "description": "Unique campaign identifier", "data_type": "UUID", "sample_values": ["e5f6a7b8-c9d0-1234-ef12-345678901234"]},
                {"name": "member_id", "description": "Member identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "campaign_name", "description": "Campaign name", "data_type": "VARCHAR(200)", "sample_values": ["Holiday Bonus Points", "Birthday Reward", "Tier Upgrade Offer"]},
                {"name": "send_date", "description": "Campaign send date", "data_type": "TIMESTAMP", "sample_values": ["2024-11-15 08:00:00", "2024-12-01 10:00:00"]},
                {"name": "channel", "description": "Communication channel", "data_type": "VARCHAR(50)", "sample_values": ["Email", "SMS", "Push Notification", "In-App"]},
                {"name": "opened", "description": "Whether message was opened", "data_type": "BOOLEAN", "sample_values": [True, True, False]},
                {"name": "clicked", "description": "Whether message was clicked", "data_type": "BOOLEAN", "sample_values": [True, False, False]},
                {"name": "converted", "description": "Whether member converted/purchased", "data_type": "BOOLEAN", "sample_values": [True, False, False]},
                {"name": "bonus_points_awarded", "description": "Bonus points awarded", "data_type": "INTEGER", "sample_values": [500, 1000, 0]},
                {"name": "revenue_generated_usd", "description": "Revenue generated from campaign", "data_type": "DECIMAL(10,2)", "sample_values": [250.00, 0.00, 500.00]},
            ]
        },
        {
            "vendor_email": "info@loyaltymetrics.net",
            "title": "Churn Risk and Retention Analytics",
            "status": "active",
            "visibility": "public",
            "description": "Member churn risk scores, retention rates, and predictive analytics for loyalty program health",
            "domain": "Retail",
            "dataset_type": "Profile",
            "granularity": "Member-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["churn prediction", "retention", "risk scoring", "loyalty health"],
            "entities": ["members", "segments", "risk"],
            "temporal_coverage": {"start_date": "2018-01-01", "end_date": "2024-12-31", "frequency": "Monthly"},
            "geographic_coverage": {"countries": ["US", "CA", "UK"], "regions": ["North America", "Europe"]},
            "columns": [
                {"name": "member_id", "description": "Unique member identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "analysis_date", "description": "Analysis date", "data_type": "DATE", "sample_values": ["2024-11-01", "2024-12-01"]},
                {"name": "churn_risk_score", "description": "Churn risk score (0-100)", "data_type": "INTEGER", "sample_values": [15, 65, 90]},
                {"name": "churn_risk_category", "description": "Risk category", "data_type": "VARCHAR(50)", "sample_values": ["Low Risk", "Medium Risk", "High Risk", "Critical"]},
                {"name": "days_since_last_purchase", "description": "Days since last purchase", "data_type": "INTEGER", "sample_values": [15, 90, 180]},
                {"name": "engagement_score", "description": "Engagement score (0-100)", "data_type": "INTEGER", "sample_values": [85, 45, 15]},
                {"name": "predicted_ltv_next_12mo", "description": "Predicted lifetime value next 12 months", "data_type": "DECIMAL(10,2)", "sample_values": [2500.00, 500.00, 100.00]},
                {"name": "retention_probability_pct", "description": "Probability of retention", "data_type": "DECIMAL(5,2)", "sample_values": [95.00, 65.00, 25.00]},
                {"name": "recommended_action", "description": "Recommended retention action", "data_type": "VARCHAR(200)", "sample_values": ["None", "Send targeted offer", "Personal outreach", "Win-back campaign"]},
            ]
        },
        
        # ============ RETAIL DOMAIN - InventoryIntel Solutions (Vendor 4) ============
        # RELATED DATASETS: Inventory Levels + Product Demand (join on product_id/sku), Stock-outs + Sales Impact (join on store_id/product_id)
        {
            "vendor_email": "contact@inventoryintel.com",
            "title": "Real-Time Inventory Levels and Stock Status",
            "status": "active",
            "visibility": "public",
            "description": "Real-time inventory data including stock levels, warehouse locations, and availability across stores",
            "domain": "Retail",
            "dataset_type": "Time-series",
            "granularity": "SKU-location-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["inventory", "stock levels", "availability", "warehouses"],
            "entities": ["products", "warehouses", "stores"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Real-time"},
            "geographic_coverage": {"countries": ["US", "CA"], "regions": ["North America"]},
            "columns": [
                {"name": "sku", "description": "Stock keeping unit", "data_type": "VARCHAR(50)", "sample_values": ["ELEC-LAP-001", "CLTH-SHR-025", "HOME-FUR-150"]},
                {"name": "product_id", "description": "Product identifier", "data_type": "UUID", "sample_values": ["d4e5f6a7-b8c9-0123-def1-234567890123"]},
                {"name": "location_id", "description": "Store or warehouse identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "location_type", "description": "Type of location", "data_type": "VARCHAR(50)", "sample_values": ["Store", "Warehouse", "Distribution Center"]},
                {"name": "timestamp", "description": "Inventory snapshot timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "quantity_on_hand", "description": "Current quantity on hand", "data_type": "INTEGER", "sample_values": [50, 0, 500]},
                {"name": "quantity_reserved", "description": "Quantity reserved for orders", "data_type": "INTEGER", "sample_values": [10, 0, 50]},
                {"name": "quantity_available", "description": "Available for sale quantity", "data_type": "INTEGER", "sample_values": [40, 0, 450]},
                {"name": "reorder_point", "description": "Reorder point threshold", "data_type": "INTEGER", "sample_values": [20, 10, 100]},
                {"name": "stock_status", "description": "Stock status", "data_type": "VARCHAR(50)", "sample_values": ["In Stock", "Low Stock", "Out of Stock", "Backorder"]},
            ]
        },
        {
            "vendor_email": "contact@inventoryintel.com",
            "title": "Product Demand Forecasting Data",
            "status": "active",
            "visibility": "public",
            "description": "Historical sales patterns, demand forecasts, and predictive inventory planning data",
            "domain": "Retail",
            "dataset_type": "Time-series",
            "granularity": "Product-weekly",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["demand forecasting", "sales patterns", "inventory planning", "predictions"],
            "entities": ["products", "forecasts", "demand"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2025-12-31", "frequency": "Weekly"},
            "geographic_coverage": {"countries": ["US", "CA"], "regions": ["North America"]},
            "columns": [
                {"name": "product_id", "description": "Product identifier", "data_type": "UUID", "sample_values": ["d4e5f6a7-b8c9-0123-def1-234567890123"]},
                {"name": "sku", "description": "Stock keeping unit", "data_type": "VARCHAR(50)", "sample_values": ["ELEC-LAP-001", "CLTH-SHR-025", "HOME-FUR-150"]},
                {"name": "week_start_date", "description": "Week start date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-01-22"]},
                {"name": "historical_demand", "description": "Historical demand (if past week)", "data_type": "INTEGER", "sample_values": [100, 250, 500]},
                {"name": "forecasted_demand", "description": "Forecasted demand", "data_type": "INTEGER", "sample_values": [110, 260, 520]},
                {"name": "forecast_lower_bound", "description": "Forecast lower confidence bound", "data_type": "INTEGER", "sample_values": [90, 230, 480]},
                {"name": "forecast_upper_bound", "description": "Forecast upper confidence bound", "data_type": "INTEGER", "sample_values": [130, 290, 560]},
                {"name": "seasonality_factor", "description": "Seasonality adjustment factor", "data_type": "DECIMAL(5,2)", "sample_values": [1.20, 0.85, 1.50]},
                {"name": "trend_direction", "description": "Demand trend", "data_type": "VARCHAR(50)", "sample_values": ["Increasing", "Stable", "Decreasing"]},
                {"name": "forecast_accuracy_pct", "description": "Historical forecast accuracy", "data_type": "DECIMAL(5,2)", "sample_values": [85.50, 92.30, 78.75]},
            ]
        },
        {
            "vendor_email": "contact@inventoryintel.com",
            "title": "Supply Chain and Shipment Tracking",
            "status": "active",
            "visibility": "public",
            "description": "Inbound shipments, purchase orders, supplier performance, and delivery tracking data",
            "domain": "Retail",
            "dataset_type": "Transactional",
            "granularity": "Shipment-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["supply chain", "shipments", "purchase orders", "suppliers"],
            "entities": ["shipments", "suppliers", "purchase orders"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "CA", "Global"], "regions": ["North America", "Worldwide"]},
            "columns": [
                {"name": "shipment_id", "description": "Unique shipment identifier", "data_type": "UUID", "sample_values": ["f6a7b8c9-d0e1-2345-f123-456789012345"]},
                {"name": "purchase_order_id", "description": "Purchase order identifier", "data_type": "UUID", "sample_values": ["e5f6a7b8-c9d0-1234-ef12-345678901234"]},
                {"name": "supplier_id", "description": "Supplier identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "supplier_name", "description": "Supplier name", "data_type": "VARCHAR(200)", "sample_values": ["Electronics Wholesale Inc", "Fashion Distributors", "Home Goods Co"]},
                {"name": "order_date", "description": "Purchase order date", "data_type": "DATE", "sample_values": ["2024-01-01", "2024-02-15"]},
                {"name": "expected_delivery_date", "description": "Expected delivery date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-03-01"]},
                {"name": "actual_delivery_date", "description": "Actual delivery date", "data_type": "DATE", "sample_values": ["2024-01-16", "2024-02-28"]},
                {"name": "shipment_status", "description": "Shipment status", "data_type": "VARCHAR(50)", "sample_values": ["In Transit", "Delivered", "Delayed", "Cancelled"]},
                {"name": "total_units", "description": "Total units in shipment", "data_type": "INTEGER", "sample_values": [1000, 500, 2500]},
                {"name": "on_time_delivery", "description": "Whether delivered on time", "data_type": "BOOLEAN", "sample_values": [False, True, True]},
            ]
        },
        {
            "vendor_email": "contact@inventoryintel.com",
            "title": "Stock-Out Events and Lost Sales Analysis",
            "status": "active",
            "visibility": "public",
            "description": "Stock-out incidents, duration, estimated lost sales, and out-of-stock impact analytics",
            "domain": "Retail",
            "dataset_type": "Event-based",
            "granularity": "Stock-out-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["stock-outs", "out of stock", "lost sales", "availability"],
            "entities": ["products", "stores", "stock-outs"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "CA"], "regions": ["North America"]},
            "columns": [
                {"name": "stockout_id", "description": "Unique stock-out event identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "product_id", "description": "Product identifier", "data_type": "UUID", "sample_values": ["d4e5f6a7-b8c9-0123-def1-234567890123"]},
                {"name": "store_id", "description": "Store identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "sku", "description": "Stock keeping unit", "data_type": "VARCHAR(50)", "sample_values": ["ELEC-LAP-001", "CLTH-SHR-025", "HOME-FUR-150"]},
                {"name": "stockout_start", "description": "Stock-out start timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 09:00:00", "2024-02-20 14:00:00"]},
                {"name": "stockout_end", "description": "Stock-out end timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-17 15:00:00", "2024-02-22 10:00:00"]},
                {"name": "duration_hours", "description": "Stock-out duration in hours", "data_type": "DECIMAL(8,2)", "sample_values": [54.00, 44.00, 120.00]},
                {"name": "estimated_lost_units", "description": "Estimated lost unit sales", "data_type": "INTEGER", "sample_values": [25, 50, 100]},
                {"name": "estimated_lost_revenue_usd", "description": "Estimated lost revenue", "data_type": "DECIMAL(10,2)", "sample_values": [2500.00, 2500.00, 10000.00]},
                {"name": "root_cause", "description": "Root cause of stock-out", "data_type": "VARCHAR(200)", "sample_values": ["Supplier delay", "Forecast error", "Unexpected demand spike", "Distribution issue"]},
            ]
        },
        {
            "vendor_email": "contact@inventoryintel.com",
            "title": "Warehouse Operations and Fulfillment Metrics",
            "status": "active",
            "visibility": "public",
            "description": "Warehouse efficiency metrics, order fulfillment rates, picking accuracy, and operational performance",
            "domain": "Retail",
            "dataset_type": "Time-series",
            "granularity": "Warehouse-daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["warehouse operations", "fulfillment", "picking", "efficiency"],
            "entities": ["warehouses", "orders", "operations"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "CA"], "regions": ["North America"]},
            "columns": [
                {"name": "warehouse_id", "description": "Unique warehouse identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "warehouse_name", "description": "Warehouse name", "data_type": "VARCHAR(200)", "sample_values": ["East Coast DC", "Midwest Fulfillment", "West Coast Warehouse"]},
                {"name": "date", "description": "Operations date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "orders_processed", "description": "Number of orders processed", "data_type": "INTEGER", "sample_values": [5000, 7500, 12000]},
                {"name": "units_picked", "description": "Total units picked", "data_type": "INTEGER", "sample_values": [25000, 37500, 60000]},
                {"name": "picking_accuracy_pct", "description": "Picking accuracy percentage", "data_type": "DECIMAL(5,2)", "sample_values": [99.50, 99.75, 98.90]},
                {"name": "average_pick_time_seconds", "description": "Average pick time per unit", "data_type": "DECIMAL(6,2)", "sample_values": [45.50, 38.30, 52.75]},
                {"name": "on_time_shipment_pct", "description": "On-time shipment percentage", "data_type": "DECIMAL(5,2)", "sample_values": [95.50, 98.30, 92.75]},
                {"name": "capacity_utilization_pct", "description": "Warehouse capacity utilization", "data_type": "DECIMAL(5,2)", "sample_values": [75.50, 82.30, 68.75]},
                {"name": "labor_hours", "description": "Total labor hours", "data_type": "DECIMAL(8,2)", "sample_values": [1250.00, 1875.00, 3000.00]},
            ]
        },
        
        # ============ TECHNOLOGY DOMAIN - CloudMetrics Analytics (Vendor 1) ============
        # RELATED DATASETS: Cloud Resources + Cost Analysis (join on resource_id), VM Metrics + Scaling Events (join on instance_id)
        {
            "vendor_email": "data@cloudmetrics.io",
            "title": "Cloud Infrastructure Resource Utilization",
            "status": "active",
            "visibility": "public",
            "description": "Cloud resource utilization metrics including CPU, memory, storage, and network usage across multi-cloud environments",
            "domain": "Technology",
            "dataset_type": "Time-series",
            "granularity": "Resource-5min",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["cloud infrastructure", "resource utilization", "monitoring", "performance"],
            "entities": ["resources", "instances", "services"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "5-minute intervals"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "resource_id", "description": "Unique resource identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "timestamp", "description": "Measurement timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "cloud_provider", "description": "Cloud provider", "data_type": "VARCHAR(50)", "sample_values": ["AWS", "Azure", "GCP", "Oracle Cloud"]},
                {"name": "resource_type", "description": "Type of resource", "data_type": "VARCHAR(100)", "sample_values": ["EC2 Instance", "Azure VM", "GCP Compute Engine", "RDS Database"]},
                {"name": "cpu_utilization_pct", "description": "CPU utilization percentage", "data_type": "DECIMAL(5,2)", "sample_values": [45.50, 78.30, 92.75]},
                {"name": "memory_utilization_pct", "description": "Memory utilization percentage", "data_type": "DECIMAL(5,2)", "sample_values": [65.50, 82.30, 58.75]},
                {"name": "disk_io_mbps", "description": "Disk I/O in megabytes per second", "data_type": "DECIMAL(10,2)", "sample_values": [125.50, 85.30, 450.75]},
                {"name": "network_in_mbps", "description": "Network inbound traffic in Mbps", "data_type": "DECIMAL(10,2)", "sample_values": [50.50, 125.30, 300.75]},
                {"name": "network_out_mbps", "description": "Network outbound traffic in Mbps", "data_type": "DECIMAL(10,2)", "sample_values": [30.50, 85.30, 200.75]},
                {"name": "region", "description": "Cloud region", "data_type": "VARCHAR(50)", "sample_values": ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]},
            ]
        },
        {
            "vendor_email": "data@cloudmetrics.io",
            "title": "Cloud Cost and Billing Analytics",
            "status": "active",
            "visibility": "public",
            "description": "Detailed cloud cost breakdown, billing data, and cost optimization recommendations across services",
            "domain": "Technology",
            "dataset_type": "Time-series",
            "granularity": "Resource-daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["cloud costs", "billing", "cost optimization", "FinOps"],
            "entities": ["resources", "accounts", "services"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "billing_id", "description": "Unique billing record identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "resource_id", "description": "Resource identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "date", "description": "Billing date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "cloud_provider", "description": "Cloud provider", "data_type": "VARCHAR(50)", "sample_values": ["AWS", "Azure", "GCP", "Oracle Cloud"]},
                {"name": "service_name", "description": "Cloud service name", "data_type": "VARCHAR(100)", "sample_values": ["EC2", "S3", "Lambda", "RDS", "Azure VM"]},
                {"name": "cost_usd", "description": "Daily cost in USD", "data_type": "DECIMAL(12,2)", "sample_values": [125.50, 85.30, 450.75]},
                {"name": "usage_quantity", "description": "Usage quantity", "data_type": "DECIMAL(15,2)", "sample_values": [1000.00, 500.00, 2500.00]},
                {"name": "usage_unit", "description": "Unit of usage", "data_type": "VARCHAR(50)", "sample_values": ["GB-Hours", "Requests", "Instance-Hours", "GB-Month"]},
                {"name": "account_id", "description": "Cloud account identifier", "data_type": "VARCHAR(100)", "sample_values": ["123456789012", "abcd-1234-efgh-5678"]},
                {"name": "tags", "description": "Resource tags (JSON)", "data_type": "VARCHAR(500)", "sample_values": ["{\"Environment\": \"Production\", \"Team\": \"Engineering\"}"]},
            ]
        },
        {
            "vendor_email": "data@cloudmetrics.io",
            "title": "Virtual Machine and Container Metrics",
            "status": "active",
            "visibility": "public",
            "description": "VM and container performance metrics, health status, and orchestration data",
            "domain": "Technology",
            "dataset_type": "Time-series",
            "granularity": "Instance-1min",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["virtual machines", "containers", "Kubernetes", "orchestration"],
            "entities": ["instances", "containers", "pods", "nodes"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "1-minute intervals"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "instance_id", "description": "Unique instance/container identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "timestamp", "description": "Measurement timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "instance_type", "description": "Instance or container type", "data_type": "VARCHAR(100)", "sample_values": ["VM", "Docker Container", "Kubernetes Pod"]},
                {"name": "status", "description": "Instance status", "data_type": "VARCHAR(50)", "sample_values": ["Running", "Stopped", "Terminated", "Pending"]},
                {"name": "uptime_seconds", "description": "Uptime in seconds", "data_type": "INTEGER", "sample_values": [86400, 172800, 604800]},
                {"name": "cpu_cores", "description": "Number of CPU cores", "data_type": "INTEGER", "sample_values": [2, 4, 8, 16]},
                {"name": "memory_gb", "description": "Memory in gigabytes", "data_type": "INTEGER", "sample_values": [8, 16, 32, 64]},
                {"name": "restart_count", "description": "Number of restarts", "data_type": "INTEGER", "sample_values": [0, 1, 5]},
                {"name": "health_status", "description": "Health check status", "data_type": "VARCHAR(50)", "sample_values": ["Healthy", "Unhealthy", "Degraded"]},
                {"name": "orchestrator", "description": "Orchestration platform", "data_type": "VARCHAR(50)", "sample_values": ["Kubernetes", "Docker Swarm", "ECS", "None"]},
            ]
        },
        {
            "vendor_email": "data@cloudmetrics.io",
            "title": "Auto-Scaling Events and Capacity Planning",
            "status": "active",
            "visibility": "public",
            "description": "Auto-scaling activity, capacity planning data, and elasticity metrics",
            "domain": "Technology",
            "dataset_type": "Event-based",
            "granularity": "Event-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["auto-scaling", "capacity planning", "elasticity", "optimization"],
            "entities": ["scaling events", "instances", "groups"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "event_id", "description": "Unique scaling event identifier", "data_type": "UUID", "sample_values": ["d4e5f6a7-b8c9-0123-def1-234567890123"]},
                {"name": "instance_id", "description": "Instance identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "event_timestamp", "description": "Event timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "scaling_action", "description": "Type of scaling action", "data_type": "VARCHAR(50)", "sample_values": ["Scale Up", "Scale Down", "Scale Out", "Scale In"]},
                {"name": "trigger_metric", "description": "Metric that triggered scaling", "data_type": "VARCHAR(100)", "sample_values": ["CPU > 80%", "Memory > 90%", "Request Rate > 1000/s"]},
                {"name": "instances_before", "description": "Instance count before scaling", "data_type": "INTEGER", "sample_values": [2, 4, 8]},
                {"name": "instances_after", "description": "Instance count after scaling", "data_type": "INTEGER", "sample_values": [4, 8, 16]},
                {"name": "cost_impact_usd", "description": "Estimated cost impact", "data_type": "DECIMAL(10,2)", "sample_values": [100.00, 200.00, 500.00]},
                {"name": "duration_seconds", "description": "Scaling event duration", "data_type": "INTEGER", "sample_values": [300, 600, 1200]},
            ]
        },
        {
            "vendor_email": "data@cloudmetrics.io",
            "title": "SaaS Application Performance Monitoring",
            "status": "active",
            "visibility": "public",
            "description": "SaaS application performance metrics, response times, error rates, and availability data",
            "domain": "Technology",
            "dataset_type": "Time-series",
            "granularity": "Application-5min",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["SaaS", "APM", "performance monitoring", "availability"],
            "entities": ["applications", "endpoints", "transactions"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "5-minute intervals"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "application_id", "description": "Unique application identifier", "data_type": "UUID", "sample_values": ["e5f6a7b8-c9d0-1234-ef12-345678901234"]},
                {"name": "timestamp", "description": "Measurement timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "application_name", "description": "Application name", "data_type": "VARCHAR(200)", "sample_values": ["Sales CRM", "HR Portal", "Customer Dashboard"]},
                {"name": "response_time_ms", "description": "Average response time in milliseconds", "data_type": "DECIMAL(10,2)", "sample_values": [125.50, 85.30, 450.75]},
                {"name": "throughput_rpm", "description": "Throughput in requests per minute", "data_type": "INTEGER", "sample_values": [5000, 12000, 25000]},
                {"name": "error_rate_pct", "description": "Error rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [0.05, 0.15, 1.50]},
                {"name": "availability_pct", "description": "Availability percentage", "data_type": "DECIMAL(5,2)", "sample_values": [99.99, 99.95, 99.90]},
                {"name": "active_users", "description": "Active concurrent users", "data_type": "INTEGER", "sample_values": [500, 1200, 2500]},
                {"name": "apdex_score", "description": "Application Performance Index score", "data_type": "DECIMAL(3,2)", "sample_values": [0.95, 0.85, 0.75]},
            ]
        },
        
        # ============ TECHNOLOGY DOMAIN - DevOps Intelligence (Vendor 2) ============
        # RELATED DATASETS: Deployments + Incidents (join on deployment_id), CI/CD Pipelines + Build Performance (join on pipeline_id)
        {
            "vendor_email": "info@devopsdata.com",
            "title": "Software Deployment and Release Data",
            "status": "active",
            "visibility": "public",
            "description": "Software deployment history, release frequency, rollback data, and deployment success metrics",
            "domain": "Technology",
            "dataset_type": "Event-based",
            "granularity": "Deployment-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["deployments", "releases", "software delivery", "DevOps"],
            "entities": ["deployments", "releases", "environments"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "deployment_id", "description": "Unique deployment identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "deployment_timestamp", "description": "Deployment timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "application_name", "description": "Application name", "data_type": "VARCHAR(200)", "sample_values": ["API Gateway", "Frontend App", "Database Service"]},
                {"name": "environment", "description": "Deployment environment", "data_type": "VARCHAR(50)", "sample_values": ["Production", "Staging", "Development", "QA"]},
                {"name": "version", "description": "Software version", "data_type": "VARCHAR(50)", "sample_values": ["v1.2.3", "v2.0.0", "v1.5.10"]},
                {"name": "deployment_status", "description": "Deployment status", "data_type": "VARCHAR(50)", "sample_values": ["Success", "Failed", "Rolled Back", "In Progress"]},
                {"name": "duration_seconds", "description": "Deployment duration in seconds", "data_type": "INTEGER", "sample_values": [300, 600, 1200]},
                {"name": "deployed_by", "description": "User who initiated deployment", "data_type": "VARCHAR(100)", "sample_values": ["john.doe@company.com", "automated-system", "jane.smith@company.com"]},
                {"name": "rollback", "description": "Whether deployment was rolled back", "data_type": "BOOLEAN", "sample_values": [False, True, False]},
                {"name": "change_size_lines", "description": "Code change size in lines", "data_type": "INTEGER", "sample_values": [50, 500, 5000]},
            ]
        },
        {
            "vendor_email": "info@devopsdata.com",
            "title": "Incident and Outage Tracking",
            "status": "active",
            "visibility": "public",
            "description": "Incident tracking data, outage duration, root cause analysis, and MTTR metrics",
            "domain": "Technology",
            "dataset_type": "Event-based",
            "granularity": "Incident-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["incidents", "outages", "MTTR", "reliability"],
            "entities": ["incidents", "services", "teams"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "incident_id", "description": "Unique incident identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "deployment_id", "description": "Related deployment ID (if applicable)", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "incident_start", "description": "Incident start timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "incident_end", "description": "Incident resolution timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 16:30:00", "2024-02-20 20:45:00"]},
                {"name": "severity", "description": "Incident severity", "data_type": "VARCHAR(50)", "sample_values": ["Critical", "High", "Medium", "Low"]},
                {"name": "affected_service", "description": "Affected service name", "data_type": "VARCHAR(200)", "sample_values": ["API Gateway", "Database", "Frontend", "Authentication Service"]},
                {"name": "mttr_minutes", "description": "Mean time to resolution in minutes", "data_type": "INTEGER", "sample_values": [120, 60, 30]},
                {"name": "users_impacted", "description": "Number of users impacted", "data_type": "INTEGER", "sample_values": [10000, 5000, 1000]},
                {"name": "root_cause", "description": "Root cause category", "data_type": "VARCHAR(200)", "sample_values": ["Deployment Issue", "Infrastructure Failure", "Configuration Error", "Third-party Service"]},
                {"name": "postmortem_completed", "description": "Whether postmortem was completed", "data_type": "BOOLEAN", "sample_values": [True, True, False]},
            ]
        },
        {
            "vendor_email": "info@devopsdata.com",
            "title": "CI/CD Pipeline Execution Metrics",
            "status": "active",
            "visibility": "public",
            "description": "CI/CD pipeline execution data, build times, test results, and pipeline success rates",
            "domain": "Technology",
            "dataset_type": "Event-based",
            "granularity": "Pipeline-run-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["CI/CD", "pipelines", "builds", "testing"],
            "entities": ["pipelines", "builds", "tests"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "pipeline_id", "description": "Unique pipeline identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "run_id", "description": "Pipeline run identifier", "data_type": "UUID", "sample_values": ["d4e5f6a7-b8c9-0123-def1-234567890123"]},
                {"name": "start_timestamp", "description": "Pipeline start timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "pipeline_name", "description": "Pipeline name", "data_type": "VARCHAR(200)", "sample_values": ["Backend Build", "Frontend Deploy", "Integration Tests"]},
                {"name": "status", "description": "Pipeline execution status", "data_type": "VARCHAR(50)", "sample_values": ["Success", "Failed", "Cancelled", "In Progress"]},
                {"name": "duration_seconds", "description": "Pipeline duration in seconds", "data_type": "INTEGER", "sample_values": [300, 600, 1200]},
                {"name": "tests_run", "description": "Number of tests executed", "data_type": "INTEGER", "sample_values": [500, 1200, 2500]},
                {"name": "tests_passed", "description": "Number of tests passed", "data_type": "INTEGER", "sample_values": [495, 1180, 2450]},
                {"name": "tests_failed", "description": "Number of tests failed", "data_type": "INTEGER", "sample_values": [5, 20, 50]},
                {"name": "code_coverage_pct", "description": "Code coverage percentage", "data_type": "DECIMAL(5,2)", "sample_values": [85.50, 92.30, 78.75]},
            ]
        },
        {
            "vendor_email": "info@devopsdata.com",
            "title": "Build Performance and Artifact Metrics",
            "status": "active",
            "visibility": "public",
            "description": "Build performance data, artifact sizes, compilation times, and dependency tracking",
            "domain": "Technology",
            "dataset_type": "Event-based",
            "granularity": "Build-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["builds", "artifacts", "compilation", "dependencies"],
            "entities": ["builds", "artifacts", "dependencies"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "build_id", "description": "Unique build identifier", "data_type": "UUID", "sample_values": ["e5f6a7b8-c9d0-1234-ef12-345678901234"]},
                {"name": "pipeline_id", "description": "Pipeline identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "build_timestamp", "description": "Build timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "compilation_time_seconds", "description": "Compilation time in seconds", "data_type": "INTEGER", "sample_values": [120, 300, 600]},
                {"name": "artifact_size_mb", "description": "Artifact size in megabytes", "data_type": "DECIMAL(10,2)", "sample_values": [125.50, 85.30, 450.75]},
                {"name": "dependency_count", "description": "Number of dependencies", "data_type": "INTEGER", "sample_values": [50, 125, 300]},
                {"name": "cache_hit_rate_pct", "description": "Build cache hit rate", "data_type": "DECIMAL(5,2)", "sample_values": [85.50, 92.30, 78.75]},
                {"name": "build_agent", "description": "Build agent identifier", "data_type": "VARCHAR(100)", "sample_values": ["agent-01", "agent-02", "cloud-runner-1"]},
                {"name": "success", "description": "Whether build succeeded", "data_type": "BOOLEAN", "sample_values": [True, True, False]},
            ]
        },
        {
            "vendor_email": "info@devopsdata.com",
            "title": "DORA Metrics and DevOps Performance",
            "status": "active",
            "visibility": "public",
            "description": "DORA metrics including deployment frequency, lead time, MTTR, and change failure rate",
            "domain": "Technology",
            "dataset_type": "Time-series",
            "granularity": "Team-weekly",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["DORA metrics", "DevOps performance", "software delivery", "benchmarking"],
            "entities": ["teams", "services", "metrics"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Weekly"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "team_id", "description": "Unique team identifier", "data_type": "UUID", "sample_values": ["f6a7b8c9-d0e1-2345-f123-456789012345"]},
                {"name": "week_start_date", "description": "Week start date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-01-22"]},
                {"name": "deployment_frequency", "description": "Deployments per week", "data_type": "INTEGER", "sample_values": [5, 15, 50]},
                {"name": "lead_time_hours", "description": "Lead time for changes in hours", "data_type": "DECIMAL(10,2)", "sample_values": [24.50, 48.30, 168.75]},
                {"name": "mttr_minutes", "description": "Mean time to recovery in minutes", "data_type": "INTEGER", "sample_values": [30, 60, 120]},
                {"name": "change_failure_rate_pct", "description": "Change failure rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [5.00, 10.00, 15.00]},
                {"name": "total_deployments", "description": "Total deployments", "data_type": "INTEGER", "sample_values": [5, 15, 50]},
                {"name": "failed_deployments", "description": "Failed deployments", "data_type": "INTEGER", "sample_values": [0, 1, 5]},
                {"name": "performance_category", "description": "DORA performance category", "data_type": "VARCHAR(50)", "sample_values": ["Elite", "High", "Medium", "Low"]},
            ]
        },
        
        # ============ TECHNOLOGY DOMAIN - API Analytics Pro (Vendor 3) ============
        # RELATED DATASETS: API Requests + Error Analysis (join on api_key/endpoint_id), Rate Limits + Usage Patterns (join on api_key)
        {
            "vendor_email": "sales@apianalytics.net",
            "title": "API Request Logs and Usage Data",
            "status": "active",
            "visibility": "public",
            "description": "Comprehensive API request logs including endpoints, response times, status codes, and usage patterns",
            "domain": "Technology",
            "dataset_type": "Time-series",
            "granularity": "Request-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["API analytics", "request logs", "usage tracking", "monitoring"],
            "entities": ["requests", "endpoints", "clients"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Real-time"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "request_id", "description": "Unique request identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "timestamp", "description": "Request timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "api_key", "description": "API key identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "endpoint", "description": "API endpoint path", "data_type": "VARCHAR(500)", "sample_values": ["/api/v1/users", "/api/v1/products", "/api/v2/orders"]},
                {"name": "http_method", "description": "HTTP method", "data_type": "VARCHAR(10)", "sample_values": ["GET", "POST", "PUT", "DELETE", "PATCH"]},
                {"name": "status_code", "description": "HTTP status code", "data_type": "INTEGER", "sample_values": [200, 201, 400, 404, 500]},
                {"name": "response_time_ms", "description": "Response time in milliseconds", "data_type": "DECIMAL(10,2)", "sample_values": [125.50, 85.30, 450.75]},
                {"name": "request_size_bytes", "description": "Request size in bytes", "data_type": "INTEGER", "sample_values": [1024, 2048, 5120]},
                {"name": "response_size_bytes", "description": "Response size in bytes", "data_type": "INTEGER", "sample_values": [2048, 4096, 10240]},
                {"name": "client_ip", "description": "Client IP address", "data_type": "VARCHAR(50)", "sample_values": ["192.168.1.1", "10.0.0.5"]},
            ]
        },
        {
            "vendor_email": "sales@apianalytics.net",
            "title": "API Error and Exception Tracking",
            "status": "active",
            "visibility": "public",
            "description": "API error tracking, exception details, error rates, and failure pattern analysis",
            "domain": "Technology",
            "dataset_type": "Event-based",
            "granularity": "Error-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["API errors", "exceptions", "failure tracking", "debugging"],
            "entities": ["errors", "endpoints", "clients"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "error_id", "description": "Unique error identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "request_id", "description": "Request identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "api_key", "description": "API key identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "error_timestamp", "description": "Error timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "endpoint", "description": "API endpoint path", "data_type": "VARCHAR(500)", "sample_values": ["/api/v1/users", "/api/v1/products"]},
                {"name": "error_type", "description": "Error type or category", "data_type": "VARCHAR(100)", "sample_values": ["ValidationError", "AuthenticationError", "RateLimitExceeded", "InternalServerError"]},
                {"name": "error_message", "description": "Error message", "data_type": "VARCHAR(1000)", "sample_values": ["Invalid request parameters", "API key expired", "Rate limit exceeded"]},
                {"name": "status_code", "description": "HTTP status code", "data_type": "INTEGER", "sample_values": [400, 401, 403, 429, 500]},
                {"name": "stack_trace", "description": "Stack trace (truncated)", "data_type": "VARCHAR(2000)", "sample_values": ["at function1()..."]},
            ]
        },
        {
            "vendor_email": "sales@apianalytics.net",
            "title": "API Rate Limiting and Throttling Data",
            "status": "active",
            "visibility": "public",
            "description": "Rate limit enforcement, throttling events, quota usage, and API consumption patterns",
            "domain": "Technology",
            "dataset_type": "Time-series",
            "granularity": "Client-hourly",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["rate limiting", "throttling", "quotas", "API consumption"],
            "entities": ["clients", "quotas", "limits"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Hourly"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "record_id", "description": "Unique record identifier", "data_type": "UUID", "sample_values": ["d4e5f6a7-b8c9-0123-def1-234567890123"]},
                {"name": "api_key", "description": "API key identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "hour_timestamp", "description": "Hour timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:00:00", "2024-02-20 18:00:00"]},
                {"name": "requests_made", "description": "Requests made in hour", "data_type": "INTEGER", "sample_values": [5000, 12000, 25000]},
                {"name": "rate_limit", "description": "Rate limit per hour", "data_type": "INTEGER", "sample_values": [10000, 50000, 100000]},
                {"name": "throttled_requests", "description": "Number of throttled requests", "data_type": "INTEGER", "sample_values": [0, 100, 500]},
                {"name": "quota_remaining", "description": "Remaining quota", "data_type": "INTEGER", "sample_values": [5000, 38000, 75000]},
                {"name": "quota_reset_timestamp", "description": "Quota reset timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 15:00:00", "2024-02-20 19:00:00"]},
                {"name": "tier", "description": "API tier or plan", "data_type": "VARCHAR(50)", "sample_values": ["Free", "Starter", "Professional", "Enterprise"]},
            ]
        },
        {
            "vendor_email": "sales@apianalytics.net",
            "title": "API Endpoint Performance Benchmarks",
            "status": "active",
            "visibility": "public",
            "description": "Endpoint-level performance benchmarks, latency percentiles, and throughput analytics",
            "domain": "Technology",
            "dataset_type": "Time-series",
            "granularity": "Endpoint-daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["endpoint performance", "benchmarks", "latency", "throughput"],
            "entities": ["endpoints", "performance", "metrics"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "endpoint_id", "description": "Unique endpoint identifier", "data_type": "UUID", "sample_values": ["e5f6a7b8-c9d0-1234-ef12-345678901234"]},
                {"name": "date", "description": "Analytics date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "endpoint_path", "description": "API endpoint path", "data_type": "VARCHAR(500)", "sample_values": ["/api/v1/users", "/api/v1/products", "/api/v2/orders"]},
                {"name": "total_requests", "description": "Total requests", "data_type": "INTEGER", "sample_values": [50000, 120000, 250000]},
                {"name": "avg_response_time_ms", "description": "Average response time", "data_type": "DECIMAL(10,2)", "sample_values": [125.50, 85.30, 450.75]},
                {"name": "p50_response_time_ms", "description": "50th percentile response time", "data_type": "DECIMAL(10,2)", "sample_values": [100.00, 75.00, 400.00]},
                {"name": "p95_response_time_ms", "description": "95th percentile response time", "data_type": "DECIMAL(10,2)", "sample_values": [250.00, 150.00, 800.00]},
                {"name": "p99_response_time_ms", "description": "99th percentile response time", "data_type": "DECIMAL(10,2)", "sample_values": [500.00, 300.00, 1500.00]},
                {"name": "error_rate_pct", "description": "Error rate percentage", "data_type": "DECIMAL(5,2)", "sample_values": [0.05, 0.15, 1.50]},
                {"name": "throughput_rpm", "description": "Throughput in requests per minute", "data_type": "INTEGER", "sample_values": [5000, 12000, 25000]},
            ]
        },
        {
            "vendor_email": "sales@apianalytics.net",
            "title": "API Consumer and Integration Analytics",
            "status": "active",
            "visibility": "public",
            "description": "API consumer behavior, integration patterns, adoption metrics, and developer platform usage",
            "domain": "Technology",
            "dataset_type": "Profile",
            "granularity": "Consumer-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["API consumers", "integrations", "developer platform", "adoption"],
            "entities": ["consumers", "integrations", "developers"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Updated continuously"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "consumer_id", "description": "Unique consumer identifier", "data_type": "UUID", "sample_values": ["f6a7b8c9-d0e1-2345-f123-456789012345"]},
                {"name": "api_key", "description": "API key identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "registration_date", "description": "API key registration date", "data_type": "DATE", "sample_values": ["2020-03-15", "2021-07-22"]},
                {"name": "tier", "description": "API tier or plan", "data_type": "VARCHAR(50)", "sample_values": ["Free", "Starter", "Professional", "Enterprise"]},
                {"name": "total_requests_lifetime", "description": "Total requests lifetime", "data_type": "INTEGER", "sample_values": [500000, 1200000, 2500000]},
                {"name": "endpoints_used", "description": "Number of unique endpoints used", "data_type": "INTEGER", "sample_values": [5, 15, 50]},
                {"name": "last_request_date", "description": "Last request date", "data_type": "DATE", "sample_values": ["2024-11-15", "2024-12-01"]},
                {"name": "average_daily_requests", "description": "Average daily requests", "data_type": "INTEGER", "sample_values": [5000, 12000, 25000]},
                {"name": "integration_type", "description": "Type of integration", "data_type": "VARCHAR(100)", "sample_values": ["Web Application", "Mobile App", "Backend Service", "Data Pipeline"]},
                {"name": "active_status", "description": "Whether consumer is active", "data_type": "BOOLEAN", "sample_values": [True, True, False]},
            ]
        },
        
        # ============ TECHNOLOGY DOMAIN - SaaS Usage Insights (Vendor 4) ============
        # RELATED DATASETS: User Activity + Feature Usage (join on user_id), Feature Adoption + User Segments (join on feature_id)
        {
            "vendor_email": "contact@usageinsights.com",
            "title": "SaaS Application User Activity Logs",
            "status": "active",
            "visibility": "public",
            "description": "User activity logs including sessions, actions, page views, and engagement patterns",
            "domain": "Technology",
            "dataset_type": "Time-series",
            "granularity": "Event-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["user activity", "sessions", "engagement", "product analytics"],
            "entities": ["users", "sessions", "actions"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Real-time"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "event_id", "description": "Unique event identifier", "data_type": "UUID", "sample_values": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"]},
                {"name": "user_id", "description": "Anonymized user identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "session_id", "description": "Session identifier", "data_type": "UUID", "sample_values": ["c3d4e5f6-a7b8-9012-cdef-123456789012"]},
                {"name": "timestamp", "description": "Event timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "event_type", "description": "Type of event", "data_type": "VARCHAR(100)", "sample_values": ["page_view", "button_click", "form_submit", "feature_used"]},
                {"name": "page_url", "description": "Page URL", "data_type": "VARCHAR(500)", "sample_values": ["/dashboard", "/reports", "/settings"]},
                {"name": "feature_name", "description": "Feature name (if applicable)", "data_type": "VARCHAR(200)", "sample_values": ["Export Data", "Create Report", "Share Dashboard"]},
                {"name": "device_type", "description": "Device type", "data_type": "VARCHAR(50)", "sample_values": ["Desktop", "Mobile", "Tablet"]},
                {"name": "browser", "description": "Web browser", "data_type": "VARCHAR(50)", "sample_values": ["Chrome", "Safari", "Firefox", "Edge"]},
            ]
        },
        {
            "vendor_email": "contact@usageinsights.com",
            "title": "Feature Usage and Adoption Metrics",
            "status": "active",
            "visibility": "public",
            "description": "Feature-level usage metrics, adoption rates, engagement, and feature performance data",
            "domain": "Technology",
            "dataset_type": "Time-series",
            "granularity": "Feature-daily",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["feature usage", "adoption", "product analytics", "engagement"],
            "entities": ["features", "users", "usage"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Daily"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "feature_id", "description": "Unique feature identifier", "data_type": "UUID", "sample_values": ["d4e5f6a7-b8c9-0123-def1-234567890123"]},
                {"name": "date", "description": "Analytics date", "data_type": "DATE", "sample_values": ["2024-01-15", "2024-02-20"]},
                {"name": "feature_name", "description": "Feature name", "data_type": "VARCHAR(200)", "sample_values": ["Export Data", "Create Report", "Share Dashboard", "API Integration"]},
                {"name": "total_users", "description": "Total unique users", "data_type": "INTEGER", "sample_values": [5000, 12000, 25000]},
                {"name": "feature_users", "description": "Users who used feature", "data_type": "INTEGER", "sample_values": [500, 2400, 7500]},
                {"name": "adoption_rate_pct", "description": "Feature adoption rate", "data_type": "DECIMAL(5,2)", "sample_values": [10.00, 20.00, 30.00]},
                {"name": "total_usage_count", "description": "Total feature usage count", "data_type": "INTEGER", "sample_values": [5000, 12000, 25000]},
                {"name": "avg_usage_per_user", "description": "Average usage per user", "data_type": "DECIMAL(10,2)", "sample_values": [10.00, 5.00, 3.33]},
                {"name": "power_users_count", "description": "Power users (>10 uses)", "data_type": "INTEGER", "sample_values": [250, 600, 1250]},
            ]
        },
        {
            "vendor_email": "contact@usageinsights.com",
            "title": "User Segmentation and Cohort Analysis",
            "status": "active",
            "visibility": "public",
            "description": "User segmentation data, cohort behavior, retention analysis, and customer lifetime value",
            "domain": "Technology",
            "dataset_type": "Profile",
            "granularity": "User-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["user segmentation", "cohorts", "retention", "customer lifetime value"],
            "entities": ["users", "cohorts", "segments"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Updated continuously"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "user_id", "description": "Unique user identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "signup_date", "description": "User signup date", "data_type": "DATE", "sample_values": ["2020-03-15", "2021-07-22"]},
                {"name": "cohort", "description": "User cohort (month/year)", "data_type": "VARCHAR(50)", "sample_values": ["2020-03", "2021-07", "2024-01"]},
                {"name": "segment", "description": "User segment", "data_type": "VARCHAR(100)", "sample_values": ["Power User", "Casual User", "At Risk", "Churned"]},
                {"name": "total_sessions", "description": "Total sessions lifetime", "data_type": "INTEGER", "sample_values": [500, 1200, 2500]},
                {"name": "total_actions", "description": "Total actions lifetime", "data_type": "INTEGER", "sample_values": [5000, 12000, 25000]},
                {"name": "days_active", "description": "Total days active", "data_type": "INTEGER", "sample_values": [100, 250, 500]},
                {"name": "last_active_date", "description": "Last active date", "data_type": "DATE", "sample_values": ["2024-11-15", "2024-12-01"]},
                {"name": "ltv_usd", "description": "Customer lifetime value in USD", "data_type": "DECIMAL(10,2)", "sample_values": [500.00, 1200.00, 2500.00]},
                {"name": "retention_day_30", "description": "Retained after 30 days", "data_type": "BOOLEAN", "sample_values": [True, True, False]},
            ]
        },
        {
            "vendor_email": "contact@usageinsights.com",
            "title": "Product Onboarding and Activation Data",
            "status": "active",
            "visibility": "public",
            "description": "User onboarding metrics, activation events, time-to-value, and onboarding funnel data",
            "domain": "Technology",
            "dataset_type": "Event-based",
            "granularity": "User-level",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["onboarding", "activation", "time to value", "user journey"],
            "entities": ["users", "onboarding", "activation"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Event-based"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "user_id", "description": "Unique user identifier", "data_type": "UUID", "sample_values": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"]},
                {"name": "signup_timestamp", "description": "User signup timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 14:30:00", "2024-02-20 18:45:00"]},
                {"name": "activation_timestamp", "description": "Activation event timestamp", "data_type": "TIMESTAMP", "sample_values": ["2024-01-15 15:30:00", "2024-02-20 19:45:00"]},
                {"name": "time_to_activation_hours", "description": "Time to activation in hours", "data_type": "DECIMAL(10,2)", "sample_values": [1.00, 5.00, 24.00]},
                {"name": "onboarding_steps_completed", "description": "Number of onboarding steps completed", "data_type": "INTEGER", "sample_values": [3, 5, 7]},
                {"name": "onboarding_steps_total", "description": "Total onboarding steps", "data_type": "INTEGER", "sample_values": [7, 7, 7]},
                {"name": "activated", "description": "Whether user activated", "data_type": "BOOLEAN", "sample_values": [True, True, False]},
                {"name": "first_key_action", "description": "First key action taken", "data_type": "VARCHAR(200)", "sample_values": ["Created first report", "Invited team member", "Integrated API"]},
                {"name": "trial_converted", "description": "Whether trial converted to paid", "data_type": "BOOLEAN", "sample_values": [True, False, True]},
            ]
        },
        {
            "vendor_email": "contact@usageinsights.com",
            "title": "SaaS Revenue and Subscription Metrics",
            "status": "active",
            "visibility": "public",
            "description": "Subscription revenue data, MRR, ARR, churn, expansion, and financial performance metrics",
            "domain": "Technology",
            "dataset_type": "Time-series",
            "granularity": "Account-monthly",
            "pricing_model": "Subscription",
            "license": "Commercial Use Allowed",
            "topics": ["SaaS metrics", "revenue", "MRR", "ARR", "churn"],
            "entities": ["accounts", "subscriptions", "revenue"],
            "temporal_coverage": {"start_date": "2020-01-01", "end_date": "2024-12-31", "frequency": "Monthly"},
            "geographic_coverage": {"countries": ["US", "Global"], "regions": ["Worldwide"]},
            "columns": [
                {"name": "account_id", "description": "Unique account identifier", "data_type": "UUID", "sample_values": ["e5f6a7b8-c9d0-1234-ef12-345678901234"]},
                {"name": "month", "description": "Revenue month", "data_type": "DATE", "sample_values": ["2024-01-01", "2024-02-01"]},
                {"name": "plan_name", "description": "Subscription plan name", "data_type": "VARCHAR(100)", "sample_values": ["Free", "Starter", "Professional", "Enterprise"]},
                {"name": "mrr_usd", "description": "Monthly recurring revenue", "data_type": "DECIMAL(12,2)", "sample_values": [0.00, 99.00, 499.00, 2999.00]},
                {"name": "arr_usd", "description": "Annual recurring revenue", "data_type": "DECIMAL(12,2)", "sample_values": [0.00, 1188.00, 5988.00, 35988.00]},
                {"name": "subscription_status", "description": "Subscription status", "data_type": "VARCHAR(50)", "sample_values": ["Active", "Cancelled", "Trial", "Expired"]},
                {"name": "seats", "description": "Number of seats/licenses", "data_type": "INTEGER", "sample_values": [1, 5, 10, 50]},
                {"name": "churned", "description": "Whether account churned", "data_type": "BOOLEAN", "sample_values": [False, False, True]},
                {"name": "expansion_revenue_usd", "description": "Expansion revenue", "data_type": "DECIMAL(10,2)", "sample_values": [0.00, 100.00, 500.00]},
            ]
        },
    ]
    
    for ds in datasets:
        topics_json = json.dumps(ds['topics']).replace("'", "''")
        entities_json = json.dumps(ds['entities']).replace("'", "''")
        temporal_json = json.dumps(ds['temporal_coverage']).replace("'", "''")
        geographic_json = json.dumps(ds['geographic_coverage']).replace("'", "''")
        
        # Build embedding_input (simplified - backend will regenerate proper embeddings)
        embedding_text_input = build_embedding_input(ds)
        vector_float = await generate_embedding_vector(embedding_text_input)
        vector_str = str(vector_float)
        
        sql_lines.append(
            f"INSERT INTO datasets (vendor_id, title, status, visibility, description, domain, dataset_type, "
            f"granularity, pricing_model, license, topics, entities, temporal_coverage, geographic_coverage, embedding_input, embedding) "
            f"VALUES ("
            f"(SELECT id FROM vendors WHERE user_id = (SELECT id FROM users WHERE email = '{ds['vendor_email']}')), "
            f"'{ds['title']}', '{ds['status']}', '{ds['visibility']}', '{ds['description']}', "
            f"'{ds['domain']}', '{ds['dataset_type']}', '{ds['granularity']}', '{ds['pricing_model']}', "
            f"'{ds['license']}', '{topics_json}'::jsonb, '{entities_json}'::jsonb, "
            f"'{temporal_json}'::jsonb, '{geographic_json}'::jsonb, '{embedding_text_input}', '{vector_str}'::vector);"
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
    
# --- 6. CONVERSATIONS ---
    sql_lines.extend(["", "-- ========================================", "-- 6. CONVERSATIONS", "-- ========================================", ""])
    
    # Conversation 1: Finance domain - Stock market data inquiry
    convo_title_1 = "Stock Market Data Inquiry"
    sql_lines.append(
        f"INSERT INTO conversations (user_id, title) "
        f"VALUES ((SELECT id FROM users WHERE email = 'olivia.zhang@quanthedge.com'), '{convo_title_1}');"
    )
    
    # Conversation 2: Healthcare domain - Clinical trial data
    convo_title_2 = "Clinical Trial Data Request"
    sql_lines.append(
        f"INSERT INTO conversations (user_id, title) "
        f"VALUES ((SELECT id FROM users WHERE email = 'mia.santos@roche-analytics.ch'), '{convo_title_2}');"
    )
    
    # Conversation 3: Retail domain - E-commerce analytics
    convo_title_3 = "E-commerce Analytics Discussion"
    sql_lines.append(
        f"INSERT INTO conversations (user_id, title) "
        f"VALUES ((SELECT id FROM users WHERE email = 'jack.bennett@amazon-retail.com'), '{convo_title_3}');"
    )
    
    # Conversation 4: Technology domain - Cloud metrics
    convo_title_4 = "Cloud Infrastructure Metrics"
    sql_lines.append(
        f"INSERT INTO conversations (user_id, title) "
        f"VALUES ((SELECT id FROM users WHERE email = 'lily.ross@google-cloud.com'), '{convo_title_4}');"
    )
    
    # Conversation 5: Sports domain - Player performance data
    convo_title_5 = "Player Performance Analytics"
    sql_lines.append(
        f"INSERT INTO conversations (user_id, title) "
        f"VALUES ((SELECT id FROM users WHERE email = 'ryan.mitchell@cowboys-analytics.com'), '{convo_title_5}');"
    )

    # --- 7. CHAT MESSAGES ---
    sql_lines.extend(["", "-- ========================================", "-- 7. CHAT MESSAGES", "-- ========================================", ""])
    
    # Messages for Conversation 1 (Stock Market Data)
    convo_subquery_1 = f"(SELECT id FROM conversations WHERE title = '{convo_title_1}' LIMIT 1)"
    msgs_1 = [
        {"role": "user", "content": "I need historical stock price data for the S&P 500 going back to 2010 for backtesting trading strategies.", "tool": None},
        {"role": "assistant", "content": "I found several datasets that match your criteria. The 'Global Stock Market Data' from MarketPulse offers comprehensive equity prices with 15-minute delayed real-time feeds and historical data back to 2010.", "tool": {"name": "search_datasets_semantic", "args": {"query": "stock market S&P 500 historical data"}}},
        {"role": "user", "content": "Perfect! Is the data adjusted for stock splits and dividends?", "tool": None},
        {"role": "assistant", "content": "Yes, MarketPulse provides both raw and adjusted prices. The adjusted prices account for stock splits, dividends, and other corporate actions. Would you like to inquire about pricing?", "tool": None}
    ]
    for m in msgs_1:
        tool_json = f"'{json.dumps(m['tool'])}'::jsonb" if m['tool'] else "NULL"
        content_escaped = m['content'].replace("'", "''")
        sql_lines.append(
            f"INSERT INTO chat_messages (conversation_id, role, content, tool_call) "
            f"VALUES ({convo_subquery_1}, '{m['role']}', '{content_escaped}', {tool_json});"
        )
    
    # Messages for Conversation 2 (Clinical Trial Data)
    convo_subquery_2 = f"(SELECT id FROM conversations WHERE title = '{convo_title_2}' LIMIT 1)"
    msgs_2 = [
        {"role": "user", "content": "I am researching oncology clinical trials for a Phase 3 drug study. Do you have trial outcome data?", "tool": None},
        {"role": "assistant", "content": "Yes! ClinicalData Intelligence offers comprehensive trial data including the 'Clinical Trial Outcomes and Efficacy' dataset covering 500,000+ trials across all therapeutic areas and phases.", "tool": {"name": "search_datasets_semantic", "args": {"query": "oncology clinical trials Phase 3"}}},
        {"role": "user", "content": "Great! Does it include patient demographics and adverse event data?", "tool": None}
    ]
    for m in msgs_2:
        tool_json = f"'{json.dumps(m['tool'])}'::jsonb" if m['tool'] else "NULL"
        content_escaped = m['content'].replace("'", "''")
        sql_lines.append(
            f"INSERT INTO chat_messages (conversation_id, role, content, tool_call) "
            f"VALUES ({convo_subquery_2}, '{m['role']}', '{content_escaped}', {tool_json});"
        )
    
    # Messages for Conversation 3 (E-commerce Analytics)
    convo_subquery_3 = f"(SELECT id FROM conversations WHERE title = '{convo_title_3}' LIMIT 1)"
    msgs_3 = [
        {"role": "user", "content": "Looking for e-commerce conversion funnel data to benchmark our cart abandonment rates.", "tool": None},
        {"role": "assistant", "content": "EcomAnalytics Pro has exactly what you need! Their 'Shopping Cart Abandonment Analysis' dataset includes cart-level data, abandonment stages, and recovery metrics from 10,000+ online retailers.", "tool": {"name": "search_datasets_semantic", "args": {"query": "e-commerce cart abandonment conversion"}}},
    ]
    for m in msgs_3:
        tool_json = f"'{json.dumps(m['tool'])}'::jsonb" if m['tool'] else "NULL"
        content_escaped = m['content'].replace("'", "''")
        sql_lines.append(
            f"INSERT INTO chat_messages (conversation_id, role, content, tool_call) "
            f"VALUES ({convo_subquery_3}, '{m['role']}', '{content_escaped}', {tool_json});"
        )
    
    # Messages for Conversation 4 (Cloud Infrastructure Metrics)
    convo_subquery_4 = f"(SELECT id FROM conversations WHERE title = '{convo_title_4}' LIMIT 1)"
    msgs_4 = [
        {"role": "user", "content": "We need to optimize our multi-cloud costs across AWS, Azure, and GCP.", "tool": None},
        {"role": "assistant", "content": "CloudMetrics Analytics provides comprehensive cloud cost data. Their 'Cloud Cost and Billing Analytics' dataset offers detailed cost breakdowns and optimization recommendations.", "tool": {"name": "search_datasets_semantic", "args": {"query": "cloud cost optimization AWS Azure GCP"}}},
    ]
    for m in msgs_4:
        tool_json = f"'{json.dumps(m['tool'])}'::jsonb" if m['tool'] else "NULL"
        content_escaped = m['content'].replace("'", "''")
        sql_lines.append(
            f"INSERT INTO chat_messages (conversation_id, role, content, tool_call) "
            f"VALUES ({convo_subquery_4}, '{m['role']}', '{content_escaped}', {tool_json});"
        )
    
    # Messages for Conversation 5 (Player Performance Analytics)
    convo_subquery_5 = f"(SELECT id FROM conversations WHERE title = '{convo_title_5}' LIMIT 1)"
    msgs_5 = [
        {"role": "user", "content": "Looking for player performance data to improve our scouting and game strategy.", "tool": None},
        {"role": "assistant", "content": "SportStats Global has excellent data! Their 'Player Statistics' dataset includes points, assists, rebounds by game with advanced metrics.", "tool": {"name": "search_datasets_semantic", "args": {"query": "player performance statistics"}}},
    ]
    for m in msgs_5:
        tool_json = f"'{json.dumps(m['tool'])}'::jsonb" if m['tool'] else "NULL"
        content_escaped = m['content'].replace("'", "''")
        sql_lines.append(
            f"INSERT INTO chat_messages (conversation_id, role, content, tool_call) "
            f"VALUES ({convo_subquery_5}, '{m['role']}', '{content_escaped}', {tool_json});"
        )

    # --- 8. INQUIRIES ---
    sql_lines.extend(["", "-- ========================================", "-- 8. INQUIRIES (Negotiations)", "-- ========================================", ""])

    # Inquiry 1: SUBMITTED (Waiting for Vendor AI) - Finance domain
    buyer1_state = {
        "summary": "Requesting S&P 500 historical data with adjusted prices for quantitative trading research.",
        "questions": [
            {"id": "q1", "text": "Does the data include pre-market and after-hours trading?", "status": "open"},
            {"id": "q2", "text": "What is the pricing for a 1-year subscription with API access?", "status": "open"}
        ],
        "constraints": {"budget": "under $10,000 annually", "start_date": "ASAP"}
    }
    buyer1_inquiry_json = json.dumps(buyer1_state).replace("'", "''")
    sql_lines.append(
        f"INSERT INTO inquiries (buyer_id, vendor_id, dataset_id, conversation_id, buyer_inquiry, status) "
        f"VALUES ("
        f"(SELECT id FROM buyers WHERE user_id = (SELECT id FROM users WHERE email = 'olivia.zhang@quanthedge.com')), "
        f"(SELECT id FROM vendors WHERE user_id = (SELECT id FROM users WHERE email = 'data@marketpulse.io')), "
        f"(SELECT id FROM datasets WHERE title = 'Global Stock Market Data and Equity Prices' LIMIT 1), "
        f"{convo_subquery_1}, "
        f"'{buyer1_inquiry_json}'::jsonb, "
        f"'submitted');"
    )

    # Inquiry 2: PENDING REVIEW (Vendor AI Drafted, Human needs to check) - Healthcare domain
    buyer2_state = {
        "summary": "Need oncology trial data with patient demographics for Phase 3 drug efficacy analysis.",
        "questions": [
            {"id": "q1", "text": "Is this data HIPAA compliant and fully anonymized?", "status": "open"},
            {"id": "q2", "text": "Can I get data filtered by specific therapeutic areas?", "status": "open"}
        ],
        "constraints": {"required_compliance": "HIPAA", "therapeutic_area": "Oncology"}
    }
    vendor2_response = {
        "internal_notes": "High confidence on HIPAA compliance. All data fully anonymized per vendor policy.",
        "answers": [
            {"q_ref": "q1", "text": "Yes, all clinical trial data is fully anonymized and HIPAA-compliant. We maintain SOC 2 Type II certification.", "confidence": "high"},
            {"q_ref": "q2", "text": "Absolutely! You can filter by therapeutic area, trial phase, enrollment size, and outcome measures.", "confidence": "high"}
        ],
        "required_human_input": ["verify_pricing_tier", "confirm_data_access_timeline"]
    }
    buyer2_inquiry_json = json.dumps(buyer2_state).replace("'", "''")
    vendor2_response_json = json.dumps(vendor2_response).replace("'", "''")
    sql_lines.append(
        f"INSERT INTO inquiries (buyer_id, vendor_id, dataset_id, conversation_id, buyer_inquiry, vendor_response, status) "
        f"VALUES ("
        f"(SELECT id FROM buyers WHERE user_id = (SELECT id FROM users WHERE email = 'mia.santos@roche-analytics.ch')), "
        f"(SELECT id FROM vendors WHERE user_id = (SELECT id FROM users WHERE email = 'info@clinicaldata.io')), "
        f"(SELECT id FROM datasets WHERE title = 'Clinical Trial Outcomes and Efficacy Data' LIMIT 1), "
        f"{convo_subquery_2}, "
        f"'{buyer2_inquiry_json}'::jsonb, "
        f"'{vendor2_response_json}'::jsonb, "
        f"'pending_review');"
    )
    
    # Inquiry 3: RESPONDED (Done) - Retail domain
    buyer3_state = {
        "summary": "Looking for cart abandonment benchmarks and recovery best practices.",
        "questions": [
            {"id": "q1", "text": "What is the average cart abandonment rate in your dataset?", "status": "answered"},
            {"id": "q2", "text": "Do you offer volume discounts for multiple team members?", "status": "answered"}
        ]
    }
    vendor3_response = {
        "answers": [
            {"q_ref": "q1", "text": "The average cart abandonment rate across our 10,000+ retailers is 68-72%, varying by industry vertical.", "confidence": "high"},
            {"q_ref": "q2", "text": "Yes! We offer 20% discount for 5+ seats and 30% for 10+ seats. Enterprise plans available for larger organizations.", "confidence": "high"}
        ],
        "pricing_offered": "$499/month per seat, discounts apply"
    }
    buyer3_inquiry_json = json.dumps(buyer3_state).replace("'", "''")
    vendor3_response_json = json.dumps(vendor3_response).replace("'", "''")
    sql_lines.append(
        f"INSERT INTO inquiries (buyer_id, vendor_id, dataset_id, conversation_id, buyer_inquiry, vendor_response, status) "
        f"VALUES ("
        f"(SELECT id FROM buyers WHERE user_id = (SELECT id FROM users WHERE email = 'jack.bennett@amazon-retail.com')), "
        f"(SELECT id FROM vendors WHERE user_id = (SELECT id FROM users WHERE email = 'sales@ecomanalytics.io')), "
        f"(SELECT id FROM datasets WHERE title = 'Shopping Cart Abandonment Analysis' LIMIT 1), "
        f"{convo_subquery_3}, "
        f"'{buyer3_inquiry_json}'::jsonb, "
        f"'{vendor3_response_json}'::jsonb, "
        f"'responded');"
    )
    
    # Inquiry 4: SUBMITTED - Technology domain
    buyer4_state = {
        "summary": "Need cloud cost optimization data for multi-cloud environment (AWS, Azure, GCP).",
        "questions": [
            {"id": "q1", "text": "Does your data include reserved instance and savings plan recommendations?", "status": "open"},
            {"id": "q2", "text": "Can I get real-time alerts on cost anomalies?", "status": "open"}
        ],
        "constraints": {"cloud_providers": ["AWS", "Azure", "GCP"], "budget": "flexible"}
    }
    buyer4_inquiry_json = json.dumps(buyer4_state).replace("'", "''")
    sql_lines.append(
        f"INSERT INTO inquiries (buyer_id, vendor_id, dataset_id, conversation_id, buyer_inquiry, status) "
        f"VALUES ("
        f"(SELECT id FROM buyers WHERE user_id = (SELECT id FROM users WHERE email = 'lily.ross@google-cloud.com')), "
        f"(SELECT id FROM vendors WHERE user_id = (SELECT id FROM users WHERE email = 'data@cloudmetrics.io')), "
        f"(SELECT id FROM datasets WHERE title = 'Cloud Cost and Billing Analytics' LIMIT 1), "
        f"{convo_subquery_4}, "
        f"'{buyer4_inquiry_json}'::jsonb, "
        f"'submitted');"
    )
    
    # Inquiry 5: PENDING REVIEW - Sports domain
    buyer5_state = {
        "summary": "Looking for player performance data to optimize team roster and game strategy.",
        "questions": [
            {"id": "q1", "text": "Do you have player tracking data with GPS coordinates?", "status": "open"},
            {"id": "q2", "text": "Is the data available for college sports as well?", "status": "open"}
        ]
    }
    vendor5_response = {
        "internal_notes": "Player tracking data requires additional licensing. College data available separately.",
        "answers": [
            {"q_ref": "q1", "text": "Yes! Our 'Professional Sports Game Results' dataset includes player tracking data with GPS, speed, and distance metrics.", "confidence": "high"},
            {"q_ref": "q2", "text": "College sports data is available in our separate 'College and Amateur Sports' dataset covering NCAA across all divisions.", "confidence": "high"}
        ],
        "required_human_input": ["confirm_licensing_requirements"]
    }
    buyer5_inquiry_json = json.dumps(buyer5_state).replace("'", "''")
    vendor5_response_json = json.dumps(vendor5_response).replace("'", "''")
    sql_lines.append(
        f"INSERT INTO inquiries (buyer_id, vendor_id, dataset_id, conversation_id, buyer_inquiry, vendor_response, status) "
        f"VALUES ("
        f"(SELECT id FROM buyers WHERE user_id = (SELECT id FROM users WHERE email = 'ryan.mitchell@cowboys-analytics.com')), "
        f"(SELECT id FROM vendors WHERE user_id = (SELECT id FROM users WHERE email = 'data@sportstats.pro')), "
        f"(SELECT id FROM datasets WHERE title = 'Professional Sports Game Results' LIMIT 1), "
        f"{convo_subquery_5}, "
        f"'{buyer5_inquiry_json}'::jsonb, "
        f"'{vendor5_response_json}'::jsonb, "
        f"'pending_review');"
    )

    sql_lines.extend(["", "-- ========================================", "-- DONE", "-- ========================================", ""])
    
    return "\n".join(sql_lines)


async def main():
    print("Generating synthetic data SQL script...")
    sql_script = await generate_sql()
    
    output_file = "populate_synthetic_data.sql"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(sql_script)
    
    print(f"\n✓ SQL script generated: {output_file}")
    print("\nUsers created (password: 'password123'):")
    print("  - admin@puddle.com, vendor1@datamart.com, buyer1@research.edu, etc.")
    print("\nInquiries created:")
    print("  1. Buyer1 -> Vendor1 (Status: 'submitted')")
    print("  2. Buyer2 -> Vendor2 (Status: 'pending_review')")
    print("  3. Buyer3 -> Vendor3 (Status: 'responded')")

if __name__ == "__main__":
    asyncio.run(main())