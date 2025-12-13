#!/usr/bin/env node
// scripts/crawl-mojibake.js
// Headless crawler using Playwright to detect mojibake patterns (dry-run, read-only)
// Supports: file://, http(s)://, auto-discovers Sitemap.xml, filesystem listing, robots.txt

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const https = require('https');
const http = require('http');

const repoRoot = path.resolve(__dirname, '..');
const publicDir = path.join(repoRoot, 'public');

let startUrl = process.argv[2] || `file://${path.join(publicDir, 'index.html')}`;
const MAX_PAGES = parseInt(process.argv[3] || '200');
const TIMEOUT = 15000; // ms

const mojibakeRegex = /(Ã¤|Ã¶|Ã¼|ÃŸ|Ã„|Ã–|Ãœ|Ãƒ|Â|�|ÃƒÂ|Ã‚)/g;
const entityRegex = /&(?:auml|ouml|uuml|Auml|Ouml|Uuml|szlig);/g;

// HTTP fetch helper (for robots.txt, sitemap.xml discovery)
function httpGet(url) {
  return new Promise((resolve, reject) => {
    const proto = url.startsWith('https') ? https : http;
    proto.get(url, { timeout: 5000 }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

// Parse sitemap.xml to extract URLs
function extractSitemapUrls(xmlContent) {
  const urls = [];
  const urlRegex = /<loc>([^<]+)<\/loc>/g;
  let match;
  while ((match = urlRegex.exec(xmlContent)) !== null) {
    urls.push(match[1]);
  }
  return urls;
}

// Auto-discover sitemaps from robots.txt
async function discoverSitemaps(baseUrl) {
  const urls = [];
  try {
    const baseUri = new URL(baseUrl);
    const robotsUrl = `${baseUri.protocol}//${baseUri.host}/robots.txt`;
    const robots = await httpGet(robotsUrl);
    const sitemapRegex = /Sitemap:\s*([^\s]+)/g;
    let match;
    while ((match = sitemapRegex.exec(robots)) !== null) {
      urls.push(match[1]);
    }
  } catch (err) {
    // robots.txt not found, try default sitemap.xml
    try {
      const baseUri = new URL(baseUrl);
      urls.push(`${baseUri.protocol}//${baseUri.host}/sitemap.xml`);
    } catch (e) {
      // not http(s)
    }
  }
  return urls;
}

// Scan filesystem for .html files (used if file:// protocol)
function scanFilesystemHtml(dir) {
  const urls = [];
  try {
    const files = fs.readdirSync(dir, { recursive: true });
    for (const file of files) {
      if (file.endsWith('.html') || file.endsWith('.htm')) {
        const filePath = path.join(dir, file);
        urls.push(`file://${filePath}`);
      }
    }
  } catch (err) {
    // dir not found
  }
  return urls;
}

(async () => {
  console.log('Starting mojibake crawler (dry-run, read-only)');
  console.log('Start URL:', startUrl);
  console.log('Max pages to scan:', MAX_PAGES);

  const isHttp = startUrl.startsWith('http');
  const isFile = startUrl.startsWith('file');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const toVisit = new Set();
  const visited = new Set();
  const findings = [];

  toVisit.add(startUrl);

  // Auto-discover sitemaps if HTTP(S)
  if (isHttp) {
    console.log('Auto-discovering sitemaps...');
    try {
      const sitemapUrls = await discoverSitemaps(startUrl);
      for (const sitemapUrl of sitemapUrls) {
        console.log(`  Found sitemap: ${sitemapUrl}`);
        try {
          const sitemapContent = await httpGet(sitemapUrl);
          const pageUrls = extractSitemapUrls(sitemapContent);
          pageUrls.forEach(u => toVisit.add(u));
          console.log(`    Extracted ${pageUrls.length} URLs from sitemap`);
        } catch (err) {
          console.warn(`    Could not fetch ${sitemapUrl}: ${err.message}`);
        }
      }
    } catch (err) {
      console.log('  Sitemap discovery skipped or unavailable');
    }
  }

  // Auto-discover HTML files if file://
  if (isFile) {
    console.log('Scanning filesystem for .html files...');
    const htmlUrls = scanFilesystemHtml(publicDir);
    htmlUrls.slice(0, 50).forEach(u => toVisit.add(u)); // limit to 50 to avoid too many
    console.log(`  Found ${htmlUrls.length} HTML files (added first 50 to crawl queue)`);
  }

  while (toVisit.size && visited.size < MAX_PAGES) {
    const next = toVisit.values().next().value;
    toVisit.delete(next);
    if (visited.has(next)) continue;

    try {
      console.log(`[${visited.size + 1}/${MAX_PAGES}] Visiting: ${next}`);
      await page.goto(next, { timeout: TIMEOUT, waitUntil: 'domcontentloaded' }).catch(() => {});
    } catch (err) {
      console.warn(`  ⚠ Could not load: ${err.message}`);
      visited.add(next);
      continue;
    }

    let text = '';
    try {
      text = await page.innerText('body').catch(() => '');
      if (!text) {
        const html = await page.content().catch(() => '');
        text = html.replace(/<[^>]+>/g, ' ');
      }
    } catch (err) {
      // ignore
    }

    const mojiMatches = Array.from((text || '').matchAll(mojibakeRegex)).map(m => m[0]);
    const entityMatches = Array.from((text || '').matchAll(entityRegex)).map(m => m[0]);

    if (mojiMatches.length || entityMatches.length) {
      const snippet = (text || '').slice(0, 200).replace(/\s+/g, ' ').trim();
      findings.push({
        url: next,
        mojibake: [...new Set(mojiMatches)],
        entities: [...new Set(entityMatches)],
        snippet
      });
      console.log(`  ✗ MOJIBAKE FOUND: moji=${[...new Set(mojiMatches)].join(',')} ents=${[...new Set(entityMatches)].join(',')}`);
    } else {
      console.log(`  ✓ OK`);
    }

    // extract links from page (only follow valid links within same origin or file system)
    try {
      const anchors = await page.$$eval('a[href]', els => els.map(a => a.getAttribute('href'))).catch(() => []);
      for (let href of anchors) {
        if (!href) continue;
        if (href.startsWith('#') || href.startsWith('mailto:') || href.startsWith('tel:')) continue;

        let absolute;
        try {
          absolute = new URL(href, page.url()).toString();
        } catch (err) {
          continue;
        }

        // Restrict to same origin (for http(s)) or same root (for file://)
        try {
          const startUri = new URL(startUrl);
          const absUri = new URL(absolute);
          if (startUri.origin === absUri.origin && !visited.has(absolute)) {
            toVisit.add(absolute);
          }
        } catch (e) {
          // for file://, simple check
          if (absolute.startsWith('file://') && !visited.has(absolute)) {
            toVisit.add(absolute);
          }
        }
      }
    } catch (err) {
      // ignore
    }

    visited.add(next);
  }

  await browser.close();

  const report = {
    start: startUrl,
    scanned: visited.size,
    findings,
    timestamp: new Date().toISOString(),
    scanDuration: '(see crawler output for timing)'
  };

  const outPath = path.join(__dirname, 'crawl-mojibake-report.json');
  fs.writeFileSync(outPath, JSON.stringify(report, null, 2), 'utf8');
  console.log('\n═══════════════════════════════════════');
  console.log('Crawl complete.');
  console.log(`Pages scanned: ${visited.size}`);
  console.log(`Issues found: ${findings.length}`);
  console.log(`Report: ${outPath}`);
  console.log('═══════════════════════════════════════');

  if (findings.length > 0) {
    console.log('\nTop findings (sample):');
    for (let f of findings.slice(0, 5)) {
      console.log(`\n- URL: ${f.url}`);
      console.log(`  mojibake patterns: ${f.mojibake.join(', ')}`);
      console.log(`  entities: ${f.entities.join(', ')}`);
      console.log(`  snippet: "${f.snippet}"`);
    }
    console.log(`\nTotal: ${findings.length} pages with issues. See full report: ${outPath}`);
  } else {
    console.log('\n✓ No mojibake patterns detected by crawler.');
  }

  process.exit(findings.length > 0 ? 1 : 0);

})().catch(err => {
  console.error('Fatal error:', err.message);
  process.exit(1);
});
