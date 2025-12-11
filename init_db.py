#!/usr/bin/env python3
"""
Initialize the KEAN Landscape Planning database.
This script creates all necessary tables and can be used to populate initial data.
"""
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent))

from src.database import init_db, engine, Base

def main():
    print("Initializing KEAN Landscape Planning Database...")
    
    # Create all tables
    init_db()
    
    print("\nDatabase initialization complete!")
    print(f"Database location: {engine.url}")

if __name__ == "__main__":
    main()
