#!/usr/bin/env node
// scripts/crawl-mojibake.js
// Headless crawler using Playwright to detect mojibake patterns (dry-run, read-only)

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const repoRoot = path.resolve(__dirname, '..');
const publicDir = path.join(repoRoot, 'public');

const DEFAULT_START = process.argv[2] || `file://${path.join(publicDir, 'index.html')}`;
const MAX_PAGES = 200;
const TIMEOUT = 15000; // ms

const mojibakeRegex = /(Ã¤|Ã¶|Ã¼|ÃŸ|Ã„|Ã–|Ãœ|Ãƒ|Â|�|ÃƒÂ|Ã‚)/g;
const entityRegex = /&(?:auml|ouml|uuml|Auml|Ouml|Uuml|szlig);/g;

(async () => {
  console.log('Starting mojibake crawler (dry-run)');
  console.log('Root public dir:', publicDir);
  console.log('Start URL:', DEFAULT_START);

  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  const toVisit = new Set();
  const visited = new Set();
  const findings = [];

  toVisit.add(DEFAULT_START);

  while (toVisit.size && visited.size < MAX_PAGES) {
    const next = toVisit.values().next().value;
    toVisit.delete(next);
    if (visited.has(next)) continue;

    try {
      console.log(`Visiting: ${next}`);
      await page.goto(next, { timeout: TIMEOUT, waitUntil: 'networkidle' });
    } catch (err) {
      console.warn(`Could not load ${next}: ${err.message}`);
      visited.add(next);
      continue;
    }

    let text = '';
    try {
      text = await page.innerText('body');
    } catch (err) {
      // fallback to whole page content
      const html = await page.content();
      // strip tags loosely
      text = html.replace(/<[^>]+>/g, ' ');
    }

    const mojiMatches = Array.from(text.matchAll(mojibakeRegex)).map(m => m[0]);
    const entityMatches = Array.from(text.matchAll(entityRegex)).map(m => m[0]);

    if (mojiMatches.length || entityMatches.length) {
      findings.push({
        url: next,
        mojibake: [...new Set(mojiMatches)],
        entities: [...new Set(entityMatches)],
        snippet: text.slice(0, 400).replace(/\s+/g, ' ').trim()
      });
      console.log(`  -> Found mojibake/entity patterns: moji=${[...new Set(mojiMatches)]} entities=${[...new Set(entityMatches)]}`);
    }

    // extract links from page
    try {
      const anchors = await page.$$eval('a[href]', els => els.map(a => a.getAttribute('href')));
      for (let href of anchors) {
        if (!href) continue;
        // normalize relative links
        if (href.startsWith('#')) continue;
        if (href.startsWith('mailto:') || href.startsWith('tel:')) continue;

        let absolute;
        try {
          absolute = new URL(href, page.url()).toString();
        } catch (err) {
          continue;
        }

        // keep file:// and http(s) links, restrict to same origin or file root
        const sameOrigin = (() => {
          try { return new URL(absolute).origin === new URL(DEFAULT_START).origin; } catch(e){ return false }
        })();

        const isFile = absolute.startsWith('file://');
        if (sameOrigin || isFile) {
          if (!visited.has(absolute)) toVisit.add(absolute);
        }
      }
    } catch (err) {
      // ignore
    }

    visited.add(next);
  }

  await browser.close();

  const report = {
    start: DEFAULT_START,
    scanned: visited.size,
    findings,
    timestamp: new Date().toISOString()
  };

  const outPath = path.join(__dirname, 'crawl-mojibake-report.json');
  fs.writeFileSync(outPath, JSON.stringify(report, null, 2), 'utf8');
  console.log('\nCrawl complete. Scanned pages:', visited.size);
  console.log('Findings:', findings.length);
  console.log('Report written to:', outPath);

  if (findings.length > 0) {
    console.log('\nTop findings (sample):');
    for (let f of findings.slice(0, 10)) {
      console.log(`- ${f.url}`);
      console.log(`  mojibake: ${f.mojibake.join(', ')}`);
      console.log(`  entities: ${f.entities.join(', ')}`);
      console.log(`  snippet: ${f.snippet}\n`);
    }
  } else {
    console.log('No mojibake patterns detected by crawler.');
  }

})();
