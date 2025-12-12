const express = require('express');
const router = express.Router();
const { db } = require('../server');

// Get all projects with optional status filter
router.get('/', (req, res) => {
  const { status, region } = req.query;
  
  let sql = `
    SELECT p.*, r.name as region_name, r.slug as region_slug 
    FROM projects p
    LEFT JOIN regions r ON p.region_id = r.id
    WHERE 1=1
  `;
  
  const params = [];
  
  if (status) {
    sql += ' AND p.status = ?';
    params.push(status);
  }
  
  if (region) {
    sql += ' AND r.slug = ?';
    params.push(region);
  }
  
  sql += ' ORDER BY p.updated_at DESC';
  
  db.all(sql, params, (err, rows) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json(rows);
  });
});

// Get project by ID
router.get('/:id', (req, res) => {
  const { id } = req.params;
  
  const sql = `
    SELECT p.*, r.name as region_name, r.slug as region_slug 
    FROM projects p
    LEFT JOIN regions r ON p.region_id = r.id
    WHERE p.id = ?
  `;
  
  db.get(sql, [id], (err, row) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    if (!row) {
      return res.status(404).json({ error: 'Project not found' });
    }
    res.json(row);
  });
});

// Get project status counts
router.get('/status/counts', (req, res) => {
  const sql = `
    SELECT 
      status,
      COUNT(*) as count
    FROM projects
    GROUP BY status
  `;
  
  db.all(sql, [], (err, rows) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    
    // Initialize with all possible statuses
    const statusCounts = {
      planning: 0,
      in_progress: 0,
      compliance: 0,
      completed: 0
    };
    
    // Update with actual counts
    rows.forEach(row => {
      statusCounts[row.status] = row.count;
    });
    
    res.json(statusCounts);
  });
});

module.exports = router;
