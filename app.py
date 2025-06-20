import streamlit as st
import datetime
import os
from invoice_generator import (
    generate_invoice_text, 
    get_next_invoice_number,
    get_current_counter,
    check_invoice_number_exists,
    format_invoice_number,
    set_custom_invoice_number,
    force_invoice_number
)
from pdf_generator import generate_pdf
from openai_helper import generate_smart_description
from utils import save_file
from image_converter import convert_pdf_to_jpg

# Initialize session state variables
if 'current_invoice_number' not in st.session_state:
    st.session_state.current_invoice_number = None

if 'document_generated' not in st.session_state:
    st.session_state.document_generated = False

# Add total income/outcome tracking
if 'total_income' not in st.session_state:
    st.session_state.total_income = 0

if 'total_outcome' not in st.session_state:
    st.session_state.total_outcome = 0

if 'generated_data' not in st.session_state:
    st.session_state.generated_data = {
        'document_type': None,
        'invoice_number': None,
        'pdf_path': None,
        'jpg_path': None,
        'currency': 'GBP',
        'pdf_data': None,
        'jpg_data': None,
        'pdf_filename': None,
        'jpg_filename': None,
        'text_version': None,
        'transaction_type': None,
        'amount': 0.0
    }
    
# Initialize counters for income and outcome
if 'total_income' not in st.session_state:
    st.session_state.total_income = 0.0
    
if 'total_outcome' not in st.session_state:
    st.session_state.total_outcome = 0.0

# Page configuration
st.set_page_config(
    page_title="Invoice Receipt Generator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stTitle {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem !important;
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-style: italic;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        text-align: center;
        color: white;
        margin-bottom: 1rem;
    }
    
    .income-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(79, 172, 254, 0.3);
        text-align: center;
        color: white;
        margin-bottom: 1rem;
    }
    
    .expense-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(250, 112, 154, 0.3);
        text-align: center;
        color: white;
        margin-bottom: 1rem;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(255, 107, 107, 0.3);
        text-align: center;
        color: white;
        margin-bottom: 1rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .reset-section {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(168, 237, 234, 0.3);
        margin-bottom: 2rem;
    }
    
    .form-container {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .stSelectbox > div > div {
        border-radius: 10px;
    }
    
    .stNumberInput > div > div {
        border-radius: 10px;
    }
    
    .stTextInput > div > div {
        border-radius: 10px;
    }
    
    .stTextArea > div > div {
        border-radius: 10px;
    }
    
    .stDateInput > div > div {
        border-radius: 10px;
    }
    
    div[data-testid="metric-container"] {
        background: white;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 25px;
        color: white;
        font-weight: 600;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
    }
    
    .separator {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
    }
    
    .stSelectbox label, .stNumberInput label, .stTextInput label, .stTextArea label, .stDateInput label {
        font-weight: 600;
        color: #333;
        font-size: 1rem;
    }
    
    .upload-section {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(252, 182, 159, 0.3);
    }
    
    .success-message {
        background: linear-gradient(135deg, #a8e6cf 0%, #88d8a3 100%);
        padding: 1rem;
        border-radius: 10px;
        color: #2d5a3d;
        font-weight: 600;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Beautiful header section
st.markdown('<div style="text-align: center; margin-bottom: 3rem;">', unsafe_allow_html=True)
st.title("📋 Invoice Receipt Generator")
st.markdown('<p class="subtitle">Generate professional invoices and receipts for your business transactions</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Reset section with beautiful design
st.markdown('<div class="reset-section">', unsafe_allow_html=True)
reset_cols = st.columns([2, 1, 2])
with reset_cols[1]:
    st.markdown("### 🔄 ضبط الترقيم")
    reset_to_number = st.number_input(
        "البدء من الرقم",
        min_value=1,
        value=1,
        step=1,
        key="reset_number_input",
        help="الرقم الذي تريد أن تبدأ منه ترقيم الفواتير"
    )
    
    if st.button("ضبط الترقيم", key="reset_invoice_btn", type="primary"):
        import json
        import os
        
        counter_file = "data/invoice_counter.json"
        os.makedirs(os.path.dirname(counter_file), exist_ok=True)
        
        counters = {
            "Invoice": reset_to_number - 1,
            "Receipt": reset_to_number - 1
        }
        
        with open(counter_file, 'w') as f:
            json.dump(counters, f)
            
        st.success(f"تم إعادة ضبط ترقيم الفواتير للبدء من الرقم {reset_to_number}!")
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Beautiful metrics cards
st.markdown("### 📊 الملخص المالي")
income_expense_cols = st.columns(2)

with income_expense_cols[0]:
    if st.session_state.total_income >= 90000:
        st.markdown(f'''
        <div class="warning-card">
            <h3>⚠️ إجمالي الدخل</h3>
            <h2>£{st.session_state.total_income:.2f}</h2>
            <p>مطلوب تسجيل ضريبة القيمة المضافة!</p>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div class="income-card">
            <h3>💰 إجمالي الدخل</h3>
            <h2>£{st.session_state.total_income:.2f}</h2>
            <p>الدخل الإجمالي المسجل</p>
        </div>
        ''', unsafe_allow_html=True)

with income_expense_cols[1]:
    st.markdown(f'''
    <div class="expense-card">
        <h3>💸 إجمالي المصروفات</h3>
        <h2>£{st.session_state.total_outcome:.2f}</h2>
        <p>المصروفات الإجمالية المسجلة</p>
    </div>
    ''', unsafe_allow_html=True)

# Beautiful separator
st.markdown('<hr class="separator">', unsafe_allow_html=True)

# Create a layout with the invoice number input on the right
header_cols = st.columns([3, 1])

with header_cols[1]:
    # Initialize invoice number input state - only store raw digit input
    if 'raw_invoice_number' not in st.session_state:
        st.session_state.raw_invoice_number = ""
    
    # Initialize force_generate flag if needed
    if 'force_generate_header' not in st.session_state:
        st.session_state.force_generate_header = False
    
    # Add an input for custom invoice number (just enter the number)
    custom_invoice_number = st.text_input(
        "Invoice Number", 
        value=st.session_state.raw_invoice_number,
        key="custom_invoice_number_input",
        placeholder="رقم فقط (مثال: 20)",
        help="أدخل الرقم فقط (مثال: 20 سيتم تنسيقه تلقائيًا إلى INV020) أو اتركه فارغًا للترقيم التلقائي"
    )
    
    # Always allow any number to be used (especially number 1)
    if custom_invoice_number and custom_invoice_number.isdigit():
        custom_number = int(custom_invoice_number)
        formatted_inv_num = format_invoice_number(custom_number, "Invoice")
        
        # Special case for number 1 - always allow it without any warning
        if custom_number == 1:
            st.session_state.force_generate_header = True
            st.session_state.force_number = custom_number
            st.success(f"سيتم استخدام الرقم: {formatted_inv_num}")
        # For other numbers that might exist
        elif check_invoice_number_exists(custom_number, "Invoice"):
            # Only show the Force button if the number exists
            if st.button(f"⚠️ استخدام {formatted_inv_num}", key="force_generate_header_btn"):
                st.session_state.force_generate_header = True
                st.session_state.force_number = custom_number
                st.session_state.header_message = f"تم تفعيل استخدام رقم الفاتورة: {formatted_inv_num}"
    
    # Display force message if needed
    if hasattr(st.session_state, 'header_message'):
        st.warning(st.session_state.header_message)
    
    # Update the raw invoice number for next render
    st.session_state.raw_invoice_number = custom_invoice_number

# Add Income and Outcome text fields below
income_outcome_cols = st.columns(2)

with income_outcome_cols[0]:
    income_value = st.text_input("Total Income (£)", 
                                value=f"{st.session_state.total_income:.2f}", 
                                key="income_display",
                                disabled=True)
    
with income_outcome_cols[1]:
    outcome_value = st.text_input("Total Outcome (£)", 
                                 value=f"{st.session_state.total_outcome:.2f}", 
                                 key="outcome_display",
                                 disabled=True)

st.markdown("---")

def regenerate_document():
    """Regenerate a document with a new description but keeping the same invoice number"""
    if not st.session_state.current_invoice_number:
        st.error("No invoice number to regenerate with")
        return
        
    # Display the current invoice number
    st.info(f"Regenerating with invoice number: {st.session_state.current_invoice_number}")
    
    # Get a new description
    with st.spinner("Generating new project description..."):
        new_description = generate_smart_description()
    
    # TODO: Implement regeneration with the same invoice number but new description

def display_generated_document():
    """Display the previously generated document and download options"""
    if not st.session_state.document_generated:
        return
        
    with st.container():
        st.success("Document generated successfully!")
        
        # Document Preview section
        st.header("Document Preview")
        st.write(f"📄 Your {st.session_state.generated_data['document_type'].lower()} has been generated with number {st.session_state.generated_data['invoice_number']}")
        
        # Show PDF preview
        if st.session_state.generated_data['pdf_path'] and os.path.exists(st.session_state.generated_data['pdf_path']):
            with open(st.session_state.generated_data['pdf_path'], "rb") as pdf_file:
                pdf_data = pdf_file.read()
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_data,
                    file_name=st.session_state.generated_data['pdf_filename'],
                    mime="application/pdf",
                    key="pdf_download"
                )
        
        # Show JPG preview if available
        if st.session_state.generated_data['jpg_path'] and os.path.exists(st.session_state.generated_data['jpg_path']):
            st.image(st.session_state.generated_data['jpg_path'], caption=f"{st.session_state.generated_data['document_type']} Preview")
            with open(st.session_state.generated_data['jpg_path'], "rb") as jpg_file:
                jpg_data = jpg_file.read()
                st.download_button(
                    label="⬇️ Download JPG",
                    data=jpg_data,
                    file_name=st.session_state.generated_data['jpg_filename'],
                    mime="image/jpeg",
                    key="jpg_download_btn"
                )
        
        # Show text version
        if st.session_state.generated_data['text_version']:
            st.subheader("Text Version")
            st.text_area("Copy this text:", value=st.session_state.generated_data['text_version'], height=100)
            st.download_button(
                label="⬇️ Download Text",
                data=st.session_state.generated_data['text_version'],
                file_name=f"{st.session_state.generated_data['invoice_number']}.txt",
                mime="text/plain",
                key="text_download_btn"
            )
            
        # Accept/Reject section
        st.subheader("Accept or Reject")
        accept_reject_cols = st.columns(2)
        
        with accept_reject_cols[0]:
            if st.button("✅ Accept Document", type="primary", key="accept_document"):
                # Get amount and currency from the generated data
                amount = st.session_state.generated_data['amount']
                currency = st.session_state.generated_data.get('currency', 'GBP')
                
                # Convert USD to GBP for tracking totals (approximate conversion rate)
                converted_amount = amount
                if currency == 'USD':
                    # Use a simplified conversion rate of 0.79 (1 USD = 0.79 GBP)
                    conversion_rate = 0.79
                    converted_amount = amount * conversion_rate
                
                # Update counters based on transaction type
                if st.session_state.generated_data['transaction_type'] == "Income":
                    # Add the converted amount to the total income (always stored in GBP for VAT tracking)
                    st.session_state.total_income += converted_amount
                else:  # Expense
                    # Add the converted amount to the total outcome (always stored in GBP for tracking)
                    st.session_state.total_outcome += converted_amount
                
                # Show success message with appropriate currency symbol
                currency_symbol = "$" if currency == "USD" else "£"
                st.success(f"Document accepted and {st.session_state.generated_data['transaction_type'].lower()} of {currency_symbol}{amount:.2f} recorded!")
                
        with accept_reject_cols[1]:
            if st.button("❌ Reject Document", type="secondary", key="reject_document"):
                st.warning("Document rejected. No financial records were updated.")
    
        # Add a separator at the end of the document display
        st.markdown("---")

def show_download_options(data):
    """Show download options for PDF, JPG and text"""
    # Implement if needed in the future
    pass

def show_document_form():
    """Show the form to create a new document"""
    # Beautiful form container
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown("### 📝 إنشاء مستند جديد")
    
    # Define company details
    COMPANY_NAME = "UPLOAD FOR SOFTWARE LTD"
    COMPANY_ADDRESS = "71-75 Shelton Street, Covent Garden, London, WC2H 9JQ, United Kingdom"
    COMPANY_EMAIL = "Support@uploadforsoftware.com"
    COMPANY_PHONE = ""  # No phone per user request
    COMPANY_WEBSITE = "uploadforsoftware.com"
    COMPANY_NUMBER = "16009190"
    COMPANY_VAT = ""  # No VAT per user request
    
    # Create form layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Transaction type (Income/Expense)
        transaction_type = st.selectbox(
            "Transaction Type",
            options=["Income", "Expense"],
            help="Select whether money is coming in or going out"
        )
        
        # Entity name
        entity_name = st.text_input("Person/Entity Name", help="Name of the person or entity involved in the transaction")
        
        # Currency selection
        currency = st.selectbox(
            "Currency",
            options=["GBP", "USD"],
            help="Select the currency for this transaction"
        )
        
        # Amount with currency symbol
        currency_symbol = "£" if currency == "GBP" else "$"
        amount = st.number_input(f"Amount ({currency_symbol})", min_value=0.01, value=100.00, step=10.0, format="%.2f", 
                              help=f"Amount in {currency}")
        
        # Entity type
        entity_type = st.selectbox(
            "Entity Type",
            options=["Individual", "Company", "Platform"],
            help="Select the type of entity"
        )
    
    with col2:
        # Date (get the current date more explicitly to avoid timezone issues)
        current_date = datetime.datetime.now().date()
        transaction_date = st.date_input("Transaction Date", value=current_date, help="Date of the transaction")
        
        # Payment method
        payment_method = st.selectbox(
            "Payment Method",
            options=["Bank Transfer", "Visa", "PayPal", "Wise", "Other"],
            help="Method of payment"
        )
        
        # Document type
        document_type = st.selectbox(
            "Document Type",
            options=["Invoice", "Receipt"],
            help="Choose the type of document to generate"
        )
        
        # Additional notes (optional)
        notes = st.text_area("Additional Notes", help="Any additional information (optional)", height=100)
    
    # Generate button
    if st.button("Generate Document", type="primary", use_container_width=True):
        if not entity_name:
            st.error("Please enter a name for the person or entity.")
            return
            
        # Get description
        with st.spinner("Generating smart project description..."):
            description = generate_smart_description()
            
        # Initialize force_generate flag if needed
        if 'force_generate' not in st.session_state:
            st.session_state.force_generate = False
            
        # Handle custom invoice number or get next number in sequence
        if custom_invoice_number:
            # Process only if it's a valid digit input
            if custom_invoice_number.isdigit():
                # Convert to integer
                custom_number = int(custom_invoice_number)
                
                # Format the invoice number for display
                formatted_invoice_number = format_invoice_number(custom_number, document_type)
                
                # Special case for number 1 - always allow it
                if custom_number == 1:
                    # Skip all validation for number 1
                    pass
                # Check if the header Force button was clicked - priority over in-form force button
                elif st.session_state.force_generate_header and hasattr(st.session_state, 'force_number'):
                    # Use the exact number from header force without additional checks
                    pass  # Skip the normal validation and use the header force number
                # Check if this number already exists and no force option was used
                elif check_invoice_number_exists(custom_number, document_type) and not st.session_state.force_generate:
                    # Don't show error for number 1
                    if custom_number != 1:
                        st.error(f"رقم الفاتورة {formatted_invoice_number} موجود بالفعل. الرجاء اختيار رقم آخر.")
                        
                        # Show a "Force Generate" button
                        if st.button("⚠️ إنشاء بالرغم من ذلك", type="secondary", key="force_generate_btn"):
                            # Set flag to use this exact number next time
                            st.session_state.force_generate = True
                            st.session_state.force_number = custom_number
                            st.warning(f"اضغط على 'Generate Document' مرة أخرى لإنشاء الفاتورة برقم {formatted_invoice_number}")
                            return
                        else:
                            return
                        
                # Check if Force was used, from either place
                force_used = False
                
                # Force from header button takes priority
                if st.session_state.force_generate_header and hasattr(st.session_state, 'force_number'):
                    # Override the custom_number with our forced number
                    custom_number = st.session_state.force_number
                    force_used = True
                    st.warning(f"استخدام الرقم المحدد مسبقاً: {format_invoice_number(custom_number, document_type)}")
                
                # Check form button force as well
                elif st.session_state.force_generate and hasattr(st.session_state, 'force_number'):
                    custom_number = st.session_state.force_number  
                    force_used = True
                    st.warning(f"استخدام الرقم المحدد: {format_invoice_number(custom_number, document_type)}")
                
                # Do not update counter when forcing
                if not force_used:
                    # Normal case - only set the counter if not forcing
                    set_custom_invoice_number(custom_number, document_type)
                
                # Always create with the exact number
                invoice_number = format_invoice_number(custom_number, document_type)
                
                # Reset all force flags now that we've used them
                st.session_state.force_generate = False
                st.session_state.force_generate_header = False
                if hasattr(st.session_state, 'header_message'):
                    delattr(st.session_state, 'header_message')
                    
                # Format already done above - remove duplicate line
                
                # Show the formatted number if not force_used
                if not force_used:
                    st.success(f"استخدام رقم الفاتورة: {invoice_number}")
            else:
                st.error("يرجى إدخال رقم صالح فقط (مثال: 20)")
                return
        else:
            # No custom number provided, get the next number in sequence
            invoice_number = get_next_invoice_number(document_type)
            
        # Generate text version with proper currency
        text_version = generate_invoice_text(
            transaction_type=transaction_type,
            entity_name=entity_name,
            amount=amount,
            date=transaction_date,
            description=description,
            company_name=COMPANY_NAME,
            currency=currency
        )
        
        # Generate PDF
        try:
            with st.spinner("Generating PDF document..."):
                pdf_filename = generate_pdf(
                    document_type=document_type,
                    transaction_type=transaction_type,
                    entity_name=entity_name,
                    entity_type=entity_type,
                    amount=amount,
                    date=transaction_date,
                    payment_method=payment_method,
                    description=description,
                    notes=notes,
                    invoice_number=invoice_number,
                    company_name=COMPANY_NAME,
                    company_address=COMPANY_ADDRESS,
                    company_email=COMPANY_EMAIL,
                    company_phone=COMPANY_PHONE,
                    company_website=COMPANY_WEBSITE,
                    company_number=COMPANY_NUMBER,
                    company_vat=COMPANY_VAT,
                    currency=currency
                )
                
                # Determine save path
                output_dir = "output"
                os.makedirs(output_dir, exist_ok=True)
                save_path = os.path.join(output_dir, pdf_filename)
                
                # Save the PDF
                with open(save_path, "wb") as f:
                    f.write(open(pdf_filename, "rb").read())
                
                # Convert to JPG and save in date-based folder
                jpg_filename = convert_pdf_to_jpg(pdf_filename, entity_name, transaction_type)
                
                # Load PDF data
                with open(save_path, "rb") as file:
                    pdf_data = file.read()
                
                # Create download filename with invoice number and entity name
                download_pdf_filename = pdf_filename
                if entity_name:
                    # Clean entity name for filename
                    clean_name = ''.join(c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in entity_name)
                    clean_name = clean_name.replace(' ', '_')
                    # Extract the original name without extension
                    base_name = os.path.splitext(pdf_filename)[0]
                    download_pdf_filename = f"{base_name}_{clean_name}.pdf"
                
                # Load JPG data
                jpg_data = None
                if jpg_filename and os.path.exists(jpg_filename):
                    with open(jpg_filename, "rb") as file:
                        jpg_data = file.read()
                
                # Save all data to session state including currency
                st.session_state.generated_data = {
                    'document_type': document_type,
                    'invoice_number': invoice_number,
                    'pdf_path': save_path,
                    'jpg_path': jpg_filename,
                    'pdf_data': pdf_data,
                    'jpg_data': jpg_data,
                    'pdf_filename': download_pdf_filename,
                    'jpg_filename': f"{os.path.splitext(download_pdf_filename)[0]}.jpg",
                    'text_version': text_version,
                    'transaction_type': transaction_type,
                    'amount': amount,
                    'currency': currency
                }
                
                # Set flags
                st.session_state.document_generated = True
                st.session_state.current_invoice_number = invoice_number
                
                # Display success message
                st.success(f"{document_type} generated successfully with number {invoice_number}!")
                
                # Do not rerun - let the normal flow continue
                pass
        except Exception as e:
            st.error(f"Error generating document: {e}")
            return
    
    # Close the form container
    st.markdown('</div>', unsafe_allow_html=True)

# Beautiful separator before tabs
st.markdown('<hr class="separator">', unsafe_allow_html=True)

# Main app layout with beautiful tabs
tab1, tab2 = st.tabs(["📝 إنشاء مستند", "📄 معاينة المستند"])

with tab1:
    show_document_form()
    
with tab2:
    if st.session_state.document_generated:
        display_generated_document()
    else:
        st.markdown('''
        <div class="form-container" style="text-align: center;">
            <h3>📄 لا يوجد مستند للمعاينة</h3>
            <p>قم بإنشاء مستند جديد في تبويب "إنشاء مستند" أولاً</p>
        </div>
        ''', unsafe_allow_html=True)

def main():
    pass

if __name__ == "__main__":
    main()