import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sheets_logic import add_order_to_sheet
from datetime import datetime, timezone

def test_add_order():
    # Use timezone-aware datetime instead of deprecated utcnow()
    delivery_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    order_data = {
        "customer_name": "Test Customer",
        "phone": "+19998887777",
        "order": "5 lbs salmon, 2 lbs shrimp",
        "notes": "Test order, ignore",
    }
    print(f"Adding order for delivery date: {delivery_date}")
    
    try:
        spreadsheet_id = add_order_to_sheet(delivery_date, order_data)
        print(f"✅ Order added! Spreadsheet ID: {spreadsheet_id}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nIf you see a Firestore API error, you need to:")
        print("1. Go to https://console.firebase.google.com/")
        print("2. Select your project")
        print("3. Go to Firestore Database")
        print("4. Create database if not exists")
        print("5. Or enable the Firestore API in Google Cloud Console")

def test_google_sheets_only():
    """Test just the Google Sheets functionality without Firestore"""
    print("\n--- Testing Google Sheets API only ---")
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        SERVICE_ACCOUNT_FILE = "google-service-account.json"
        
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        sheets_service = build("sheets", "v4", credentials=credentials)
        
        # Test creating a simple spreadsheet
        sheet_title = "test-sheet-api"
        spreadsheet = sheets_service.spreadsheets().create(
            body={
                "properties": {"title": sheet_title},
                "parents": ["YOUR_FOLDER_ID_HERE"]  # Add this line
            },
            fields="spreadsheetId"
        ).execute()
        
        spreadsheet_id = spreadsheet["spreadsheetId"]
        print(f"✅ Google Sheets API works! Created test sheet: {spreadsheet_id}")
        
        # Clean up - delete the test sheet
        # Note: This requires additional permissions, so we'll just report success
        
    except Exception as e:
        print(f"❌ Google Sheets API error: {e}")

if __name__ == "__main__":
    test_google_sheets_only()
    test_add_order() 