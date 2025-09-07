# Google Sheets Setup Guide

This guide will help you set up Google Sheets integration for the WhatsApp message processing microservice.

## Prerequisites

1. A Google account
2. Access to Google Cloud Console
3. A Google Sheet where you want to store the extracted data

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note down your project ID

## Step 2: Enable Google Sheets API

1. In the Google Cloud Console, navigate to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Click on it and press "Enable"
4. Also enable "Google Drive API" (required for sheets access)

## Step 3: Create a Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details:
   - **Name**: `whatsapp-processor` (or any name you prefer)
   - **Description**: `Service account for WhatsApp message processing`
4. Click "Create and Continue"
5. For roles, add: "Editor" or "Google Sheets API Service Agent"
6. Click "Done"

## Step 4: Generate Service Account Key

1. In the "Credentials" page, find your newly created service account
2. Click on the service account name
3. Go to the "Keys" tab
4. Click "Add Key" > "Create new key"
5. Select "JSON" format
6. Download the JSON file
7. **Important**: Keep this file secure and never commit it to version control

## Step 5: Prepare Your Google Sheet

1. Create a new Google Sheet or use an existing one
2. Note the sheet name (you'll need this for the `SHEET_NAME` environment variable)
3. Share the sheet with your service account:
   - Open your Google Sheet
   - Click "Share" in the top right
   - Add the service account email (found in the JSON credentials file under `client_email`)
   - Give it "Editor" permissions
   - Uncheck "Notify people" since it's a service account

## Step 6: Set Up Sheet Headers (Optional)

The microservice will automatically create headers, but you can manually set them up:

| Timestamp | Full Name | Phone Number | ID Document |
|-----------|-----------|--------------|-------------|

## Step 7: Configure Environment Variables

1. Copy your JSON credentials file to your project directory
2. Update your `.env` file:

```bash
# Path to your service account JSON file
GOOGLE_SHEETS_CREDENTIALS_PATH=./path/to/your/service-account-key.json

# Your Google Sheet name (exactly as it appears in Google Drive)
SHEET_NAME=WhatsApp User Data

# Your other existing variables...
GEMINI_API_KEY=your_gemini_api_key_here
```

## Step 8: Test the Connection

Run the test function to verify everything works:

```bash
python gsheets_client.py
```

If successful, you should see a test record added to your Google Sheet.

## Security Best Practices

1. **Never commit credentials**: Add your JSON file to `.gitignore`
2. **Restrict permissions**: Only grant necessary permissions to the service account
3. **Regular rotation**: Consider rotating your service account keys periodically
4. **Environment-specific accounts**: Use different service accounts for development and production

## Troubleshooting

### Common Issues:

1. **"Permission denied" error**:
   - Make sure you've shared the sheet with the service account email
   - Check that the service account has "Editor" permissions

2. **"Sheet not found" error**:
   - Verify the `SHEET_NAME` exactly matches your Google Sheet name
   - Make sure the service account has access to the sheet

3. **"Credentials not found" error**:
   - Check that the `GOOGLE_SHEETS_CREDENTIALS_PATH` points to the correct file
   - Verify the JSON file is valid and not corrupted

4. **"API not enabled" error**:
   - Ensure both Google Sheets API and Google Drive API are enabled in your Google Cloud Console

### Testing Individual Components:

```bash
# Test Google Sheets connection only
python -c "from gsheets_client import GSheetsClient; client = GSheetsClient(); print('Connection successful!')"

# Test with sample data
python -c "
from gsheets_client import GSheetsClient
client = GSheetsClient()
test_data = {'full_name': 'Test User', 'phone_number': '1234567890', 'id_document': '12345'}
result = client.insert_user_data(test_data)
print(f'Insertion result: {result}')
"
```

## Sheet Structure

The microservice will create/use this structure in your Google Sheet:

- **Column A**: Timestamp (when the data was processed)
- **Column B**: Full Name (extracted from message)
- **Column C**: Phone Number (extracted from message)
- **Column D**: ID Document (extracted from message)

Each row represents one processed message with extracted user data.