require('dotenv').config();
const fs = require('fs');
const path = require('path');
const express = require('express');
const helmet = require('helmet');

const app = express();
const portEnv = parseInt(process.env.PORT, 10);
const startPort = Number.isFinite(portEnv) ? portEnv : 3000;
const maxPort = 3100;

// Serve static files from absolute path so behaviour is consistent
const staticPath = path.join(__dirname, '..', 'public');
app.use(express.static(staticPath));
console.log('Serving static files from:', staticPath);

// Security headers: stricter in production, relaxed in dev to allow debugging
if (process.env.NODE_ENV === 'production') {
  app.use(helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'", 'https:'],
        styleSrc: ["'self'", 'https:', "'unsafe-inline'"],
        connectSrc: ["'self'", 'ws:', 'wss:'],
        imgSrc: ["'self'", 'data:', 'https:']
      }
    }
  }));
} else {
  // In development we disable CSP to avoid blocking DevTools and local debug endpoints
  app.use(helmet({ contentSecurityPolicy: false }));
}

app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Serve downloads manifest
app.get('/api/downloads', (req, res) => {
  try {
    const manifestPath = path.join(__dirname, '../public/downloads/downloads.json');
    if (fs.existsSync(manifestPath)) {
      const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
      res.json({ status: 'OK', downloads: manifest });
    } else {
      res.json({ status: 'OK', downloads: [] });
    }
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Serve download files with path traversal protection
app.get('/downloads/:filename', (req, res) => {
  try {
    const filename = req.params.filename;
    // Security: prevent path traversal
    if (filename.includes('..') || filename.includes('/') || filename.includes('\\')) {
      return res.status(400).json({ error: 'Invalid filename' });
    }
    const filepath = path.join(__dirname, '../public/downloads', filename);
    if (!fs.existsSync(filepath)) {
      return res.status(404).json({ error: 'File not found' });
    }
    res.download(filepath);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

function listenOn(p) {
  return new Promise((resolve, reject) => {
    const s = app.listen(p, () => resolve(s));
    s.on('error', reject);
  });
}

(async () => {
  try {
    // Ensure /public/downloads exists
    const downloadsDir = path.join(__dirname, '../public/downloads');
    if (!fs.existsSync(downloadsDir)) {
      fs.mkdirSync(downloadsDir, { recursive: true });
      console.log(`Created downloads directory: ${downloadsDir}`);
    }

    let server = null;
    let chosenPort = null;

    for (let p = startPort; p <= maxPort; p++) {
      try {
        server = await listenOn(p);
        chosenPort = server.address().port;
        break;
      } catch (err) {
        if (err && err.code === 'EADDRINUSE') continue;
        throw err;
      }
    }

    if (!chosenPort) {
      server = await listenOn(0);
      chosenPort = server.address().port;
    }

    const url = `http://localhost:${chosenPort}`;
    console.log(`Server running at ${url}`);

    // Used by start-server.bat to open the correct port
    try {
      fs.writeFileSync('server_url.txt', url);
    } catch (_) {
      // ignore
    }
  } catch (err) {
    console.error('Failed to start server:', err);
    process.exit(1);
  }
})();
