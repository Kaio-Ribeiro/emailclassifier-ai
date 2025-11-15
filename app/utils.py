"""
File processing utilities for Email Classifier AI
"""
import os
import PyPDF2
from werkzeug.utils import secure_filename


def extract_text_from_file(file, filename):
    """
    Extract text content from uploaded file
    
    Args:
        file: Werkzeug FileStorage object
        filename: Original filename
        
    Returns:
        str: Extracted text content
        
    Raises:
        ValueError: If file type is not supported
        Exception: If file processing fails
    """
    file_extension = filename.rsplit('.', 1)[1].lower()
    
    if file_extension == 'txt':
        return extract_text_from_txt(file)
    elif file_extension == 'pdf':
        return extract_text_from_pdf(file)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")


def extract_text_from_txt(file):
    """
    Extract text from .txt file
    
    Args:
        file: Werkzeug FileStorage object
        
    Returns:
        str: Text content
    """
    try:
        # Try UTF-8 first
        content = file.read().decode('utf-8')
        file.seek(0)  # Reset file pointer
        return content.strip()
    except UnicodeDecodeError:
        # Fallback to latin-1 if UTF-8 fails
        file.seek(0)
        content = file.read().decode('latin-1')
        file.seek(0)
        return content.strip()


def extract_text_from_pdf(file):
    """
    Extract text from .pdf file
    
    Args:
        file: Werkzeug FileStorage object
        
    Returns:
        str: Extracted text content
    """
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        file.seek(0)  # Reset file pointer
        return text.strip()
    
    except Exception as e:
        file.seek(0)
        raise Exception(f"Error processing PDF: {str(e)}")


def save_uploaded_file(file, upload_folder):
    """
    Save uploaded file to disk
    
    Args:
        file: Werkzeug FileStorage object
        upload_folder: Directory to save file
        
    Returns:
        str: Path to saved file
    """
    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    
    # Ensure unique filename
    counter = 1
    base, ext = os.path.splitext(file_path)
    while os.path.exists(file_path):
        file_path = f"{base}_{counter}{ext}"
        counter += 1
    
    file.save(file_path)
    return file_path


def validate_file_size(file, max_size_mb=16):
    """
    Validate file size
    
    Args:
        file: Werkzeug FileStorage object
        max_size_mb: Maximum size in MB
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Get file size
    file.seek(0, 2)  # Move to end
    size = file.tell()
    file.seek(0)  # Reset to beginning
    
    max_size_bytes = max_size_mb * 1024 * 1024
    return size <= max_size_bytes


def clean_text(text):
    """
    Clean and normalize text content
    
    Args:
        text: Raw text content
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    lines = [line.strip() for line in text.split('\n')]
    cleaned_lines = [line for line in lines if line]
    
    # Join with single spaces
    cleaned_text = ' '.join(cleaned_lines)
    
    # Remove multiple spaces
    while '  ' in cleaned_text:
        cleaned_text = cleaned_text.replace('  ', ' ')
    
    return cleaned_text.strip()