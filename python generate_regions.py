import sqlite3
import os
from pathlib import Path

# Database path
DB_PATH = r"D:\busineshuboffline CHATGTP\KEAN\db\kean_regions_cms.sqlite"
OUTPUT_DIR = Path("regions")

def get_region_data():
    """Connect to SQLite database and fetch region data."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get all tables (regions)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall() if not table[0].startswith('sqlite_')]
        
        regions_data = {}
        for table in tables:
            # Get table structure
            cursor.execute(f"PRAGMA table_info({table});")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Get table data
            cursor.execute(f"SELECT * FROM {table};")
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            regions_data[table] = [
                dict(zip(columns, row)) for row in rows
            ]
            
        return regions_data
    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {}
    finally:
        if conn:
            conn.close()

def create_region_template(region_name, region_data):
    """Generate HTML template for a region."""
    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{region_name} - KEAN Platform</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {{
            --primary: #2c3e50;
            --secondary: #e74c3c;
            --light: #ecf0f1;
            --dark: #2c3e50;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--dark);
        }}
        .region-header {{
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                        url('../images/regions/{region_name.lower()}.jpg');
            background-size: cover;
            background-position: center;
            color: white;
            padding: 100px 0;
            margin-bottom: 30px;
        }}
        .region-title {{
            font-size: 3.5rem;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        .info-card {{
            border: none;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            transition: transform 0.3s;
        }}
        .info-card:hover {{
            transform: translateY(-5px);
        }}
        .section-title {{
            color: var(--primary);
            border-bottom: 3px solid var(--secondary);
            display: inline-block;
            padding-bottom: 5px;
            margin-bottom: 20px;
        }}
        .gallery-img {{
            height: 200px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="../index.html">KEAN Platform</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="../index.html">Home</a></li>
                    <li class="nav-item"><a class="nav-link active" href="#">Regions</a></li>
                    <li class="nav-item"><a class="nav-link" href="#">About</a></li>
                    <li class="nav-item"><a class="nav-link" href="#">Contact</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Region Header -->
    <header class="region-header text-center">
        <div class="container">
            <h1 class="region-title">{region_name}</h1>
            <p class="lead">Discover the rich heritage and culture</p>
        </div>
    </header>

    <!-- Main Content -->
    <main class="container my-5">
        <!-- Overview Section -->
        <section class="mb-5">
            <h2 class="section-title">Overview</h2>
            <div class="row">
                <div class="col-lg-8">
                    <p class="lead">{region_data.get('description', 'Explore the beautiful region of ' + region_name)}</p>
                </div>
                <div class="col-lg-4">
                    <div class="card info-card">
                        <div class="card-body">
                            <h5 class="card-title">Quick Facts</h5>
                            <ul class="list-group list-group-flush">
                                {''.join(f'<li class="list-group-item"><strong>{k}:</strong> {v}</li>' 
                                        for k, v in region_data.items() 
                                        if k not in ['description', 'images', 'id'] and v)}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Gallery Section -->
        <section class="mb-5">
            <h2 class="section-title">Gallery</h2>
            <div class="row">
                <!-- Placeholder for images -->
                <div class="col-md-4">
                    <img src="../images/regions/{region_name.lower()}_1.jpg" alt="{region_name} 1" class="img-fluid gallery-img">
                </div>
                <div class="col-md-4">
                    <img src="../images/regions/{region_name.lower()}_2.jpg" alt="{region_name} 2" class="img-fluid gallery-img">
                </div>
                <div class="col-md-4">
                    <img src="../images/regions/{region_name.lower()}_3.jpg" alt="{region_name} 3" class="img-fluid gallery-img">
                </div>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="bg-dark text-white py-4">
        <div class="container text-center">
            <p>&copy; 2025 KEAN Platform. All rights reserved.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
    return template

def generate_region_pages():
    """Generate HTML pages for all regions."""
    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Get data from database
    regions_data = get_region_data()
    
    # Generate a page for each region
    for region_name, data_list in regions_data.items():
        if not data_list:
            continue
            
        # Use the first row of data
        region_data = data_list[0]
        
        # Generate HTML
        html_content = create_region_template(region_name, region_data)
        
        # Write to file
        output_file = OUTPUT_DIR / f"{region_name.lower()}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Generated: {output_file}")

if __name__ == "__main__":
    generate_region_pages()