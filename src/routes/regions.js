const express = require('express');
const router = express.Router();
const { db } = require('../server');

// Get all regions
router.get('/', (req, res) => {
  const sql = 'SELECT * FROM regions ORDER BY name';
  
  db.all(sql, [], (err, rows) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json(rows);
  });
});

// Get single region by slug
router.get('/:slug', (req, res) => {
  const { slug } = req.params;
  const sql = 'SELECT * FROM regions WHERE slug = ?';
  
  db.get(sql, [slug], (err, row) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    if (!row) {
      return res.status(404).json({ error: 'Region not found' });
    }
    res.json(row);
  });
});

// Get projects for a region
router.get('/:regionId/projects', (req, res) => {
  const { regionId } = req.params;
  const { status } = req.query;
  
  let sql = 'SELECT * FROM projects WHERE region_id = ?';
  const params = [regionId];
  
  if (status) {
    sql += ' AND status = ?';
    params.push(status);
  }
  
  sql += ' ORDER BY created_at DESC';
  
  db.all(sql, params, (err, rows) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json(rows);
  });
});

module.exports = router;
