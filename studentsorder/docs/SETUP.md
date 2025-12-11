# Startup Systems - Setup Guide

This guide provides step-by-step instructions for setting up the Startup Systems application.

## Prerequisites

1. **System Requirements**
   - Windows Server 2019/2022 or Ubuntu 20.04 LTS
   - Docker 20.10.0 or later
   - Docker Compose 1.29.0 or later
   - Git 2.30.0 or later
   - Node.js 16.x LTS
   - Python 3.8 or later
   - PowerShell 7.0 or later (Windows) or Bash (Linux)

2. **Network Requirements**
   - Port 80 (HTTP)
   - Port 443 (HTTPS)
   - Port 27017 (MongoDB)
   - Port 6379 (Redis)
   - Port 1883 (MQTT)
   - Port 3000 (Web Interface)
   - Port 5000 (API)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url> startup-systems
cd startup-systems
```

### 2. Run the Setup Script

Windows:
```powershell
.\scripts\setup\install-prerequisites.ps1
```

Linux:
```bash
chmod +x ./scripts/setup/install-prerequisites.sh
./scripts/setup/install-prerequisites.sh
```

### 3. Configure Environment

1. Copy the example environment file:
   ```bash
   copy config\.env.example config\.env
   ```

2. Edit the `.env` file with your configuration:
   ```bash
   notepad config\.env
   ```

### 4. Initialize the Database

```bash
docker-compose -f docker\docker-compose.db.yml up -d
.\scripts\setup\init-database.ps1
```

### 5. Start the Application

```bash
docker-compose -f docker\docker-compose.yml up -d
```

### 6. Verify Installation

1. Check the status of all services:
   ```bash
   docker-compose ps
   ```

2. Access the web interface:
   - URL: http://localhost:3000
   - Default credentials: admin / changeme

## Post-Installation

1. **Change Default Credentials**
   - Log in to the web interface
   - Navigate to Settings > Users
   - Change the default admin password

2. **Configure Backups**
   - Set up database backups:
     ```bash
     .\scripts\maintenance\setup-backup.ps1
     ```

3. **Enable Monitoring**
   - Access Grafana at http://localhost:3001
   - Default credentials: admin / admin
   - Configure data sources and dashboards

## Next Steps

- [Configure Security Settings](SECURITY.md)
- [Set Up Monitoring](docs/MONITORING.md)
- [Backup and Recovery](docs/BACKUP.md)
