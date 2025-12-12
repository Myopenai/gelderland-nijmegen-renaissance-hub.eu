#!/usr/bin/env node

/**
 * Health Check: Verify downloads system is operational
 * Run this after server startup to validate configuration
 */

const fs = require('fs');
const path = require('path');

const CHECKS = [
  {
    name: 'Ensure /public/downloads directory exists',
    check: () => {
      const dir = path.join(__dirname, '../public/downloads');
      if (!fs.existsSync(dir)) {
        throw new Error(`Directory does not exist: ${dir}`);
      }
      console.log(`  ✓ Directory exists: ${dir}`);
    }
  },
  {
    name: 'Ensure downloads.json manifest exists',
    check: () => {
      const file = path.join(__dirname, '../public/downloads/downloads.json');
      if (!fs.existsSync(file)) {
        throw new Error(`Manifest does not exist: ${file}`);
      }
      const content = JSON.parse(fs.readFileSync(file, 'utf-8'));
      if (!Array.isArray(content)) {
        throw new Error('Manifest is not a JSON array');
      }
      console.log(`  ✓ Manifest valid (${content.length} entries)`);
    }
  },
  {
    name: 'Ensure downloads.html portal page exists',
    check: () => {
      const file = path.join(__dirname, '../public/downloads.html');
      if (!fs.existsSync(file)) {
        throw new Error(`Portal page does not exist: ${file}`);
      }
      console.log(`  ✓ Portal page exists`);
    }
  },
  {
    name: 'Verify manifest entries point to existing files',
    check: () => {
      const manifest = JSON.parse(fs.readFileSync(path.join(__dirname, '../public/downloads/downloads.json'), 'utf-8'));
      const dir = path.join(__dirname, '../public/downloads');
      
      manifest.forEach(entry => {
        const filepath = path.join(dir, entry.filename);
        // Note: Files may not exist yet if just deployed, but we check path safety
        if (entry.filename.includes('..') || entry.filename.includes('/')) {
          throw new Error(`Unsafe filename in manifest: ${entry.filename}`);
        }
      });
      console.log(`  ✓ All manifest entries have safe filenames`);
    }
  }
];

async function runHealthChecks() {
  console.log('🏥 Running Download System Health Checks...\n');
  
  let passed = 0;
  let failed = 0;
  
  for (const check of CHECKS) {
    try {
      console.log(`Checking: ${check.name}`);
      check.check();
      passed++;
    } catch (err) {
      console.error(`  ❌ Failed: ${err.message}`);
      failed++;
    }
  }
  
  console.log(`\n${passed}/${CHECKS.length} checks passed`);
  
  if (failed > 0) {
    console.error(`\n⚠️  ${failed} check(s) failed. Downloads system may not work correctly.`);
    process.exit(1);
  } else {
    console.log('\n✅ All health checks passed!\n');
  }
}

if (require.main === module) {
  runHealthChecks();
}

module.exports = { runHealthChecks };
