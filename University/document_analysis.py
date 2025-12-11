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
        logging.FileHandler('document_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DocumentAnalyzer:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.results_dir = self.base_dir / "document_analysis"
        self.results_dir.mkdir(exist_ok=True)
        self.faculty_data = defaultdict(dict)
        self.text_data = []
        
    def process_document(self, file_path):
        """Process a single document based on its file type"""
        try:
            if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
                return self._process_image(file_path)
            elif file_path.suffix.lower() == '.pdf':
                return self._process_pdf(file_path)
            elif file_path.suffix.lower() == '.docx':
                return self._process_docx(file_path)
            elif file_path.suffix.lower() == '.txt':
                return self._process_txt(file_path)
            else:
                logger.warning(f"Unsupported file type: {file_path}")
                return ""
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return ""
    
    def _process_image(self, image_path):
        """Extract text from image using OCR"""
        try:
            # Open image and enhance for better OCR
            image = Image.open(image_path)
            
            # Enhance image for better OCR results
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2)
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2)
            
            # Use pytesseract to extract text
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            return ""
    
    def _process_pdf(self, pdf_path):
        """Extract text from PDF file"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            return ""
    
    def _process_docx(self, docx_path):
        """Extract text from DOCX file"""
        try:
            return docx2txt.process(docx_path)
        except Exception as e:
            logger.error(f"Error processing DOCX {docx_path}: {str(e)}")
            return ""
    
    def _process_txt(self, txt_path):
        """Read text from TXT file"""
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Error reading TXT {txt_path}: {str(e)}")
            return ""
    
    def analyze_text(self, text, file_path):
        """Analyze the extracted text and categorize by faculty"""
        if not text:
            return
            
        # Simple faculty detection (can be enhanced with more sophisticated NLP)
        faculty = self._detect_faculty(text, file_path)
        
        # Store text data
        self.text_data.append({
            'file': str(file_path.relative_to(self.base_dir)),
            'faculty': faculty,
            'text': text,
            'word_count': len(text.split())
        })
        
        # Update faculty data
        if faculty not in self.faculty_data:
            self.faculty_data[faculty] = {
                'documents': [],
                'word_count': 0,
                'topics': set()
            }
        
        self.faculty_data[faculty]['documents'].append(str(file_path.name))
        self.faculty_data[faculty]['word_count'] += len(text.split())
        
        # Simple topic extraction (can be enhanced with NLP)
        topics = self._extract_topics(text)
        self.faculty_data[faculty]['topics'].update(topics)
    
    def _detect_faculty(self, text, file_path):
        """Detect faculty from text or file path"""
        # Check file path for faculty indicators
        path_str = str(file_path).lower()
        faculties = {
            'informatik': 'Informatik',
            'wirtschaft': 'Wirtschaftswissenschaften',
            'ingenieur': 'Ingenieurwissenschaften',
            'design': 'Design',
            'gesundheit': 'Gesundheitswesen',
            'sozial': 'Sozialwesen',
            'recht': 'Rechtswissenschaften',
            'kultur': 'Kulturwissenschaften'
        }
        
        for key, faculty in faculties.items():
            if key in path_str.lower():
                return faculty
        
        # Check text content if not found in path
        text_lower = text.lower()
        for key, faculty in faculties.items():
            if key in text_lower:
                return faculty
        
        return 'Allgemein'
    
    def _extract_topics(self, text):
        """Extract potential topics from text"""
        # Simple keyword matching (can be enhanced with NLP)
        topics = set()
        text_lower = text.lower()
        
        # Common academic topics
        topic_keywords = {
            'ki': 'Künstliche Intelligenz',
            'maschinelles lernen': 'Maschinelles Lernen',
            'data science': 'Data Science',
            'big data': 'Big Data',
            'cloud computing': 'Cloud Computing',
            'cybersicherheit': 'Cybersicherheit',
            'blockchain': 'Blockchain',
            'internet der dinge': 'Internet der Dinge',
            'wirtschaftsinformatik': 'Wirtschaftsinformatik',
            'marketing': 'Marketing',
            'finanzen': 'Finanzen',
            'maschinenbau': 'Maschinenbau',
            'elektrotechnik': 'Elektrotechnik',
            'design thinking': 'Design Thinking',
            'gesundheitsmanagement': 'Gesundheitsmanagement',
            'soziale arbeit': 'Soziale Arbeit',
            'recht': 'Recht',
            'kulturwissenschaft': 'Kulturwissenschaft',
            'medien': 'Medien',
            'kommunikation': 'Kommunikation'
        }
        
        for keyword, topic in topic_keywords.items():
            if keyword in text_lower:
                topics.add(topic)
        
        return topics
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report = {
            'metadata': {
                'report_date': datetime.now().isoformat(),
                'total_documents': sum(len(data['documents']) for data in self.faculty_data.values()),
                'total_faculties': len(self.faculty_data),
                'total_word_count': sum(data['word_count'] for data in self.faculty_data.values())
            },
            'faculties': {}
        }
        
        # Process faculty data
        for faculty, data in self.faculty_data.items():
            report['faculties'][faculty] = {
                'document_count': len(data['documents']),
                'word_count': data['word_count'],
                'documents': data['documents'],
                'topics': list(data['topics'])
            }
        
        # Save full text data
        text_report_path = self.results_dir / f'full_text_data_{timestamp}.json'
        with open(text_report_path, 'w', encoding='utf-8') as f:
            json.dump(self.text_data, f, ensure_ascii=False, indent=2)
        
        # Save analysis report
        report_path = self.results_dir / f'analysis_report_{timestamp}.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # Generate human-readable report
        self._generate_human_readable_report(report, timestamp)
        
        logger.info(f"Analysis complete. Reports saved to {self.results_dir}")
        return report
    
    def _generate_human_readable_report(self, report, timestamp):
        """Generate a human-readable text report"""
        report_path = self.results_dir / f'analysis_report_{timestamp}.txt'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("DOCUMENT ANALYSIS REPORT\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Summary
            f.write("SUMMARY\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total documents analyzed: {report['metadata']['total_documents']}\n")
            f.write(f"Total faculties identified: {report['metadata']['total_faculties']}\n")
            f.write(f"Total word count: {report['metadata']['total_word_count']:,}\n\n")
            
            # Faculty details
            f.write("FACULTY ANALYSIS\n")
            f.write("-" * 80 + "\n")
            
            for faculty, data in report['faculties'].items():
                f.write(f"\nFACULTY: {faculty.upper()}\n")
                f.write(f"Documents: {data['document_count']}\n")
                f.write(f"Word count: {data['word_count']:,}\n")
                
                f.write("\nTopics:\n")
                for topic in data['topics']:
                    f.write(f"- {topic}\n")
                
                f.write("\nDocuments:\n")
                for doc in data['documents']:
                    f.write(f"- {doc}\n")
                
                f.write("\n" + "-" * 40 + "\n")
            
            f.write("\nEND OF REPORT\n")
            f.write("=" * 80 + "\n")
    
    def process_directory(self, directory=None):
        """Process all documents in the specified directory"""
        if directory is None:
            directory = self.base_dir
        else:
            directory = Path(directory)
        
        logger.info(f"Starting document analysis in: {directory}")
        
        # Supported file extensions
        extensions = {'.pdf', '.docx', '.txt', '.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        
        # Walk through directory and process files
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in extensions:
                    logger.info(f"Processing: {file_path}")
                    text = self.process_document(file_path)
                    if text:
                        self.analyze_text(text, file_path)
        
        # Generate and save reports
        return self.generate_report()


def main():
    # Initialize analyzer with the University directory
    analyzer = DocumentAnalyzer(Path(__file__).parent)
    
    # Process all documents and generate reports
    report = analyzer.process_directory()
    
    print(f"\nAnalysis complete!")
    print(f"Total documents processed: {report['metadata']['total_documents']}")
    print(f"Faculties identified: {', '.join(report['faculties'].keys())}")
    print(f"\nReports saved to: {analyzer.results_dir}")


if __name__ == "__main__":
    main()
