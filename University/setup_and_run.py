import os
import subprocess
from pathlib import Path

def setup_directories():
    base_dir = Path(r"D:\busineshuboffline CHATGTP\KEAN\University\Universitycapital")
    dirs = [
        "analysis",
        "valuations",
        "market_analysis",
        "future_roadmap"
    ]
    
    # Create all directories
    for dir_name in dirs:
        dir_path = base_dir / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")

def run_analysis():
    try:
        # Run the analysis script
        print("Running analysis...")
        subprocess.run(["python", "analyze_project.py"], check=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        # Run the valuation script
        print("Generating valuation report...")
        subprocess.run(["python", "create_valuation.py"], check=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        print("Analysis completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error running analysis: {e}")

if __name__ == "__main__":
    setup_directories()
    run_analysis()
