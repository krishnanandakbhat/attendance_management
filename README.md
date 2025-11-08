# Attendance Management System

A secure, single-host attendance management system built with FastAPI and SQLite.

## Features

- Student management with encrypted age storage
- Attendance tracking with duplicate prevention
- User authentication with device limiting (2 devices per user)
- Report generation (CSV, XLSX)
- Secure by default: localhost-only binding with optional IP whitelisting

## Requirements

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