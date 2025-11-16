# Synthetic Data Generation for Puddle
### 1. Generate the SQL file

source .venv/bin/activate
python3 extras/generate_synthetic_data.py

This creates `populate_synthetic_data.sql` with bcrypt-hashed passwords.

### 2. Run the SQL script

First run this sql to clean db: database-creation-script.sql
Then run newly generated one: populate_synthetic_data.sql

All users have the same password: `password123`



