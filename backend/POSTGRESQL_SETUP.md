# PostgreSQL Setup Instructions for Voice of TN

## Step 1: Install PostgreSQL
1. **Download:** Go to https://www.postgresql.org/download/windows/ (page opened)
2. **Install:** Run the installer with default settings
3. **Remember:** The password you set for the `postgres` user during installation

## Step 2: Verify Installation
Open Command Prompt and run:
```bash
psql --version
```
You should see PostgreSQL version information.

## Step 3: Run Setup Script
```bash
cd c:\Voice_of_TN\backend
python setup_postgres.py
```

## Step 4: Enter Your Credentials
The script will ask for:
- **Username:** Usually `postgres` (default)
- **Password:** The password you set during installation
- **Database name:** `voiceoftn` (default)

## Step 5: Start the Backend
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## Troubleshooting

### If PostgreSQL Service is Not Running:
```bash
# Start PostgreSQL service
net start postgresql

# Or check status
sc query postgresql
```

### If Connection Fails:
- Make sure PostgreSQL is running on port 5432
- Verify your username and password
- Try connecting manually: `psql -U postgres -d postgres`

### If Database Creation Fails:
- Make sure your user has CREATE DATABASE privileges
- Try: `psql -U postgres -c "ALTER USER postgres CREATEDB;"`

## Default Admin Credentials
After setup:
- **Email:** admin@voiceoftn.com
- **Password:** admin123

## Test the Application
1. **Register:** http://localhost:3000/frentend/register.html
2. **Login:** http://localhost:3000/frentend/login.html
3. **File Complaint:** Select department and submit
4. **Admin Dashboard:** admin@voiceoftn.com / admin123