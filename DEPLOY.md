# Deployment / Operator Guide

This document describes how to deploy the Attendance Management app on a single host (Linux/macOS). It assumes you have SSH and ability to install system packages.

1. Prepare host

- Install Python 3.11
- Install a production-ready ASGI server (uvicorn or daphne) and a process manager (systemd, supervisord, or pm2)

2. Clone repository and create virtualenv

```bash
git clone <repo_url> attendance_management
cd attendance_management
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Configuration

Create a `.env` file in the project root (copy from `env.example`) and fill in required values:

- SECRET_KEY: 32+ bytes for JWT
- AGE_ENCRYPTION_KEY: Fernet key (32 url-safe base64 bytes). Generate with:
  ```bash
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```
- DATABASE_URL: e.g. `sqlite:///./attendance.db` or `postgresql+asyncpg://user:pass@host/dbname`

4. Database migrations

If using SQLite or Postgres, run Alembic migrations:

```bash
alembic upgrade head
```

5. Run application

For development:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

For production, run with a process manager. Example `systemd` unit:

```ini
[Unit]
Description=Attendance Management
After=network.target

[Service]
User=appuser
WorkingDirectory=/srv/attendance_management
ExecStart=/srv/attendance_management/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

6. Optional: Reverse proxy and TLS

Run behind Nginx with TLS and proxy to the local ASGI server for TLS termination.

7. Monitoring and logs

Ensure stdout/stderr captured by the process manager and add log rotation.

8. Backups

If you use SQLite, periodically copy the `attendance.db`. For Postgres, use pg_dump.

9. Security

- Keep `SECRET_KEY` and `AGE_ENCRYPTION_KEY` secret and not checked into git.
- Limit access via firewall to trusted IPs or localhost.
