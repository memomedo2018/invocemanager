import os
import random

def generate_smart_description():
    """
    Generate a smart description about software development services
    Describes a specific software project requested by client
    
    Returns:
        str: A suitable description for the invoice/receipt with a product name
    """
    # Software project descriptions
    software_descriptions = [
        "Development of custom inventory management system",
        "Mobile application development for customer engagement",
        "Web portal implementation for client management",
        "E-commerce platform development with payment integration",
        "Business intelligence dashboard implementation",
        "Custom CRM system development and integration",
        "API development for third-party service integration",
        "Software maintenance and performance optimization",
        "Legacy system modernization and migration",
        "Cloud migration and infrastructure setup",
        "Enterprise resource planning system implementation",
        "Customer service ticketing system development",
        "Accounting software customization",
        "HR management system development",
        "E-learning platform development and integration",
        "Real-time messaging application development",
        "Project management software implementation",
        "Data visualization dashboard development",
        "Automated reporting system implementation",
        "Membership management portal development",
        "Online booking system implementation",
        "Fleet management software development",
        "Restaurant management system implementation",
        "Inventory tracking software development",
        "Point of sale system implementation"
    ]
    
    # Product/System names
    product_names = [
        "ProAccess",
        "SmartFlow",
        "DataVista",
        "NexusCore",
        "OmniTrack",
        "InteliServe",
        "PrimeSoft",
        "MetaLogic",
        "OptiSphere",
        "VisiTech",
        "SyncWave",
        "PrecisionPro",
        "TotalSphere",
        "EnterLogic",
        "MaxiTech",
        "PowerPortal",
        "SmartPulse",
        "EliteServe",
        "SyncMatrix",
        "TechEdge"
    ]

    # Generate a description with a product name
    description = random.choice(software_descriptions) + " - " + random.choice(product_names) + " System"
    return description
