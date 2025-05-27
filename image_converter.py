import os
import datetime
from pdf2image import convert_from_path
from PIL import Image

def convert_pdf_to_jpg(pdf_path, entity_name=None, transaction_type=None):
    """
    Convert a PDF file to JPG image and save it in a date-based folder
    
    Args:
        pdf_path (str): Path to the PDF file
        entity_name (str, optional): Name of the person/entity to include in filename
        transaction_type (str, optional): Type of transaction (Income/Expense)
        
    Returns:
        str: Path to the JPG image
    """
    # Get current date for folder name
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Create folder name based on transaction type and date
    folder_prefix = "income" if transaction_type and transaction_type.lower() == "income" else "expense"
    folder_name = f"{folder_prefix}_{today}"
    
    # Create full folder path
    folder_path = os.path.join("output", folder_name)
    
    # Create the folder if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)
    
    # Extract base filename without extension and path
    base_filename = os.path.basename(pdf_path).replace('.pdf', '')
    
    # Create output filename with entity name if provided
    if entity_name:
        # Clean entity name for filename (remove invalid characters)
        clean_name = ''.join(c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in entity_name)
        # Replace spaces with underscores
        clean_name = clean_name.replace(' ', '_')
        # Create new filename with invoice number and entity name
        jpg_filename = f"{base_filename}_{clean_name}.jpg"
    else:
        jpg_filename = f"{base_filename}.jpg"
    
    # Full path to the jpg file
    jpg_path = os.path.join(folder_path, jpg_filename)
    
    # Convert PDF to image
    images = convert_from_path(pdf_path, dpi=300)
    
    # Save the first page as a JPG
    if images:
        images[0].save(jpg_path, 'JPEG', quality=95)
        return jpg_path
    
    return None