import json
import os
import datetime

# Path to store the invoice counter
COUNTER_FILE = "data/invoice_counter.json"

def get_next_invoice_number(document_type):
    """
    Get the next invoice or receipt number in sequence
    """
    # Create the data directory if it doesn't exist
    os.makedirs(os.path.dirname(COUNTER_FILE), exist_ok=True)
    
    # Initialize or load the counter file
    if not os.path.exists(COUNTER_FILE):
        counters = {
            "Invoice": 0,
            "Receipt": 0
        }
    else:
        with open(COUNTER_FILE, 'r') as f:
            try:
                counters = json.load(f)
            except json.JSONDecodeError:
                counters = {
                    "Invoice": 0,
                    "Receipt": 0
                }
    
    # Increment the counter for the specified document type
    counters[document_type] += 1
    
    # Save the updated counter
    with open(COUNTER_FILE, 'w') as f:
        json.dump(counters, f)
    
    # Format the invoice number
    prefix = "INV" if document_type == "Invoice" else "REC"
    return f"{prefix}{counters[document_type]:03d}"

def get_current_counter(document_type):
    """
    Get the current counter value without incrementing
    """
    # Create the data directory if it doesn't exist
    os.makedirs(os.path.dirname(COUNTER_FILE), exist_ok=True)
    
    # Initialize or load the counter file
    if not os.path.exists(COUNTER_FILE):
        return 0
    else:
        with open(COUNTER_FILE, 'r') as f:
            try:
                counters = json.load(f)
                return counters.get(document_type, 0)
            except json.JSONDecodeError:
                return 0

def check_invoice_number_exists(number, document_type):
    """
    Check if an invoice number already exists
    
    Args:
        number (int): The numeric part of the invoice number (without prefix)
        document_type (str): "Invoice" or "Receipt"
        
    Returns:
        bool: True if the invoice number exists, False otherwise
    """
    current_counter = get_current_counter(document_type)
    return number <= current_counter

def format_invoice_number(number, document_type):
    """
    Format an invoice number with the appropriate prefix
    
    Args:
        number (int): The numeric part of the invoice number
        document_type (str): "Invoice" or "Receipt"
        
    Returns:
        str: Formatted invoice number (e.g., "INV001")
    """
    prefix = "INV" if document_type == "Invoice" else "REC"
    return f"{prefix}{number:03d}"

def set_custom_invoice_number(number, document_type, force=False):
    """
    Set a custom invoice number for the specified document type
    
    Args:
        number (int): The custom invoice number to set
        document_type (str): "Invoice" or "Receipt"
        force (bool): If True, allow using an existing number
        
    Returns:
        bool: True if successful, False if number already exists and force is False
    """
    # Create the data directory if it doesn't exist
    os.makedirs(os.path.dirname(COUNTER_FILE), exist_ok=True)
    
    # Initialize or load the counter file
    if not os.path.exists(COUNTER_FILE):
        counters = {
            "Invoice": 0,
            "Receipt": 0
        }
    else:
        with open(COUNTER_FILE, 'r') as f:
            try:
                counters = json.load(f)
            except json.JSONDecodeError:
                counters = {
                    "Invoice": 0,
                    "Receipt": 0
                }
    
    # Check if the number already exists and we're not forcing
    if not force and number <= counters.get(document_type, 0):
        return False
    
    # If we're forcing or the number is new, set it (but don't decrease the counter)
    if number > counters.get(document_type, 0):
        counters[document_type] = number
        
        # Save the updated counter
        with open(COUNTER_FILE, 'w') as f:
            json.dump(counters, f)
    
    return True


def force_invoice_number(number, document_type):
    """
    Force using a specific invoice number even if it already exists
    
    Args:
        number (int): The invoice number to force
        document_type (str): "Invoice" or "Receipt"
        
    Returns:
        str: The formatted invoice number
    """
    # Just return the formatted number without updating the counter
    prefix = "INV" if document_type == "Invoice" else "REC"
    return f"{prefix}{number:03d}"

def generate_invoice_text(transaction_type, entity_name, amount, date, description, company_name, currency="GBP"):
    """
    Generate a text representation of the invoice/receipt for messaging
    
    Args:
        transaction_type (str): "Income" or "Expense"
        entity_name (str): Name of the person or entity
        amount (float): Transaction amount
        date (datetime): Transaction date
        description (str): Description of the transaction
        company_name (str): Name of the company
        currency (str, optional): Currency code (GBP or USD). Defaults to "GBP".
    
    Returns:
        str: Text representation of the invoice/receipt
    """
    # Format the date
    date_str = date.strftime("%d %B %Y")
    
    # Set currency symbol
    currency_symbol = "$" if currency == "USD" else "£"
    
    # Create the appropriate text based on transaction type
    if transaction_type == "Income":
        text = f"Received payment of {currency_symbol}{amount:.2f} on {date_str} from {entity_name} for {description}. Thank you for your business. - {company_name}"
    else:  # Expense
        text = f"Paid amount of {currency_symbol}{amount:.2f} on {date_str} to {entity_name} for {description}. Payment made by {company_name}."
    
    return text
