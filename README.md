# Attendance Management System

A secure, single-host attendance management system built with FastAPI and SQLite.

## Features

- Student management with encrypted age storage
- Attendance tracking with duplicate prevention
- User authentication with device limiting (2 devices per user)
- Report generation (CSV, XLSX)
- Secure by default: localhost-only binding with optional IP whitelisting

## For Non-Technical Users

If you're not familiar with command line or development tools, follow these simple steps:

### Prerequisites
- Make sure Python 3.11 is installed on your Mac
- Download or clone this project to your computer

### First Time Setup

1. **Open Terminal** (you can find it in Applications → Utilities)

2. **Navigate to the project folder**:
   ```bash
   cd /path/to/attendance_management
   ```
   (Replace `/path/to/attendance_management` with where you saved this project)

3. **Set up the environment** (one-time setup):
   ```bash
   # Create a virtual environment
   python3.11 -m venv .venv
   
   # Activate it
   source .venv/bin/activate
   
   # Install required packages
   pip install -r requirements.txt
   
   # Create configuration file
   cp env.example .env
   
   # Set up the database
   export PYTHONPATH=$(pwd)
   export DATABASE_URL=sqlite+aiosqlite:///./attendance.db
   alembic upgrade head
   
   # Create your admin account
   python scripts/create_user.py
   ```
   Follow the prompts to create your username and password.

### Running the Application

#### Easy Way (Double-Click)

Simply double-click these files in Finder:
- **Start Server.command** - Starts the server and opens your browser
- **Stop Server.command** - Safely stops the server

That's it! No Terminal needed for daily use.

#### Alternative Way (Terminal)

If you prefer using Terminal:

**To start the server:**
```bash
./start.sh
```

**To stop the server:**
```bash
./stop.sh
```

### Troubleshooting

- **First time**: macOS may ask "Are you sure you want to open it?" - click "Open"
- **Permission denied**: Right-click the .command file → "Open" (this bypasses security for trusted files)
- **Browser doesn't open**: Manually visit `http://127.0.0.1:8000/auth/login`
- **Create more users**: Double-click "Start Server.command" first, then:
  ```bash
  cd /path/to/attendance_management
  source .venv/bin/activate
  python scripts/create_user.py
  ```

---

## For Developers

### Requirements

- Python 3.11+
- Poetry for dependency management
- macOS (for firewall configuration examples)

## Quick Start

1. Clone this repository
2. Install dependencies:
   ```bash
   poetry install
   ```

3. Generate encryption keys and create `.env` file:
   ```bash
   # Generate a secret key for JWT signing
   openssl rand -hex 32
   
   # Generate an encryption key for age encryption
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   
   # Copy example env file and fill in the keys
   cp env.example .env
   ```

4. Initialize the database and create admin user:
   ```bash
   poetry run python scripts/init_db.py
   ```

5. Start the development server:
   ```bash
   poetry run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

### Run locally (without Poetry)

If you prefer a plain venv instead of Poetry, this project works with Python 3.11 and a virtual environment. From the project root:

```bash
# create and activate a venv (macOS / Linux)
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# copy example env and generate an encryption key (if you don't have one yet)
cp env.example .env || true
python - <<'PY'
from cryptography.fernet import Fernet
print('AGE_ENCRYPTION_KEY=' + Fernet.generate_key().decode())
PY

# run alembic migrations to create the DB used by the app
export PYTHONPATH=$(pwd)
export DATABASE_URL=sqlite+aiosqlite:///./attendance.db
alembic upgrade head

# start the dev server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Create a local user (for login)

The project does not expose a registration endpoint by default. To create a user for local testing, run the provided script:

```bash
source .venv/bin/activate
python scripts/create_user.py
# follow the prompts to enter username/email/password
```

Alternatively, you can run direct SQL against the `attendance.db` file, but the script above handles password hashing correctly.

## Security Configuration

### macOS Firewall Configuration

To restrict access to only localhost and specific IPs:

1. Create a firewall rule file (e.g., `attendance-fw.conf`):
   ```
   # Block all incoming traffic to the app port
   block in proto tcp to any port 8000
   
   # Allow localhost
   pass in proto tcp from 127.0.0.1 to 127.0.0.1 port 8000
   
   # Allow specific IPs (replace with your mobile device IPs)
   pass in proto tcp from 192.168.1.100 to any port 8000
   pass in proto tcp from 192.168.1.101 to any port 8000
   ```

2. Load the rules:
   ```bash
   sudo pfctl -f attendance-fw.conf
   ```

3. Enable the firewall if not already enabled:
   ```bash
   sudo pfctl -e
   ```

### Running behind Nginx with TLS

For added security, you can run the application behind Nginx with TLS:

1. Install mkcert and create local certificates:
   ```bash
   brew install mkcert
   mkcert -install
   mkcert localhost 127.0.0.1
   ```

2. Create Nginx configuration (example for local development):
   ```nginx
   server {
       listen 443 ssl;
       server_name localhost;
       
       ssl_certificate /path/to/localhost.pem;
       ssl_certificate_key /path/to/localhost-key.pem;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Device Management

The system limits each user to 2 concurrent devices. Users can view and manage their active sessions in the Sessions page. When the limit is reached, users must revoke an existing session before logging in from a new device.

## Testing
Run tests locally (recommended via a Python 3.11 venv):

```bash
# create and activate a venv (macOS / Linux)
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# run tests (loads .env.test when TESTING=true)
TESTING=true python -m pytest -q
```

The test-runner uses an in-memory SQLite database and the `.env.test` file in the project root.

## License

MIT