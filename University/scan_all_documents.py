import os
import logging
import pytesseract
from PIL import Image, ImageEnhance
import PyPDF2
import docx2txt
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('document_scan.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DocumentScanner:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.results_dir = self.base_dir / "document_analysis"
        self.results_dir.mkdir(exist_ok=True)
        self.faculty_data = defaultdict(dict)
        self.text_data = []
        self.supported_extensions = {
            # Document formats
            '.pdf', '.docx', '.doc', '.txt', '.rtf', '.odt',
            # Image formats
            '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif',
            # Spreadsheet formats
            '.xlsx', '.xls', '.ods',
            # Presentation formats
            '.pptx', '.ppt', '.odp'
        }
    
    def scan_documents(self):
        """Scan all documents in the base directory and subdirectories"""
        logger.info(f"Starting document scan in: {self.base_dir}")
        
        # Walk through all directories and files
        for root, _, files in os.walk(self.base_dir):
            # Skip certain directories
            if any(skip_dir in root for skip_dir in ['venv', '__pycache__', '.git', 'node_modules']):
                continue
                
            for file in files:
                file_path = Path(root) / file
                
                # Skip files in the results directory
                if str(file_path).startswith(str(self.results_dir)):
                    continue
                    
                # Process supported file types
                if file_path.suffix.lower() in self.supported_extensions:
                    try:
                        logger.info(f"Processing: {file_path}")
                        text = self._extract_text(file_path)
                        if text:
                            self._analyze_document(text, file_path)
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {str(e)}")
        
        # Generate reports
        return self._generate_reports()
    
    def _extract_text(self, file_path):
        """Extract text from different file types"""
        try:
            ext = file_path.suffix.lower()
            
            # Handle PDF files
            if ext == '.pdf':
                return self._extract_from_pdf(file_path)
                
            # Handle Word documents
            elif ext in ['.docx', '.doc', '.odt', '.rtf']:
                return self._extract_from_docx(file_path)
                
            # Handle text files
            elif ext == '.txt':
                return self._extract_from_txt(file_path)
                
            # Handle images
            elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
                return self._extract_from_image(file_path)
                
            # Handle spreadsheets
            elif ext in ['.xlsx', '.xls', '.ods']:
                return self._extract_from_spreadsheet(file_path)
                
            # Handle presentations
            elif ext in ['.pptx', '.ppt', '.odp']:
                return self._extract_from_presentation(file_path)
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return ""
    
    def _extract_from_pdf(self, file_path):
        """Extract text from PDF files"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            return ""
    
    def _extract_from_docx(self, file_path):
        """Extract text from Word documents"""
        try:
            return docx2txt.process(file_path)
        except Exception as e:
            logger.error(f"Error processing DOCX {file_path}: {str(e)}")
            return ""
    
    def _extract_from_txt(self, file_path):
        """Extract text from plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Error reading TXT {file_path}: {str(e)}")
            return ""
    
    def _extract_from_image(self, file_path):
        """Extract text from images using OCR"""
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
            logger.error(f"Error processing image {file_path}: {str(e)}")
            return ""
    
    def _extract_from_spreadsheet(self, file_path):
        """Extract text from spreadsheet files (simplified)"""
        try:
            # For now, just return basic info about the spreadsheet
            # In a production environment, you would use openpyxl or similar to extract data
            return f"[Spreadsheet] {file_path.name} - Content extraction not fully implemented"
        except Exception as e:
            logger.error(f"Error processing spreadsheet {file_path}: {str(e)}")
            return ""
    
    def _extract_from_presentation(self, file_path):
        """Extract text from presentation files (simplified)"""
        try:
            # For now, just return basic info about the presentation
            # In a production environment, you would use python-pptx or similar to extract data
            return f"[Presentation] {file_path.name} - Content extraction not fully implemented"
        except Exception as e:
            logger.error(f"Error processing presentation {file_path}: {str(e)}")
            return ""
    
    def _analyze_document(self, text, file_path):
        """Analyze the extracted text and categorize by faculty"""
        if not text:
            return
            
        # Detect faculty from path or content
        faculty = self._detect_faculty(text, file_path)
        
        # Store document information
        doc_info = {
            'file': str(file_path.relative_to(self.base_dir)),
            'faculty': faculty,
            'size_kb': os.path.getsize(file_path) / 1024,
            'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
            'word_count': len(text.split()),
            'char_count': len(text)
        }
        
        self.text_data.append(doc_info)
        
        # Update faculty data
        if faculty not in self.faculty_data:
            self.faculty_data[faculty] = {
                'documents': [],
                'total_size_kb': 0,
                'total_word_count': 0,
                'file_types': defaultdict(int)
            }
        
        self.faculty_data[faculty]['documents'].append(doc_info['file'])
        self.faculty_data[faculty]['total_size_kb'] += doc_info['size_kb']
        self.faculty_data[faculty]['total_word_count'] += doc_info['word_count']
        self.faculty_data[faculty]['file_types'][file_path.suffix.lower()] += 1
    
    def _detect_faculty(self, text, file_path):
        """Detect faculty from file path or content"""
        path_str = str(file_path).lower()
        text_lower = text.lower()
        
        # Faculty keywords mapping
        faculty_keywords = {
            'informatik': ['informatik', 'computer science', 'cs', 'it', 'software', 'programmierung', 'algorithm'],
            'wirtschaft': ['wirtschaft', 'business', 'bwl', 'vwl', 'betriebswirt', 'volkswirt', 'management', 'marketing'],
            'ingenieur': ['ingenieur', 'engineering', 'maschinenbau', 'elektrotechnik', 'mechanical', 'electrical'],
            'design': ['design', 'gestaltung', 'grafik', 'typografie', 'illustration', 'fotografie'],
            'gesundheit': ['gesundheit', 'medizin', 'gesundheitswesen', 'pflege', 'medizintechnik', 'pharmazie'],
            'sozial': ['sozial', 'sozialarbeit', 'pädagogik', 'erziehung', 'bildung', 'lehramt', 'bildungswissenschaft'],
            'recht': ['recht', 'jura', 'gesetz', 'jurist', 'verwaltung', 'steuer', 'wirtschaftsrecht'],
            'sprache': ['sprache', 'linguistik', 'übersetzung', 'dolmetschen', 'germanistik', 'anglistik']
        }
        
        # Check file path for faculty indicators
        for faculty, keywords in faculty_keywords.items():
            if any(keyword in path_str for keyword in keywords):
                return faculty
        
        # Check text content if not found in path
        for faculty, keywords in faculty_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return faculty
        
        # Try to detect from directory structure
        path_parts = path_str.replace('\\', '/').split('/')
        for part in path_parts:
            part_lower = part.lower()
            for faculty, keywords in faculty_keywords.items():
                if any(keyword in part_lower for keyword in keywords):
                    return faculty
        
        return 'Allgemein'
    
    def _generate_reports(self):
        """Generate analysis reports"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prepare report data
        report = {
            'metadata': {
                'scan_date': datetime.now().isoformat(),
                'base_directory': str(self.base_dir),
                'total_documents': len(self.text_data),
                'total_faculties': len(self.faculty_data),
                'total_word_count': sum(doc['word_count'] for doc in self.text_data),
                'total_size_mb': round(sum(doc['size_kb'] for doc in self.text_data) / 1024, 2)
            },
            'faculties': {}
        }
        
        # Add faculty data to report
        for faculty, data in self.faculty_data.items():
            report['faculties'][faculty] = {
                'document_count': len(data['documents']),
                'total_size_mb': round(data['total_size_kb'] / 1024, 2),
                'total_word_count': data['total_word_count'],
                'file_types': dict(data['file_types']),
                'documents': data['documents']
            }
        
        # Save full data as JSON
        full_report_path = self.results_dir / f'full_analysis_{timestamp}.json'
        with open(full_report_path, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': report['metadata'],
                'faculties': report['faculties'],
                'documents': self.text_data
            }, f, ensure_ascii=False, indent=2)
        
        # Generate human-readable report
        self._generate_human_readable_report(report, timestamp)
        
        logger.info(f"Document scan complete. Reports saved to {self.results_dir}")
        return report
    
    def _generate_human_readable_report(self, report, timestamp):
        """Generate a human-readable text report"""
        report_path = self.results_dir / f'summary_report_{timestamp}.txt'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("DOCUMENT SCAN AND ANALYSIS REPORT\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Summary
            f.write("SUMMARY\n")
            f.write("-" * 80 + "\n")
            f.write(f"Base Directory: {report['metadata']['base_directory']}\n")
            f.write(f"Total Documents: {report['metadata']['total_documents']:,}\n")
            f.write(f"Total Word Count: {report['metadata']['total_word_count']:,}\n")
            f.write(f"Total Size: {report['metadata']['total_size_mb']:.2f} MB\n")
            f.write(f"Faculties Identified: {len(report['faculties'])}\n\n")
            
            # Faculty Summary
            f.write("FACULTY SUMMARY\n")
            f.write("-" * 80 + "\n")
            for faculty, data in sorted(report['faculties'].items(), key=lambda x: x[1]['document_count'], reverse=True):
                f.write(f"\n{faculty.upper()}:\n")
                f.write(f"- Documents: {data['document_count']:,}\n")
                f.write(f"- Word Count: {data['total_word_count']:,}\n")
                f.write(f"- Size: {data['total_size_mb']:.2f} MB\n")
                f.write("- File Types: " + ", ".join([f"{ext} ({count})" for ext, count in data['file_types'].items()]) + "\n")
            
            # Document Details
            f.write("\n" + "=" * 80 + "\n")
            f.write("DETAILED DOCUMENT LISTING\n")
            f.write("=" * 80 + "\n\n")
            
            for faculty, data in sorted(report['faculties'].items()):
                f.write(f"FACULTY: {faculty.upper()}\n")
                f.write("-" * 40 + "\n")
                
                for doc in sorted(data['documents']):
                    doc_info = next((d for d in self.text_data if d['file'] == doc), None)
                    if doc_info:
                        f.write(f"- {doc} ({doc_info['word_count']:,} words, {doc_info['size_kb']:.1f} KB, modified: {doc_info['modified'][:10]})\n")
                f.write("\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")

def main():
    # Initialize scanner with the current directory
    scanner = DocumentScanner(Path(__file__).parent)
    
    # Start scanning
    print("Starting document scan...")
    report = scanner.scan_documents()
    
    # Print summary
    print("\nScan Complete!")
    print(f"Total documents processed: {report['metadata']['total_documents']}")
    print(f"Faculties identified: {', '.join(report['faculties'].keys())}")
    print(f"\nReports saved to: {scanner.results_dir}")

if __name__ == "__main__":
    main()
