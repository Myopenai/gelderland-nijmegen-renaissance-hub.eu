import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
from datetime import datetime
import os

# Database configuration
DB_PATH = Path("db/kean_regions_cms.sqlite")
IMAGES_DIR = Path("public/images/regions")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

class DatabaseEnhancer:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def get_tables(self) -> List[str]:
        """Get list of all tables in the database."""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        return [row[0] for row in self.cursor.fetchall()]

    def get_table_columns(self, table_name: str) -> List[Dict]:
        """Get column information for a table."""
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        return [dict(row) for row in self.cursor.fetchall()]

    def get_table_data(self, table_name: str, limit: int = 5) -> List[Dict]:
        """Get sample data from a table."""
        self.cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (limit,))
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

    def analyze_database(self) -> Dict[str, Any]:
        """Analyze the database structure and content."""
        analysis = {
            "tables": {},
            "row_counts": {}
        }
        
        tables = self.get_tables()
        for table in tables:
            analysis["tables"][table] = {
                "columns": self.get_table_columns(table),
                "sample_data": self.get_table_data(table, 3)
            }
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            analysis["row_counts"][table] = self.cursor.fetchone()[0]
        
        return analysis

    def enhance_schema(self):
        """Enhance the database schema with additional tables and columns."""
        # Add new tables for enhanced functionality
        self.cursor.executescript("""
        -- Table for storing detailed region information
        CREATE TABLE IF NOT EXISTS region_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region_id INTEGER NOT NULL,
            region_type TEXT NOT NULL,  -- 'area' or 'community'
            description TEXT,
            history TEXT,
            geography TEXT,
            population INTEGER,
            area_km2 REAL,
            languages TEXT,  -- JSON array of languages
            timezone TEXT,
            coordinates TEXT,  -- JSON with lat/lng
            website_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (region_id) REFERENCES areas(id) ON DELETE CASCADE,
            UNIQUE(region_id, region_type)
        );

        -- Table for points of interest
        CREATE TABLE IF NOT EXISTS points_of_interest (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region_id INTEGER NOT NULL,
            region_type TEXT NOT NULL,  -- 'area' or 'community'
            name TEXT NOT NULL,
            type TEXT NOT NULL,  -- e.g., 'landmark', 'museum', 'park', 'restaurant'
            description TEXT,
            address TEXT,
            coordinates TEXT,  -- JSON with lat/lng
            website_url TEXT,
            phone TEXT,
            email TEXT,
            opening_hours TEXT,  -- JSON object
            entry_fee TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (region_id) REFERENCES areas(id) ON DELETE CASCADE
        );

        -- Table for events
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region_id INTEGER NOT NULL,
            region_type TEXT NOT NULL,  -- 'area' or 'community'
            title TEXT NOT NULL,
            description TEXT,
            start_datetime TIMESTAMP NOT NULL,
            end_datetime TIMESTAMP,
            location TEXT,
            coordinates TEXT,  -- JSON with lat/lng
            website_url TEXT,
            ticket_url TEXT,
            price_range TEXT,
            is_featured BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (region_id) REFERENCES areas(id) ON DELETE CASCADE
        );

        -- Table for images
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,  -- 'region', 'poi', 'event', etc.
            entity_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            alt_text TEXT,
            caption TEXT,
            is_primary BOOLEAN DEFAULT 0,
            width INTEGER,
            height INTEGER,
            size_bytes INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (entity_id) REFERENCES region_details(id) ON DELETE CASCADE
        );

        -- Add indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_region_details_region ON region_details(region_id, region_type);
        CREATE INDEX IF NOT EXISTS idx_poi_region ON points_of_interest(region_id, region_type);
        CREATE INDEX IF NOT EXISTS idx_events_region ON events(region_id, region_type);
        CREATE INDEX IF NOT EXISTS idx_events_dates ON events(start_datetime, end_datetime);
        CREATE INDEX IF NOT EXISTS idx_images_entity ON images(entity_type, entity_id);
        """)
        
        # Commit the changes
        self.conn.commit()
        print("Database schema enhanced successfully!")

    def populate_region_data(self):
        """Populate the database with detailed information about the KEAN region."""
        # This is a placeholder for the actual implementation
        # In a real-world scenario, you would fetch this data from reliable sources
        # and populate the database accordingly
        print("Populating region data...")
        
        # Example: Add detailed information for the KEAN area
        self.cursor.execute("""
        INSERT OR REPLACE INTO region_details 
        (region_id, region_type, description, history, geography, population, area_km2, 
         languages, timezone, coordinates, website_url, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ""
