import os
import shutil

def save_file(path, filename):
    """
    Save a file to the specified path
    
    Args:
        path (str): The full path where to save the file
        filename (str): The original filename
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Make sure the directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # If the file already exists in the root directory, move it to the output directory
        if os.path.exists(filename):
            shutil.move(filename, path)
        
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False
