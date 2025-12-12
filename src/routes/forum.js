const express = require('express');
const router = express.Router();
const { db } = require('../server');

// Get all forum topics with optional category filter
router.get('/topics', (req, res) => {
  const { category } = req.query;
  
  let sql = `
    SELECT t.*, u.username as author
    FROM forum_topics t
    LEFT JOIN users u ON t.user_id = u.id
    WHERE 1=1
  `;
  
  const params = [];
  
  if (category) {
    sql += ' AND t.category = ?';
    params.push(category);
  }
  
  sql += ' ORDER BY t.updated_at DESC';
  
  db.all(sql, params, (err, rows) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json(rows);
  });
});

// Get single topic by ID
router.get('/topics/:id', (req, res) => {
  const { id } = req.params;
  
  const sql = `
    SELECT t.*, u.username as author
    FROM forum_topics t
    LEFT JOIN users u ON t.user_id = u.id
    WHERE t.id = ?
  `;
  
  db.get(sql, [id], (err, row) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    if (!row) {
      return res.status(404).json({ error: 'Topic not found' });
    }
    
    // Get replies for this topic
    db.all(
      'SELECT * FROM forum_replies WHERE topic_id = ? ORDER BY created_at',
      [id],
      (err, replies) => {
        if (err) {
          return res.status(500).json({ error: err.message });
        }
        
        res.json({
          ...row,
          replies: replies || []
        });
      }
    );
  });
});

// Create new topic (protected route - requires authentication)
router.post('/topics', (req, res) => {
  const { title, content, category, userId } = req.body;
  
  if (!title || !content || !category || !userId) {
    return res.status(400).json({ error: 'Missing required fields' });
  }
  
  const sql = `
    INSERT INTO forum_topics (title, content, user_id, category)
    VALUES (?, ?, ?, ?)
  `;
  
  db.run(sql, [title, content, userId, category], function(err) {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    
    // Return the newly created topic
    db.get(
      'SELECT t.*, u.username as author FROM forum_topics t LEFT JOIN users u ON t.user_id = u.id WHERE t.id = ?',
      [this.lastID],
      (err, row) => {
        if (err) {
          return res.status(500).json({ error: err.message });
        }
        res.status(201).json(row);
      }
    );
  });
});

// Get available forum categories
router.get('/categories', (req, res) => {
  const sql = `
    SELECT DISTINCT category 
    FROM forum_topics 
    WHERE category IS NOT NULL
    ORDER BY category
  `;
  
  db.all(sql, [], (err, rows) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    
    // Default categories if none exist yet
    const defaultCategories = [
      'General Discussion',
      'Ideas & Proposals',
      'Local Recommendations',
      'Cultural Events',
      'Sustainability'
    ];
    
    const categories = rows.length > 0 
      ? rows.map(row => row.category)
      : defaultCategories;
    
    res.json(categories);
  });
});

module.exports = router;
