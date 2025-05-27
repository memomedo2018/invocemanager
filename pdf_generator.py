import io
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfgen import canvas

def generate_pdf(
    document_type, transaction_type, entity_name, entity_type, 
    amount, date, payment_method, description, notes, invoice_number,
    company_name, company_address, company_email, company_phone,
    company_website, company_number, company_vat, currency="GBP"
):
    """
    Generate a PDF invoice or receipt
    
    Returns:
        str: The filename of the generated PDF
    """
    # Create a filename based on document type and invoice number
    filename = f"{document_type.lower()}_{invoice_number}_{date.strftime('%Y%m%d')}.pdf"
    
    # Create a buffer for the PDF
    buffer = io.BytesIO()
    
    # Create the PDF document with reduced margins for compact layout
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,  # Reduced from 72
        leftMargin=36,   # Reduced from 72
        topMargin=36,    # Reduced from 72
        bottomMargin=36  # Reduced from 72
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles - reducing font sizes for compact layout
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='DocumentTitle',
        fontName='Helvetica-Bold',
        fontSize=14,  # Reduced from 18
        alignment=1,
        spaceAfter=6  # Reduced from 12
    ))
    styles.add(ParagraphStyle(
        name='SectionHeading',
        fontName='Helvetica-Bold',
        fontSize=10,  # Reduced from 14
        alignment=0,
        spaceAfter=4  # Reduced from 6
    ))
    styles.add(ParagraphStyle(
        name='BasicText',
        fontName='Helvetica',
        fontSize=8,   # Reduced from 10
        alignment=0,
        spaceAfter=3  # Reduced from 6
    ))
    styles.add(ParagraphStyle(
        name='BoldText',
        fontName='Helvetica-Bold',
        fontSize=8,   # Reduced from 10
        alignment=0,
        spaceAfter=3  # Reduced from 6
    ))
    styles.add(ParagraphStyle(
        name='RightAligned',
        fontName='Helvetica',
        fontSize=8,   # Reduced from 10
        alignment=2,
        spaceAfter=3  # Reduced from 6
    ))
    styles.add(ParagraphStyle(
        name='CenterAligned',
        fontName='Helvetica',
        fontSize=8,   # Reduced from 10
        alignment=1,
        spaceAfter=3  # Reduced from 6
    ))
    
    # Create a table for the header with logo on the right
    logo_path = "assets/company_logo.png"
    header_data = []
    if os.path.exists(logo_path):
        try:
            logo = Image(logo_path)
            # Resize logo to small size (max width 1 inch)
            logo_width = 1 * inch
            logo_height = (logo.imageHeight * logo_width) / logo.imageWidth
            logo.drawWidth = logo_width
            logo.drawHeight = logo_height
            
            # Create a header table with logo on the right
            header_data = [[Paragraph(f"<b>{document_type.upper()}</b>", styles['DocumentTitle']), logo]]
        except Exception as e:
            # If logo fails, just add the document title
            header_data = [[Paragraph(f"<b>{document_type.upper()}</b>", styles['DocumentTitle']), ""]]
    else:
        header_data = [[Paragraph(f"<b>{document_type.upper()}</b>", styles['DocumentTitle']), ""]]
    
    header_table = Table(header_data, colWidths=[4*doc.width/5.0, 1*doc.width/5.0])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.1*inch))
    
    # Company and Customer Information
    data = [
        [Paragraph(f"<b>{company_name}</b>", styles['BasicText']), 
         Paragraph(f"<b>Document Number:</b> {invoice_number}", styles['RightAligned'])],
        [Paragraph(company_address, styles['BasicText']), 
         Paragraph(f"<b>Date:</b> {date.strftime('%d/%m/%Y')}", styles['RightAligned'])],
        [Paragraph(f"Email: {company_email}", styles['BasicText']), ""],
    ]
    
    # Add website if available
    if company_website:
        data.append([Paragraph(f"Website: {company_website}", styles['BasicText']), ""])
    
    # Add company number if available
    if company_number:
        data.append([Paragraph(f"Company No: {company_number}", styles['BasicText']), ""])
    
    # Add phone only if it's not empty
    if company_phone:
        data.append([Paragraph(f"Phone: {company_phone}", styles['BasicText']), ""])
    
    # Add VAT only if it's not empty
    if company_vat:
        data.append([Paragraph(f"VAT: {company_vat}", styles['BasicText']), ""])
    
    company_table = Table(data, colWidths=[doc.width/2.0]*2)
    company_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(company_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Customer/Vendor Information Section
    if transaction_type == "Income":
        customer_title = "CUSTOMER INFORMATION"
        entity_label = "Customer Name:"
    else:
        customer_title = "VENDOR INFORMATION"
        entity_label = "Vendor Name:"
    
    elements.append(Paragraph(customer_title, styles['SectionHeading']))
    elements.append(Spacer(1, 0.1*inch))
    
    customer_data = [
        [Paragraph(f"<b>{entity_label}</b>", styles['BasicText']), 
         Paragraph(entity_name, styles['BasicText'])],
        [Paragraph("<b>Type:</b>", styles['BasicText']), 
         Paragraph(entity_type, styles['BasicText'])],
    ]
    
    customer_table = Table(customer_data, colWidths=[doc.width/4.0, 3*doc.width/4.0])
    customer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 0.1*inch))
    
    # Transaction Details Section
    elements.append(Paragraph("TRANSACTION DETAILS", styles['SectionHeading']))
    elements.append(Spacer(1, 0.1*inch))
    
    # Header row for the transaction table
    transaction_data = [
        ["Description", "Amount"],
        [description, f"£{amount:.2f}"],
    ]
    
    # If there are notes, add them
    if notes:
        transaction_data.append(["Notes:", notes])
    
    transaction_table = Table(transaction_data, colWidths=[3*doc.width/4.0, doc.width/4.0])
    transaction_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(transaction_table)
    elements.append(Spacer(1, 0.1*inch))
    
    # Payment Information
    elements.append(Paragraph("PAYMENT INFORMATION", styles['SectionHeading']))
    elements.append(Spacer(1, 0.1*inch))
    
    payment_data = [
        ["Payment Method:", payment_method],
        ["Transaction Type:", transaction_type],
        ["Payment Date:", date.strftime('%d/%m/%Y')],
    ]
    
    payment_table = Table(payment_data, colWidths=[doc.width/4.0, 3*doc.width/4.0])
    payment_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(payment_table)
    elements.append(Spacer(1, 0.1*inch))
    
    # Determine currency symbol based on currency parameter
    currency_symbol = "$" if currency == "USD" else "£"
    
    # Total Section
    total_data = [
        ["", "Total", f"{currency_symbol}{amount:.2f}"],
    ]
    
    total_table = Table(total_data, colWidths=[2*doc.width/4.0, doc.width/4.0, doc.width/4.0])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (1, 0), (1, 0), colors.lightgrey),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.black),
        ('ALIGN', (1, 0), (2, 0), 'RIGHT'),
        ('FONTNAME', (1, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 0), (2, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(total_table)
    
    # Add simple VAT notice to fix stability issue
    elements.append(Spacer(1, 0.05*inch))
    vat_notice = Paragraph('<font color="red">No VAT charged – supplier is not VAT registered.</font>', styles['Normal'])
    elements.append(vat_notice)
    
    # Footer with thank you message and bank details for GBP payments
    elements.append(Spacer(1, 0.1*inch))
    
    if transaction_type == "Income":
        thank_you_msg = "Thank you for your business!"
        
        # Add bank details for GBP payments
        elements.append(Paragraph(thank_you_msg, styles['CenterAligned']))
        elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Paragraph("BANK PAYMENT DETAILS", styles['SectionHeading']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Instructions before table
        instructions = "Here are the GBP account details for Upload For Software Ltd on Wise.\n"
        instructions += "If you're sending money from a bank in the UK, use these details for a domestic transfer. "
        instructions += "For international payments, use the Swift/BIC details."
        
        elements.append(Paragraph(instructions, styles['BasicText']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Bank details in a properly sized table to avoid page break issues
        bank_data = [
            ["Name:", "Upload For Software Ltd"],
            ["Account number:", "15336022"],
            ["Sort code:", "23-08-01 (Use when sending money from the UK)"],
            ["IBAN:", "GB83 TRWI 2308 0115 3360 22"],
            ["Swift/BIC:", "TRWIGB2LXXX (Use when sending money from outside the UK)"],
            ["Bank name:", "Wise Payments Limited"],
            ["Bank address:", "1st Floor, Worship Square, 65 Clifton Street, London, EC2A 4JE, United Kingdom"]
        ]
        
        # Make sure the table fits within page width
        bank_table = Table(bank_data, colWidths=[doc.width*0.25, doc.width*0.75], splitByRow=True)
        bank_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(bank_table)
    else:
        thank_you_msg = "Thank you for your services!"
        elements.append(Paragraph(thank_you_msg, styles['CenterAligned']))
    
    # Build the PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Save to file
    with open(filename, 'wb') as f:
        f.write(pdf_data)
    
    return filename
