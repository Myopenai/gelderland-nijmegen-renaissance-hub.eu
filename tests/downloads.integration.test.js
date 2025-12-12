/**
 * Integration Test: Download API & Portal
 * Tests that the download manifest and file serving work correctly
 */

const fs = require('fs');
const path = require('path');

// Mock test (run with Node directly or with Jest)
async function testDownloadAPI() {
  console.log('🧪 Testing Download Endpoints...');
  
  const baseUrl = 'http://localhost:3000';
  
  try {
    // Test 1: /api/downloads endpoint
    console.log('  [TEST 1] GET /api/downloads');
    const res1 = await fetch(`${baseUrl}/api/downloads`);
    if (res1.status !== 200) {
      throw new Error(`Expected 200, got ${res1.status}`);
    }
    const data = await res1.json();
    if (!Array.isArray(data.downloads)) {
      throw new Error('Expected downloads array in response');
    }
    console.log(`    ✓ API returned ${data.downloads.length} downloads`);
    
    // Test 2: Each download entry has required fields
    console.log('  [TEST 2] Validate download metadata');
    data.downloads.forEach((dl, idx) => {
      if (!dl.filename || !dl.name || !dl.version) {
        throw new Error(`Download ${idx} missing required fields`);
      }
    });
    console.log('    ✓ All entries have required metadata');
    
    // Test 3: /downloads/:filename security (path traversal block)
    console.log('  [TEST 3] Security: path traversal protection');
    const res3 = await fetch(`${baseUrl}/downloads/../etc/passwd`);
    if (res3.status === 200) {
      throw new Error('Path traversal not blocked!');
    }
    console.log('    ✓ Path traversal blocked');
    
    // Test 4: Non-existent file returns 404
    console.log('  [TEST 4] Non-existent file handling');
    const res4 = await fetch(`${baseUrl}/downloads/nonexistent-file.zip`);
    if (res4.status !== 404) {
      throw new Error(`Expected 404, got ${res4.status}`);
    }
    console.log('    ✓ Non-existent files return 404');
    
    console.log('\n✅ All tests passed!\n');
    
  } catch (err) {
    console.error(`\n❌ Test failed: ${err.message}\n`);
    process.exit(1);
  }
}

// Run tests
if (require.main === module) {
  testDownloadAPI();
}

module.exports = { testDownloadAPI };
