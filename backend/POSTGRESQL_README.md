# PostgreSQL Setup Guide for Voice of TN

## Quick Setup (Recommended)

1. **Run the automated setup script:**
   ```bash
   cd backend
   python setup_postgres.py
   ```

2. **Follow the prompts** to enter your PostgreSQL credentials

3. **Start the backend:**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

## Manual Setup

### Step 1: Install PostgreSQL

**Windows:**
- Download from: https://www.postgresql.org/download/windows/
- Install with default settings
- **Important:** Remember the password you set during installation

**Linux/Ubuntu:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

### Step 2: Create Database

**Method 1: Using pgAdmin (GUI)**
1. Open pgAdmin
2. Connect to your PostgreSQL server
3. Right-click "Databases" → Create → Database
4. Name: `voiceoftn`
5. Owner: `postgres` (or your username)

**Method 2: Using Command Line**
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE voiceoftn;

# Create user (optional)
CREATE USER voiceoftn_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE voiceoftn TO voiceoftn_user;

# Exit
\q
```

### Step 3: Configure Environment

Edit `backend/.env` file with your actual credentials:

```env
# Replace with your actual PostgreSQL credentials
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/voiceoftn

# Examples:
# DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/voiceoftn
# DATABASE_URL=postgresql://voiceoftn_user:mypassword@localhost:5432/voiceoftn
```

### Step 4: Test Connection

```bash
cd backend
python -c "from app.main import *; print('✅ PostgreSQL connection successful!')"
```

### Step 5: Initialize Database

```bash
python init_postgres_db.py
```

## Troubleshooting

### Connection Issues:
- **"password authentication failed"**: Check your password in `.env` file
- **"database doesn't exist"**: Create the database first
- **"connection refused"**: Make sure PostgreSQL service is running

### Permission Issues:
- Use the correct username/password
- Make sure your user has CREATE privileges
- Try connecting as `postgres` user

### Port Issues:
- Default PostgreSQL port is 5432
- Make sure no other service is using this port

### Service Not Running:
**Windows:**
- Open Services → Find "postgresql" → Start
- Or: `net start postgresql`

**Linux:**
```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```

## Default Admin Credentials

After successful setup:
- **Email:** admin@voiceoftn.com
- **Password:** admin123

## Environment Variables

Make sure your `.env` file contains:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/voiceoftn
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Testing the Setup

1. **Test database connection:**
   ```bash
   python -c "from app.database import engine; print('✅ DB connected')"
   ```

2. **Test full application:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

3. **Check API docs:**
   - Open: http://localhost:8001/docs
   - Test the endpoints

## Production Considerations

- Change the default SECRET_KEY
- Use environment-specific database URLs
- Set up database backups
- Configure connection pooling
- Use SSL connections in production