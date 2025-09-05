import os
import firebase_admin
from firebase_admin import credentials, firestore
from google.oauth2 import service_account as gservice_account
from googleapiclient.discovery import build
from datetime import datetime, timezone

# Initialize Firebase only once
if not firebase_admin._apps:
    firebase_json_path = os.path.join(os.path.dirname(__file__), "firebase.json")
    cred = credentials.Certificate(firebase_json_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Google Sheets and Drive API setup
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "google-service-account.json")

gcredentials = gservice_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
sheets_service = build("sheets", "v4", credentials=gcredentials)
drive_service = build("drive", "v3", credentials=gcredentials)

# --- NEW: Use one master spreadsheet to avoid quota issues ---
# MANUALLY CREATE A SPREADSHEET IN YOUR DRIVE AND PASTE THE ID HERE
MASTER_SPREADSHEET_ID = "1xh0awAjdBRv4MP5poZExV-saRiBZU2Vu2VCu4RLqwHE" 

# Folder configuration is no longer needed for sheet creation
# ORDERS_FOLDER_ID = "1tLiyIY-hDVLMBP_mUnxvAAP3y8XiiEte"

def get_orders_folder_id():
    """Get the folder ID for SMS Chatbot Orders folder"""
    # This is now only for reference, not for creating sheets
    return "1tLiyIY-hDVLMBP_mUnxvAAP3y8XiiEte"

# Helper: Get or create a TAB (sheet) for a delivery date in the master spreadsheet
def get_or_create_sheet_for_date(delivery_date):
    """
    Get existing tab (sheet) for a delivery date, or create a new one if it doesn't exist.
    delivery_date: string, e.g. 'Friday, January 17, 2025' or '2025-01-17'
    """
    if MASTER_SPREADSHEET_ID == "YOUR_MASTER_SPREADSHEET_ID_HERE":
        raise Exception("Please set the MASTER_SPREADSHEET_ID in sheets_logic.py")

    try:
        # Create a sortable tab name (YYYY-MM-DD format for easy sorting)
        from datetime import datetime
        
        # Try to parse the delivery_date to create a sortable name
        try:
            # Handle various date formats
            if ',' in delivery_date:
                # Format like "Friday, January 17, 2025"
                date_part = delivery_date.split(', ', 1)[1]  # Remove day of week
                parsed_date = datetime.strptime(date_part, '%B %d, %Y')
            else:
                # Try other formats
                parsed_date = datetime.strptime(delivery_date, '%Y-%m-%d')
            
            # Create sortable tab name: "2025-01-17 (Friday, Jan 17)"
            sortable_name = f"{parsed_date.strftime('%Y-%m-%d')} ({parsed_date.strftime('%a, %b %d')})"
        except:
            # If parsing fails, use original name
            sortable_name = delivery_date
        
        # Check if a sheet with this name already exists
        sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=MASTER_SPREADSHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', [])
        
        for sheet in sheets:
            sheet_title = sheet.get('properties', {}).get('title', '')
            # Check both the sortable name and original delivery_date
            if sheet_title == sortable_name or sheet_title == delivery_date:
                return MASTER_SPREADSHEET_ID

        # If not found, create a new tab with the sortable name
        body = {
            'requests': [
                {
                    'addSheet': {
                        'properties': {
                            'title': sortable_name
                        }
                    }
                }
            ]
        }
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=MASTER_SPREADSHEET_ID,
            body=body
        ).execute()

        # Add header row to the new sheet
        header_row = [
            "Order Time", "Customer Phone", "Business Name", "Order Items", 
            "Delivery Address", "Delivery Date", "Notes", "Status"
        ]
        
        # Use the sortable name in the range
        sheets_service.spreadsheets().values().append(
            spreadsheetId=MASTER_SPREADSHEET_ID,
            range=f"'{sortable_name}'!A1", 
            valueInputOption="RAW",
            body={"values": [header_row]}
        ).execute()

        return MASTER_SPREADSHEET_ID

    except Exception as e:
        raise e

# Helper: Add an order to the correct sheet (now a tab)
def add_order_to_sheet(delivery_date, order_data):
    """
    Add a confirmed order to the spreadsheet for the delivery date
    delivery_date: string, the delivery date for the order
    order_data: dict with order details
    """
    try:
        spreadsheet_id = get_or_create_sheet_for_date(delivery_date)
        
        # Create the same sortable tab name used in get_or_create_sheet_for_date
        from datetime import datetime
        try:
            if ',' in delivery_date:
                date_part = delivery_date.split(', ', 1)[1]
                parsed_date = datetime.strptime(date_part, '%B %d, %Y')
            else:
                parsed_date = datetime.strptime(delivery_date, '%Y-%m-%d')
            
            tab_name = f"{parsed_date.strftime('%Y-%m-%d')} ({parsed_date.strftime('%a, %b %d')})"
        except:
            tab_name = delivery_date
        
        # Extract business name from address (first part before comma)
        address = order_data.get("delivery_address", "")
        business_name = address.split(",")[0].strip() if "," in address else "Unknown Business"
        
        # Format order items as a readable string
        if isinstance(order_data.get("order"), list):
            # If order is a list of items
            items_str = ", ".join([f"{item.get('quantity', '')} {item.get('product', '')}" 
                                 for item in order_data.get("order", [])])
        else:
            # If order is already a string
            items_str = str(order_data.get("order", ""))
        
        # Prepare row data
        row = [
            order_data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            order_data.get("phone", ""),
            business_name,
            items_str,
            order_data.get("delivery_address", ""),
            delivery_date,
            order_data.get("notes", ""),
            "Confirmed"
        ]
        
        # Add row to spreadsheet, using the sortable tab name
        sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"'{tab_name}'!A1",
            valueInputOption="RAW",
            body={"values": [row]}
        ).execute()
        
        return spreadsheet_id
        
    except Exception as e:
        raise e

# Helper: Process confirmed order from conversation
def process_confirmed_order(phone_number, order_details):
    """
    Process a confirmed order and add it to the appropriate spreadsheet
    phone_number: customer's phone number
    order_details: parsed order details from conversation
    """
    try:
        # Format order data for spreadsheet
        order_data = {
            "phone": phone_number,
            "order": order_details.get("items", []),
            "delivery_address": order_details.get("delivery_address", ""),
            "notes": order_details.get("notes", ""),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        delivery_date = order_details.get("delivery_date", "")
        
        # Add to spreadsheet
        spreadsheet_id = add_order_to_sheet(delivery_date, order_data)
        
        return spreadsheet_id
        
    except Exception as e:
        raise e

# Helper: List all order sheets
def list_order_sheets():
    """Get all order sheets from Firestore"""
    try:
        sheets_ref = db.collection("order_sheets")
        docs = sheets_ref.stream()
        
        sheets = []
        for doc in docs:
            data = doc.to_dict()
            data["doc_id"] = doc.id
            sheets.append(data)
        
        return sheets
        
    except Exception as e:
        return [] 