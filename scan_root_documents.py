import os
import logging
import pytesseract
from PIL import Image, ImageEnhance
import PyPDF2
import docx2txt
import json
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any, Set, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('root_document_scan.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DocumentAnalyzer:
    """Enhanced document analyzer with better filtering and analysis capabilities."""
    
    def __init__(self, base_dir: str, max_reports: int = 5, days_to_keep: int = 7):
        """Initialize the document analyzer.
        
        Args:
            base_dir: Base directory to scan
            max_reports: Maximum number of reports to keep
            days_to_keep: Number of days to keep old reports
        """
        self.base_dir = Path(base_dir).resolve()
        self.results_dir = self.base_dir / "document_analysis"
        self.max_reports = max_reports
        self.days_to_keep = days_to_keep
        
        # Setup results directory
        self.results_dir.mkdir(exist_ok=True)
        
        # Document analysis data
        self.text_data: List[Dict[str, Any]] = []
        self.file_types: Dict[str, int] = defaultdict(int)
        self.faculty_keywords = {
            'business': ['business', 'management', 'economics', 'finance'],
            'technology': ['technology', 'computer', 'engineering', 'it'],
            'arts': ['arts', 'design', 'music', 'humanities'],
            'science': ['science', 'biology', 'chemistry', 'physics']
        }
        
        # Supported file extensions
        self.supported_extensions = {
            # Document formats
            '.pdf', '.docx', '.doc', '.txt', '.rtf', '.odt',
            # Image formats (OCR supported)
            '.jpg', '.jpeg', '.png',
            # Other text formats
            '.md', '.html', '.json'
        }
        
        # Directories to scan (relative to base_dir)
        self.target_dirs = [
            '',  # root directory
            'regions',
            'pages',
            'studentsorder',
            'src'
        ]
        
        # Directories to always skip
        self.skip_dirs = {
            # Version control
            '.git', '.github', '.svn',
            # Python
            '__pycache__', '.pytest_cache', '.mypy_cache',
            # Virtual environments
            '.venv', 'venv', 'env', 'ENV',
            # Node.js
            'node_modules',
            # Build and distribution
            'build', 'dist', 'target', 'out', 'bin',
            # IDEs and editors
            '.idea', '.vscode', '.vs',
            # System
            'logs', 'cache', 'temp', 'tmp',
            # Project specific
            'document_analysis', 'assets', 'pictures', 'images', 'img', 
            'css', 'js', 'fonts', 'bower_components'
        }
    
    def scan_documents(self) -> Dict[str, Any]:
        """Scan and analyze documents in the target directories."""
        logger.info(f"Starting document scan in: {self.base_dir}")
        
        # Process each target directory
        for rel_dir in self.target_dirs:
            target_dir = self.base_dir / rel_dir if rel_dir else self.base_dir
            
            if not target_dir.exists():
                logger.warning(f"Directory not found: {target_dir}")
                continue
                
            # Walk through the directory
            for root, dirs, files in os.walk(target_dir):
                # Skip ignored directories
                dirs[:] = [d for d in dirs if d not in self.skip_dirs]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    # Check if file should be skipped
                    if self._should_skip(file_path):
                        continue
                        
                    try:
                        self._process_file(file_path)
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}")
        
        # Clean up old reports before generating new ones
        self._cleanup_old_reports()
        
        # Generate and save reports
        return self._generate_reports()
    
    def _process_file(self, file_path: Path) -> None:
        """Process a single file and extract text with enhanced analysis."""
        try:
            logger.info(f"Processing: {file_path}")
            
            # Get file info
            file_stat = file_path.stat()
            file_size = file_path.stat().st_size
            file_ext = file_path.suffix.lower()
            
            # Read file content based on type
            text = self._read_file_content(file_path, file_ext)
            if not text:
                return
                
            # Basic text metrics
            word_count = len(text.split())
            char_count = len(text)
            line_count = text.count('\n') + 1
            
            # Analyze content
            faculty_mentions = self._analyze_faculty_content(text)
            
            # Store file info with enhanced metadata
            self.file_types[file_ext] = self.file_types.get(file_ext, 0) + 1
            
            self.text_data.append({
                'path': str(file_path.relative_to(self.base_dir)),
                'size': file_size,
                'words': word_count,
                'chars': char_count,
                'lines': line_count,
                'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                'extension': file_ext,
                'faculty_mentions': faculty_mentions,
                'content_preview': text[:500] + '...' if len(text) > 500 else text
            })
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}", exc_info=True)
    
    def _read_file_content(self, file_path: Path, file_ext: str) -> Optional[str]:
        """Read content from different file types with error handling."""
        try:
            if file_ext == '.pdf':
                return self._read_pdf(file_path)
            elif file_ext in ('.docx', '.doc'):
                return docx2txt.process(str(file_path))
            elif file_ext in ('.jpg', '.jpeg', '.png'):
                return self._read_image(file_path)
            else:  # .txt, .md, .html, .json, etc.
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            return f.read()
                    except Exception as e:
                        logger.warning(f"Could not read {file_path}: {e}")
                        return None
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return None
    
    def _read_pdf(self, file_path: Path) -> str:
        """Read content from PDF files."""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            return ""
    
    def _read_image(self, file_path: Path) -> str:
        """Read content from images using OCR."""
        try:
            # Open image and enhance for better OCR
            image = Image.open(file_path)
            
            # Convert to grayscale if not already
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance image for better OCR results
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2)
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2)
            
            # Use pytesseract to extract text
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error(f"Error processing image {file_path}: {e}")
            return ""
    
    def _generate_reports(self) -> Dict[str, Any]:
        """Generate comprehensive analysis reports with enhanced metrics."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Calculate statistics
        total_size = sum(f['size'] for f in self.text_data)
        total_words = sum(f['words'] for f in self.text_data)
        total_chars = sum(f.get('chars', 0) for f in self.text_data)
        
        # Aggregate faculty mentions
        faculty_mentions = defaultdict(int)
        for doc in self.text_data:
            for faculty, count in doc.get('faculty_mentions', {}).items():
                faculty_mentions[faculty] += count
        
        # Create metadata
        metadata = {
            'generated_at': datetime.now().isoformat(),
            'base_directory': str(self.base_dir),
            'total_documents': len(self.text_data),
            'total_size': total_size,
            'total_words': total_words,
            'total_chars': total_chars,
            'avg_words_per_doc': round(total_words / len(self.text_data), 2) if self.text_data else 0,
            'file_types': dict(sorted(self.file_types.items(), key=lambda x: x[1], reverse=True)),
            'faculty_mentions': dict(sorted(faculty_mentions.items(), key=lambda x: x[1], reverse=True)),
            'analysis_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save JSON report
        json_report = {
            'metadata': metadata,
            'documents': self.text_data
        }
        
        json_path = self.results_dir / f"document_analysis_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2, ensure_ascii=False, default=str)
        
        # Save text report
        txt_path = self.results_dir / f"document_summary_{timestamp}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            self._write_text_report(f, metadata)
        
        logger.info(f"Reports generated: {json_path}, {txt_path}")
        return json_report
    
    def _write_text_report(self, file, metadata: Dict[str, Any]) -> None:
        """Write a comprehensive text version of the report with enhanced formatting."""
        def write_section(title: str, char: str = '=') -> None:
            """Helper to write section headers."""
            file.write(f"\n{char * 80}\n")
            file.write(f"{title.upper()}\n")
            file.write(f"{char * 80}\n\n")
        
        # Header
        file.write("=" * 80 + "\n")
        file.write("ENHANCED DOCUMENT ANALYSIS REPORT\n")
        file.write(f"Generated: {metadata['generated_at']}\n")
        file.write("=" * 80 + "\n")
        
        # Summary
        write_section("SUMMARY")
        file.write(f"Base Directory: {metadata['base_directory']}\n")
        file.write(f"Analysis Time: {metadata['analysis_time']}\n")
        file.write(f"Total Documents: {metadata['total_documents']:,}\n")
        file.write(f"Total Size: {metadata['total_size'] / (1024*1024):.2f} MB\n")
        file.write(f"Total Words: {metadata['total_words']:,}\n")
        file.write(f"Total Characters: {metadata['total_chars']:,}\n")
        file.write(f"Average Words/Document: {metadata['avg_words_per_doc']:,}\n")
        
        # File Type Analysis
        write_section("FILE TYPE ANALYSIS")
        for ext, count in metadata['file_types'].items():
            file.write(f"{ext}: {count} files\n")
        
        # Faculty Analysis
        if any(count > 0 for count in metadata['faculty_mentions'].values()):
            write_section("FACULTY MENTIONS")
            for faculty, count in metadata['faculty_mentions'].items():
                if count > 0:
                    file.write(f"- {faculty.title()}: {count} mentions\n")
        
        # Document Details
        write_section("DOCUMENT DETAILS")
        for doc in sorted(self.text_data, key=lambda x: x['path'].lower()):
            # Skip very small or empty files
            if doc['words'] < 5:
                continue
                
            file.write(f"\n{'=' * 60}\n")
            file.write(f"FILE: {doc['path']}\n")
            file.write(f"{'=' * 60}\n")
            file.write(f"Type: {doc['extension']} | ")
            file.write(f"Size: {doc['size'] / 1024:.1f} KB | ")
            file.write(f"Words: {doc['words']:,} | ")
            file.write(f"Lines: {doc['lines']:,}\n")
            file.write(f"Modified: {doc['modified']}\n")
            
            # Show faculty mentions if any
            faculty_refs = [f"{k.title()}:{v}" for k, v in doc.get('faculty_mentions', {}).items() if v > 0]
            if faculty_refs:
                file.write(f"Faculty References: {', '.join(faculty_refs)}\n")
            
            # Show content preview
            if 'content_preview' in doc and doc['content_preview'].strip():
                preview = ' '.join(doc['content_preview'].split()[:50])
                if len(doc['content_preview'].split()) > 50:
                    preview += '...'
                file.write(f"\nPreview: {preview}\n")
        
        file.write("\n" + "=" * 80 + "\n")
        file.write("END OF REPORT\n")
        file.write("=" * 80 + "\n")
    
    def _cleanup_old_reports(self) -> None:
        """Remove old report files, keeping only the most recent ones."""
        try:
            # Get all report files
            report_files = list(self.results_dir.glob('*_*_*.{txt,json}'))
            
            # Sort by modification time (newest first)
            report_files.sort(key=os.path.getmtime, reverse=True)
            
            # Keep only the most recent reports
            for report_file in report_files[self.max_reports:]:
                try:
                    report_file.unlink()
                    logger.info(f"Removed old report: {report_file}")
                except Exception as e:
                    logger.error(f"Error removing {report_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error during report cleanup: {e}")
    
    def _analyze_faculty_content(self, text: str) -> Dict[str, int]:
        """Analyze text for faculty-related keywords."""
        text_lower = text.lower()
        faculty_counts = {faculty: 0 for faculty in self.faculty_keywords}
        
        for faculty, keywords in self.faculty_keywords.items():
            for keyword in keywords:
                faculty_counts[faculty] += text_lower.count(keyword)
                
        return faculty_counts

    def _should_skip(self, path: Path) -> bool:
        """Determine if a path should be skipped during scanning."""
        # Skip hidden files and directories
        if any(part.startswith('.') for part in path.parts if part != '.'):
            return True
            
        # Skip files in excluded directories
        for part in path.parts:
            if part in self.skip_dirs:
                return True
                
        # Skip unsupported file extensions
        if path.suffix.lower() not in self.supported_extensions:
            return True
            
        return False

def main():
    try:
        # Initialize scanner with the root directory
        analyzer = DocumentAnalyzer(
            base_dir=r'D:\busineshuboffline CHATGTP\KEAN',
            max_reports=5,  # Keep last 5 reports
            days_to_keep=7  # Keep reports up to 7 days old
        )
        
        # Start scanning
        logger.info("Starting document analysis...")
        report = analyzer.scan_documents()
        
        # Print summary
        print("\n=== Document Analysis Complete ===")
        print(f"Total documents processed: {report['metadata']['total_documents']}")
        print(f"File types found: {', '.join(report['metadata']['file_types'].keys())}")
        
        # Print faculty analysis if available
        if 'faculty_mentions' in report['metadata']:
            print("\nFaculty Mentions:")
            for faculty, count in report['metadata']['faculty_mentions'].items():
                if count > 0:
                    print(f"- {faculty.title()}: {count} mentions")
        
        print(f"\nReports saved to: {analyzer.results_dir}")
        
    except Exception as e:
        logger.error(f"Error during document analysis: {e}")
        raise

if __name__ == "__main__":
    main()
