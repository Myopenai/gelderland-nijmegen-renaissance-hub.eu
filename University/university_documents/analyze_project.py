import os
import json
import datetime
import logging
from pathlib import Path
from collections import defaultdict
import hashlib
import pytesseract
from PIL import Image
import PyPDF2
import docx2txt

class ProjectAnalyzer:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.analysis_dir = self.root_dir / "Universitycapital"
        self.analysis_results = {
            "metadata": {
                "analysis_date": datetime.datetime.now().isoformat(),
                "total_files": 0,
                "file_types": defaultdict(int),
                "faculties": defaultdict(dict)
            },
            "code_analysis": {},
            "documentation": {},
            "dependencies": set()
        }
        
        # Supported file extensions
        self.code_extensions = {'.py', '.js', '.java', '.c', '.cpp', '.h', '.hpp', '.go', '.rs', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.sh', '.bat', '.ps1', '.sql'}
        self.doc_extensions = {'.md', '.txt', '.pdf', '.docx', '.xlsx', '.csv'}
        self.image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        
    def analyze(self):
        print(f"Starting analysis of {self.root_dir}...")
        self._walk_directory(self.root_dir)
        self._analyze_dependencies()
        self._generate_reports()
        print("Analysis complete!")
        
    def _walk_directory(self, path):
        for item in path.iterdir():
            try:
                if item.is_file():
                    self._analyze_file(item)
                elif item.is_dir() and item.name not in {'__pycache__', 'node_modules', '.git', '.idea', 'venv', 'Universitycapital'}:
                    self._walk_directory(item)
            except Exception as e:
                print(f"Error analyzing {item}: {str(e)}")
    
    def _analyze_file(self, file_path):
        ext = file_path.suffix.lower()
        rel_path = str(file_path.relative_to(self.root_dir))
        
        # Update metadata
        self.analysis_results["metadata"]["total_files"] += 1
        self.analysis_results["metadata"]["file_types"][ext] += 1
        
        # Analyze based on file type
        if ext in self.code_extensions:
            self._analyze_code_file(file_path, rel_path)
        elif ext in self.doc_extensions:
            self._analyze_document(file_path, rel_path)
    
    def _analyze_code_file(self, file_path, rel_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Basic code analysis
            lines = content.split('\n')
            analysis = {
                "line_count": len(lines),
                "size_kb": os.path.getsize(file_path) / 1024,
                "imports": [line for line in lines if line.strip().startswith(('import ', 'from '))],
                "functions": [line for line in lines if line.strip().startswith(('def ', 'function '))],
                "hash": hashlib.md5(content.encode()).hexdigest()
            }
            
            # Add to results
            faculty = self._get_faculty(rel_path)
            if 'code' not in self.analysis_results["metadata"]["faculties"][faculty]:
                self.analysis_results["metadata"]["faculties"][faculty]['code'] = 0
            self.analysis_results["metadata"]["faculties"][faculty]['code'] += 1
            
            self.analysis_results["code_analysis"][rel_path] = analysis
            
        except Exception as e:
            print(f"Error analyzing code file {file_path}: {str(e)}")
    
    def _analyze_document(self, file_path, rel_path):
        try:
            content = ""
            file_type = file_path.suffix.lower()
            
            # Handle different document types
            if file_type == '.pdf':
                # Extract text from PDF
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    content = "\n".join([page.extract_text() for page in reader.pages])
            elif file_type == '.docx':
                # Extract text from Word documents
                content = docx2txt.process(file_path)
            elif file_type in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                # Extract text from images using OCR
                try:
                    content = pytesseract.image_to_string(Image.open(file_path))
                except Exception as e:
                    print(f"OCR failed for {file_path}: {str(e)}")
            else:
                # Fallback to regular text file reading
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            
            # Store document analysis
            faculty = self._get_faculty(rel_path)
            if 'docs' not in self.analysis_results["metadata"]["faculties"][faculty]:
                self.analysis_results["metadata"]["faculties"][faculty]['docs'] = 0
            self.analysis_results["metadata"]["faculties"][faculty]['docs'] += 1
            
            self.analysis_results["documentation"][rel_path] = {
                "size_kb": os.path.getsize(file_path) / 1024,
                "word_count": len(content.split()),
                "file_type": file_type,
                "content_sample": content[:1000] + ('...' if len(content) > 1000 else ''),
                "hash": hashlib.md5(content.encode()).hexdigest()
            }
            
        except Exception as e:
            print(f"Error analyzing document {file_path}: {str(e)}")
    
    def _get_faculty(self, file_path):
        # Extract faculty from path (modify as needed)
        parts = file_path.split(os.sep)
        if len(parts) > 1:
            return parts[0]
        return "general"
    
    def _analyze_dependencies(self):
        # Analyze Python dependencies
        req_file = self.root_dir / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r') as f:
                self.analysis_results["dependencies"].update(
                    line.split('==')[0].strip() 
                    for line in f 
                    if line.strip() and not line.startswith('#')
                )
        
        # Analyze Node.js dependencies
        package_json = self.root_dir / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = data.get('dependencies', {})
                    deps.update(data.get('devDependencies', {}))
                    self.analysis_results["dependencies"].update(deps.keys())
            except Exception as e:
                print(f"Error parsing package.json: {str(e)}")
    
    def _generate_reports(self):
        try:
            # Create analysis directory if it doesn't exist
            analysis_dir = self.analysis_dir / "analysis"
            analysis_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate timestamp for the report
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save full analysis
            output_file = analysis_dir / f"full_analysis_{timestamp}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                # Convert sets to lists for JSON serialization
                report_data = self.analysis_results.copy()
                report_data['dependencies'] = list(report_data['dependencies'])
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            # Generate and save summary report
            self._generate_summary_report(analysis_dir, timestamp)
            
            logger.info(f"Analysis reports generated successfully in {analysis_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating reports: {str(e)}", exc_info=True)
            return False
        self._generate_summary_report()
    
    def _generate_summary_report(self):
        """Generate a human-readable summary report"""
        summary = {
            'analysis_date': datetime.datetime.now().isoformat(),
            'total_files_analyzed': self.analysis_results['metadata']['total_files'],
            'file_type_distribution': dict(self.analysis_results['metadata']['file_types']),
            'faculty_breakdown': {
                faculty: dict(counts) 
                for faculty, counts in self.analysis_results['metadata']['faculties'].items()
            },
            'total_code_files': len(self.analysis_results['code_analysis']),
            'total_documents': len(self.analysis_results['documentation'])
        }
        
        summary_file = self.analysis_dir / "analysis" / "summary_report.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Generate summary
        summary = {
            "analysis_date": self.analysis_results["metadata"]["analysis_date"],
            "total_files": self.analysis_results["metadata"]["total_files"],
            "file_type_summary": dict(self.analysis_results["metadata"]["file_types"]),
            "faculties_summary": {
                faculty: {
                    "code_files": data.get('code', 0),
                    "documents": data.get('docs', 0),
                    "images": data.get('images', 0)
                }
                for faculty, data in self.analysis_results["metadata"]["faculties"].items()
            },
            "total_dependencies": len(self.analysis_results["dependencies"])
        }
        
        with open(self.analysis_dir / "analysis" / "summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Analysis reports generated in {self.analysis_dir / 'analysis'}")

def setup_logging():
    """Configure logging for the analysis script"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'analysis.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

if __name__ == "__main__":
    logger = setup_logging()
    
    try:
        logger.info("Starting project analysis...")
        analyzer = ProjectAnalyzer(r"D:\busineshuboffline CHATGTP\KEAN")
        analyzer.analyze()
        logger.info("Analysis completed successfully")
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        sys.exit(1)

# Add this method to your ProjectAnalyzer class
def _generate_summary_report(self, output_dir, timestamp):
    """Generate a summary report of the analysis"""
    try:
        summary = {
            "report_date": datetime.now(pytz.UTC).isoformat(),
            "total_files_analyzed": self.analysis_results["metadata"]["total_files"],
            "file_type_distribution": dict(self.analysis_results["metadata"]["file_types"]),
            "code_analysis": {
                "total_files": len(self.analysis_results["code_analysis"]),
                "total_lines": sum(
                    f.get("line_count", 0) 
                    for f in self.analysis_results["code_analysis"].values()
                ),
                "languages": {
                    ext: count 
                    for ext, count in self.analysis_results["metadata"]["file_types"].items()
                    if ext in ['.py', '.js', '.java', '.c', '.cpp', '.go', '.rs', '.ts', '.jsx', '.tsx']
                }
            },
            "documentation": {
                "total_files": len(self.analysis_results["documentation"]),
                "total_words": sum(
                    doc.get("word_count", 0)
                    for doc in self.analysis_results["documentation"].values()
                )
            },
            "dependencies": {
                "total": len(self.analysis_results["dependencies"]),
                "sample": list(self.analysis_results["dependencies"])[:10]  # First 10 deps
            },
            "faculty_breakdown": {
                faculty: {
                    "code_files": data.get("code", 0),
                    "documents": data.get("docs", 0),
                    "images": data.get("images", 0)
                }
                for faculty, data in self.analysis_results["metadata"]["faculties"].items()
            }
        }
        
        # Save summary report
        summary_file = output_dir / f"summary_report_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        # Generate human-readable text report
        text_report = output_dir / f"summary_report_{timestamp}.txt"
        with open(text_report, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("PROJECT ANALYSIS SUMMARY REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Report generated on: {summary['report_date']}\n\n")
            
            f.write("OVERVIEW\n")
            f.write("--------\n")
            f.write(f"Total files analyzed: {summary['total_files_analyzed']}\n")
            f.write(f"Code files: {summary['code_analysis']['total_files']}\n")
            f.write(f"Documentation files: {summary['documentation']['total_files']}\n")
            f.write(f"Total dependencies found: {summary['dependencies']['total']}\n\n")
            
            f.write("\nFILE TYPE DISTRIBUTION\n")
            f.write("---------------------\n")
            for ext, count in summary['file_type_distribution'].items():
                f.write(f"{ext or 'No extension'}: {count}\n")
            
            f.write("\nFACULTY BREAKDOWN\n")
            f.write("----------------\n")
            for faculty, data in summary['faculty_breakdown'].items():
                f.write(f"\nFaculty: {faculty or 'General'}\n")
                for key, value in data.items():
                    f.write(f"  {key.replace('_', ' ').title()}: {value}\n")
            
            if summary['dependencies']['total'] > 0:
                f.write("\nTOP 10 DEPENDENCIES\n")
                f.write("------------------\n")
                for dep in summary['dependencies']['sample']:
                    f.write(f"- {dep}\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("END OF REPORT\n")
        
        self.logger.info(f"Summary report generated: {summary_file}")
        self.logger.info(f"Text report generated: {text_report}")
        return True
        
    except Exception as e:
        self.logger.error(f"Error generating summary report: {str(e)}", exc_info=True)
        return False
