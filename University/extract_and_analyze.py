import zipfile
import os
from pathlib import Path
from document_analysis import DocumentAnalyzer

def extract_zip(zip_path, extract_to):
    """Extract zip file to the specified directory"""
    extract_to = Path(extract_to)
    extract_to.mkdir(exist_ok=True)
    
    print(f"Extracting {zip_path} to {extract_to}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extraction complete!")
    return extract_to

def main():
    # Define paths
    base_dir = Path(__file__).parent
    zip_file = base_dir / "university begin.zip"
    extract_dir = base_dir / "university_documents"
    
    # Extract the zip file if it exists
    if zip_file.exists():
        extract_dir = extract_zip(zip_file, extract_dir)
    
    # Initialize and run document analysis
    print("\nStarting document analysis...")
    analyzer = DocumentAnalyzer(extract_dir)
    report = analyzer.process_directory()
    
    print(f"\nAnalysis complete!")
    print(f"Total documents processed: {report['metadata']['total_documents']}")
    print(f"Faculties identified: {', '.join(report['faculties'].keys())}")
    print(f"\nReports saved to: {analyzer.results_dir}")

if __name__ == "__main__":
    main()
