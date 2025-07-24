import pyttsx3
import pathlib
from typing import Union, Optional
import sys
import re

def install_package(package_name: str, module_name: Optional[str] = None):
    """
    Helper function to install and import missing packages.
    Handles cases where the pip package name and the importable module name are different.
    """
    import subprocess
    import importlib
    
    # If module_name isn't provided, assume it's the same as the package_name
    if module_name is None:
        module_name = package_name

    try:
        # Try to import the module by its import name
        return importlib.import_module(module_name)
    except ImportError:
        # If it fails, install the package using its pip name
        print(f"Module '{module_name}' not found. Installing '{package_name}'...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        # Return the imported module
        return importlib.import_module(module_name)

def read_pdf(file_path: str) -> str:
    """Read text from PDF files"""
    try:
        PyPDF2 = install_package("PyPDF2")
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def read_docx(file_path: str) -> str:
    """Read text from DOCX files"""
    try:
        # CORRECTED: Specify package name and module name separately
        docx = install_package(package_name="python-docx", module_name="docx")
        doc = docx.Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs if para.text.strip())
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def read_pptx(file_path: str) -> str:
    """Read text from PowerPoint files"""
    try:
        # CORRECTED: Specify package name and module name separately
        pptx = install_package(package_name="python-pptx", module_name="pptx")
        prs = pptx.Presentation(file_path)
        text = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text.append(shape.text)
        return "\n".join(text)
    except Exception as e:
        return f"Error reading PPTX: {str(e)}"

def read_image(file_path: str) -> str:
    """Extract text from images using OCR"""
    try:
        pytesseract = install_package("pytesseract")
        # CORRECTED: Specify package name and module name for Pillow
        PIL = install_package(package_name="Pillow", module_name="PIL")
        img = PIL.Image.open(file_path)
        return pytesseract.image_to_string(img)
    except Exception as e:
        return f"Error reading image: {str(e)}"

def read_epub(file_path: str) -> str:
    """Read text from EPUB eBooks"""
    try:
        ebooklib = install_package("ebooklib")
        from ebooklib import epub
        book = epub.read_epub(file_path)
        items = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
        return "\n".join(item.get_content().decode('utf-8') for item in items)
    except Exception as e:
        return f"Error reading EPUB: {str(e)}"

def read_html(file_path: str) -> str:
    """Extract text from HTML files"""
    try:
        # CORRECTED: Specify package name and module name for BeautifulSoup
        bs4 = install_package(package_name="beautifulsoup4", module_name="bs4")
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = bs4.BeautifulSoup(f.read(), 'html.parser')
            return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        return f"Error reading HTML: {str(e)}"

def read_office(file_path: str) -> str:
    """Read text from various office formats"""
    try:
        textract = install_package("textract")
        return textract.process(file_path).decode('utf-8')
    except Exception as e:
        return f"Error reading office file: {str(e)}"

def read_txt(file_path: str) -> str:
    """Read text from plain text files"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"Error reading TXT: {str(e)}"

def read_srt(file_path: str) -> str:
    """Read dialogue from .srt subtitle files"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Filter out sequence numbers, timestamps, and empty lines
        dialogue_lines = [
            line.strip() for line in lines
            if line.strip() and not line.strip().isdigit() and '-->' not in line
        ]
        return "\n".join(dialogue_lines)
    except Exception as e:
        return f"Error reading SRT: {str(e)}"

def read_file(file_path: str) -> Union[str, None]:
    """Universal file reader with automatic format detection"""
    path = pathlib.Path(file_path)
    if not path.exists():
        return "File not found"
    
    suffix = path.suffix.lower()
    
    # Document formats
    if suffix == '.pdf':
        return read_pdf(file_path)
    elif suffix == '.docx':
        return read_docx(file_path)
    elif suffix == '.pptx':
        return read_pptx(file_path)
    elif suffix in ('.doc', '.xls', '.xlsx', '.odt', '.ods'):
        return read_office(file_path)
    
    # eBook formats
    elif suffix == '.epub':
        return read_epub(file_path)
    
    # Image formats
    elif suffix in ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic'):
        return read_image(file_path)
    
    # Web formats
    elif suffix in ('.html', '.htm'):
        return read_html(file_path)
    
    # Data formats
    elif suffix in ('.csv', '.json', '.xml'):
        return read_txt(file_path)
    
    # Plain text and subtitle formats
    elif suffix in ('.txt', '.md', '.rtf'):
        return read_txt(file_path)
    elif suffix == '.srt': # ADDED: Handle .srt files
        return read_srt(file_path)
    
    else:
        return f"Unsupported file type: {suffix}"

def text_to_speech(text: str, max_chars: int = 20000):
    """Convert text to speech with safety limits"""
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    
    # Split long text into chunks
    print("Preparing to speak...")
    for i in range(0, min(len(text), max_chars), 5000):
        chunk = text[i:i+5000]
        engine.say(chunk)
        engine.runAndWait()
    print("Finished speaking.")

if __name__ == "__main__":
    # Handle drag-and-drop or command line input
    file_path = sys.argv[1] if len(sys.argv) > 1 else input("Enter file path: ").strip('"')
    
    print(f"\nReading: {file_path}")
    text = read_file(file_path)
    
    if text and not text.startswith("Unsupported") and not text.startswith("Error"):
        print(f"\nFirst 500 characters:\n{text[:500]}...\n")
        text_to_speech(text)
    else:
        print(f"\n{text}")
        # Optional: Decide if you want to speak the error message or not
        # text_to_speech(text)