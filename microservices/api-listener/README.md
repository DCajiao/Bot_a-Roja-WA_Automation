# WhatsApp Message Processing Microservice

A Flask microservice that processes WhatsApp webhook messages and extracts user data (full name, phone number, and ID document) using Google AI Studio (Gemini).

## Features

- ✅ Processes WhatsApp webhook messages from specific group
- ✅ Validates group membership and message format
- ✅ Extracts user data using AI (Gemini 2.5 Flash)
- ✅ Returns structured JSON responses
- ✅ Handles errors gracefully with null values
- ✅ Modular architecture with separated concerns

## Project Structure

```
├── main.py                 # Flask application and endpoints
├── message_processor.py    # WhatsApp message validation and processing
├── ai_processor.py        # AI data extraction using Gemini
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Installation

1. **Clone the repository and navigate to the project directory**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Google AI Studio API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

4. **Get your Gemini API Key:**
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create or select a project
   - Generate an API key
   - Copy the key to your `.env` file

## Usage

### Start the server:
```bash
python main.py
```

The service will start on `http://localhost:5000`

### Endpoints

#### 1. `/webhook` (POST)
Main endpoint for processing WhatsApp webhooks.

**Expected payload:** WhatsApp webhook message (see example in documentation)

**Response format:**
```json
{
  "success": true,
  "message_content": "Hola, soy Juan Pérez, mi teléfono es 573123456789 y mi cédula es 12345678",
  "full_name": "Juan Pérez",
  "phone_number": "573123456789", 
  "id_document": "12345678"
}
```

#### 2. `/test` (GET)
Health check endpoint.

#### 3. `/test-ai` (POST)
Direct AI testing endpoint.

**Request:**
```json
{
  "message": "Your test message here"
}
```

## Message Processing Logic

### Validation Rules
1. **Group Validation**: `data.key.remoteJid` must be `"120363403986445201@g.us"`
2. **Group Message**: `data.key.participantLid` must exist
3. **Content Extraction**: Extracts `data.message.conversation`

### AI Data Extraction
The AI processor extracts three specific pieces of information:
- **Full Name**: Complete person name (first + last name minimum)
- **Phone Number**: Any telephone number (with/without country code)
- **ID Document**: Any identification number (cédula, DNI, passport, etc.)

### Error Handling
- Returns `null` for any missing data fields
- Maintains consistent JSON structure even during errors
- Logs errors for debugging while returning user-friendly responses

## Testing

### Test with curl:

**Test the webhook endpoint:**
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d @sample_payload.json
```

**Test AI extraction directly:**
```bash
curl -X POST http://localhost:5000/test-ai \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, soy Ana García, mi teléfono es 573112345678 y mi documento es 87654321"}'
```

**Health check:**
```bash
curl http://localhost:5000/test
```

## Configuration

Environment variables in `.env`:

- `GEMINI_API_KEY`: Your Google AI Studio API key (required)
- `FLASK_ENV`: Flask environment (development/production)
- `FLASK_DEBUG`: Enable/disable debug mode (True/False)
- `PORT`: Server port (default: 5000)

## Dependencies

- **Flask**: Web framework
- **python-dotenv**: Environment variable management
- **google-genai**: Google AI Studio client library
- **requests**: HTTP library for external requests

## Error Responses

All error responses maintain the same structure:

```json
{
  "success": false,
  "error": "Error description",
  "full_name": null,
  "phone_number": null,
  "id_document": null
}
```