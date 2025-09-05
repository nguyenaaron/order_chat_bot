#!/usr/bin/env python3
"""
Test Google Drive Access for Service Account
"""

import os
from google.oauth2 import service_account as gservice_account
from googleapiclient.discovery import build

# Configuration
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "google-service-account.json")
ORDERS_FOLDER_ID = "1tLiyIY-hDVLMBP_mUnxvAAP3y8XiiEte"

def test_drive_access():
    try:
        # Set up credentials
        credentials = gservice_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        drive_service = build("drive", "v3", credentials=credentials)
        
        print("🔍 Testing Google Drive Access")
        print("=" * 50)
        
        # Test 1: Check if we can access the folder
        print("1. Testing folder access...")
        try:
            folder = drive_service.files().get(fileId=ORDERS_FOLDER_ID).execute()
            print(f"   ✅ Can access folder: {folder.get('name')}")
        except Exception as e:
            print(f"   ❌ Cannot access folder: {e}")
            return
        
        # Test 2: Check folder permissions
        print("\n2. Checking folder permissions...")
        try:
            permissions = drive_service.permissions().list(fileId=ORDERS_FOLDER_ID).execute()
            print(f"   📋 Folder has {len(permissions.get('permissions', []))} permission(s)")
            for perm in permissions.get('permissions', []):
                print(f"      - {perm.get('emailAddress', 'N/A')}: {perm.get('role', 'N/A')}")
        except Exception as e:
            print(f"   ⚠️  Cannot check permissions: {e}")
        
        # Test 3: Try creating a simple text file
        print("\n3. Testing file creation...")
        try:
            file_metadata = {
                'name': 'TEST_FILE_DELETE_ME.txt',
                'parents': [ORDERS_FOLDER_ID],
                'mimeType': 'text/plain'
            }
            
            test_file = drive_service.files().create(
                body=file_metadata,
                fields='id,name'
            ).execute()
            
            print(f"   ✅ Successfully created test file: {test_file.get('name')}")
            print(f"   📋 File ID: {test_file.get('id')}")
            
            # Clean up - delete the test file
            drive_service.files().delete(fileId=test_file.get('id')).execute()
            print("   🗑️  Test file deleted")
            
        except Exception as e:
            print(f"   ❌ Cannot create file: {e}")
            if "quota" in str(e).lower():
                print("   💡 This confirms it's a storage quota issue")
                print("   💡 The service account might not be using your shared storage")
        
        print("\n" + "=" * 50)
        print("✅ Drive access test completed!")
        
    except Exception as e:
        print(f"❌ Setup error: {e}")

if __name__ == "__main__":
    test_drive_access() 