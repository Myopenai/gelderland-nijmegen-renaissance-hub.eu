import sqlite3
import json
from pathlib import Path

# Database path
DB_PATH = Path("db/kean_regions_cms.sqlite")

def get_table_info(conn, table_name):
    """Get column information for a table."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return cursor.fetchall()

def get_table_data_sample(conn, table_name, limit=3):
    """Get a sample of data from a table."""
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (limit,))
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return {"columns": columns, "rows": rows}
    except sqlite3.Error as e:
        return {"error": str(e)}

def analyze_database():
    """Analyze the database structure and content."""
    results = {}
    
    if not DB_PATH.exists():
        return {"error": f"Database file not found at {DB_PATH}"}
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]
        results["tables"] = tables
        
        # Get table structures and sample data
        results["table_info"] = {}
        for table in tables:
            results["table_info"][table] = {
                "structure": get_table_info(conn, table),
                "sample_data": get_table_data_sample(conn, table)
            }
        
        # Get row counts
        results["row_counts"] = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            results["row_counts"][table] = cursor.fetchone()[0]
        
        return results
        
    except sqlite3.Error as e:
        return {"error": f"Database error: {str(e)}"}
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    analysis = analyze_database()
    print(json.dumps(analysis, indent=2, default=str))
