# KEAN Landscape Planning System

A comprehensive landscape planning system for the KEAN region (Kleve, Emmerich, Arnhem, Nijmegen).

## Project Structure

```
KEAN/
├── src/
│   ├── __init__.py
│   ├── database.py         # Database configuration and session management
│   └── models/
│       ├── __init__.py
│       └── landscape.py    # SQLAlchemy models for the landscape planning system
├── init_db.py             # Script to initialize the database
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Setup Instructions

1. **Prerequisites**
   - Python 3.9+
   - PostgreSQL with PostGIS extension (for production)
   - SQLite (for development, included with Python)

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the database**
   - For development, SQLite is used by default
   - For production, set the `DATABASE_URL` environment variable to your PostgreSQL connection string:
     ```
     postgresql://username:password@localhost:5432/kean_landscape
     ```

5. **Initialize the database**
   ```bash
   python init_db.py
   ```

## Database Schema

The database schema includes the following main entities:

- `AdministrativeArea`: Hierarchical administrative divisions (countries, states, municipalities)
- `Parcel`: Land parcels/cadastral units
- `LandUseCategory`: Categories of land use
- `ProtectedArea`: Protected areas (nature reserves, Natura 2000 sites, etc.)
- `Enterprise`: Businesses and organizations
- `NACECategory`: NACE classification for economic activities
- `Infrastructure`: Transportation and utility infrastructure
- `PlanningDocument`: Spatial planning documents and regulations
- `EnvironmentalData`: Environmental measurements and indicators

## Data Import

To import data into the system, you can use the following approaches:

1. **CSV/Shapefile Import**: Create scripts to parse and import data from common formats
2. **API Integration**: Connect to external data sources via their APIs
3. **Manual Entry**: Use the application interface (when implemented) to enter data manually

## Development

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Document all public functions and classes with docstrings
- Run code formatters and linters before committing:
  ```bash
  black .
  isort .
  flake8
  mypy .
  ```

### Testing

Run tests with:
```bash
pytest
```

## License

This project is proprietary and confidential.
