# IBM Standard Node.js Application Setup with Auto Port Detection
# Save this as setup.ps1 and run it

# Configuration
$APP_NAME = "kean-platform"
$DEFAULT_PORT = 3000
$MAX_PORT_ATTEMPTS = 10

# Function to find an available port
function Get-AvailablePort {
    param([int]$startPort = $DEFAULT_PORT, [int]$maxAttempts = $MAX_PORT_ATTEMPTS)
    
    for ($port = $startPort; $port -lt ($startPort + $maxAttempts); $port++) {
        try {
            $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
            $listener.Start()
            $listener.Stop()
            return $port
        } catch {
            # Port is in use, try next one
            continue
        }
    }
    throw "Could not find an available port after $maxAttempts attempts"
}

# Create project structure
$directories = @(
    "src",
    "src/controllers",
    "src/middleware",
    "src/models",
    "src/routes",
    "src/utils",
    "public",
    "test/unit",
    "test/integration",
    "logs"
)

Write-Host "📂 Creating directory structure..." -ForegroundColor Cyan
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Initialize npm project
Write-Host "📦 Initializing Node.js project..." -ForegroundColor Cyan
npm init -y | Out-Null

# Install dependencies
Write-Host "🔧 Installing dependencies..." -ForegroundColor Cyan
npm install express helmet cors dotenv winston bcryptjs jsonwebtoken sqlite3 | Out-Null
npm install --save-dev nodemon jest supertest | Out-Null

# Create .env file with auto-detected port
$availablePort = Get-AvailablePort
Write-Host "🔑 Creating .env file with port $availablePort..." -ForegroundColor Cyan
@"
# Server Configuration
PORT=$availablePort
NODE_ENV=development

# Security
JWT_SECRET=$([guid]::NewGuid().ToString())
PASSWORD_SALT_ROUNDS=10

# Logging
LOG_LEVEL=info

# Database
DB_PATH=./data/kean.db
"@ | Out-File -FilePath ".env" -Encoding utf8

# Create basic server.js
Write-Host "💻 Creating server.js with auto-port detection..." -ForegroundColor Cyan
@"
require('dotenv').config();
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const path = require('fs');
const { createServer } = require('http');
const { promisify } = require('util');
const fs = require('fs').promises;
const path = require('path');

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ 
        status: 'UP',
        timestamp: new Date().toISOString(),
        environment: process.env.NODE_ENV,
        port: PORT
    });
});

// Create server with auto-port detection
async function startServer(port = PORT) {
    const server = createServer(app);
    
    // Handle server errors
    server.on('error', (error) => {
        if (error.code === 'EADDRINUSE') {
            console.log(\`Port \${port} is in use, trying next port...\`);
            return startServer(port + 1);
        }
        console.error('Server error:', error);
        process.exit(1);
    });

    // Start listening
    server.listen(port, () => {
        console.log(\`✅ Server is running on http://localhost:\${port}\`);
        console.log(\`📊 Health check: http://localhost:\${port}/health\`);
    });

    // Handle graceful shutdown
    process.on('SIGTERM', () => {
        console.log('SIGTERM received. Shutting down gracefully...');
        server.close(() => {
            console.log('Server closed');
            process.exit(0);
        });
    });
}

// Start the server
startServer(PORT);
"@ | Out-File -FilePath "src/server.js" -Encoding utf8

# Create public/index.html
Write-Host "🌐 Creating public/index.html..." -ForegroundColor Cyan
@"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$APP_NAME</title>
    <style>
        body {
            font-family: 'IBM Plex Sans', Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            line-height: 1.6;
        }
        .status {
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 4px;
            background: #f4f4f4;
        }
        .success { color: #0e6027; background: #e6f6ee; }
        .error { color: #a2191f; background: #fff1f1; }
    </style>
</head>
<body>
    <h1>Welcome to $APP_NAME</h1>
    <div class="status" id="status">Checking server status...</div>
    
    <h2>Available Endpoints</h2>
    <ul id="endpoints"></ul>

    <script>
        async function checkHealth() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                
                const statusEl = document.getElementById('status');
                statusEl.textContent = \`✅ Server is running on port \${data.port} (\${data.environment} environment)\`;
                statusEl.className = 'status success';
                
                // Update endpoints list
                const endpointsEl = document.getElementById('endpoints');
                endpointsEl.innerHTML = \`
                    <li><strong>GET</strong> <code>/health</code> - Health check</li>
                    <li><strong>GET</strong> <code>/api/status</code> - Application status</li>
                \`;
            } catch (error) {
                const statusEl = document.getElementById('status');
                statusEl.textContent = '❌ Could not connect to server. Make sure the server is running.';
                statusEl.className = 'status error';
                console.error('Error:', error);
            }
        }

        // Check status on load and every 5 seconds
        checkHealth();
        setInterval(checkHealth, 5000);
    </script>
</body>
</html>
"@ | Out-File -FilePath "public/index.html" -Encoding utf8

# Update package.json with proper scripts
Write-Host "📝 Updating package.json with IBM standard scripts..." -ForegroundColor Cyan
$packageJson = Get-Content -Path "package.json" -Raw | ConvertFrom-Json
$packageJson.scripts = @{
    "start" = "node src/server.js"
    "dev" = "nodemon src/server.js"
    "test" = "jest --detectOpenHandles --forceExit"
    "test:watch" = "jest --watch"
    "test:coverage" = "jest --coverage"
    "lint" = "eslint . --ext .js"
    "lint:fix" = "eslint . --ext .js --fix"
}
$packageJson | ConvertTo-Json -Depth 10 | Out-File -FilePath "package.json" -Encoding utf8

Write-Host "`n✨ Setup complete! ✨" -ForegroundColor Green
Write-Host "`nTo start the development server:" -ForegroundColor Cyan
Write-Host "  npm run dev" -ForegroundColor Yellow
Write-Host "`nThen open http://localhost:$availablePort in your browser" -ForegroundColor Cyan
Write-Host "`nThe server will automatically find an available port if $availablePort is in use." -ForegroundColor Cyan