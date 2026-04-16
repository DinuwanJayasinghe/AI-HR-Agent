# CV Review & Analysis System

An automated CV screening system that downloads CVs from Gmail, analyzes them using AI, and ranks candidates based on ATS compatibility.

## Features

- 📧 **Automatic CV Download from Gmail** - Downloads CV attachments using IMAP
- 📅 **Date-Based Filtering** - Download CVs from last 1, 3, 7, or any number of days
- 🤖 **AI-Powered Analysis** - Uses Google Gemini AI for resume analysis
- 📊 **ATS Scoring** - Scores resumes for ATS compatibility (0-100)
- 🏆 **Smart Ranking** - Automatically ranks top 10 candidates
- 💬 **Chat Interface** - Interactive chat agent for CV queries
- 🔌 **REST API** - FastAPI backend for easy integration
- ⏰ **Schedulable** - Set up automatic daily/weekly CV processing

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment Variables

Create a `.env` file with:

```env
EMAIL = 'your-email@gmail.com'
EMAIL_PASSWORD = 'your-gmail-app-password'
GOOGLE_API_KEY = 'your-google-gemini-api-key'
OPEN_AI_API_KEY = 'your-openai-api-key'  # Optional for chat agent
```

**Important:** Use Gmail App Password (not your regular password)
- Go to: https://myaccount.google.com/apppasswords
- Generate an app password for "Mail"
- Use that 16-character password in `.env`

### 3. Download CVs from Gmail

```bash
python download_cvs_imap.py
```

This will:
- Connect to your Gmail
- Search for CV attachments (PDF, DOC, DOCX)
- Download them to `cv_collection/` folder

### 4. Run the API Server

```bash
python main.py
```

Server will start at: `http://127.0.0.1:8000`

## API Endpoints

### 1. Download CVs by Date (NEW! ⭐)

```bash
POST http://127.0.0.1:8000/api/download-cvs-by-date
Content-Type: application/json

{
  "days_back": 7,
  "job_position": "R&D Engineer",
  "job_description": "Looking for R&D Engineer with Python experience",
  "analyze": true
}
```

**Parameters:**
- `days_back` (int): Number of days to look back (1=today, 7=week, 30=month)
- `job_position` (str): Filter emails by job position in subject
- `job_description` (str): Job description for better matching
- `analyze` (bool): Auto-analyze after download (default: true)

### 2. Review CVs from Gmail

```bash
POST http://127.0.0.1:8000/api/review-cvs
Content-Type: application/json

{
  "job_description": "Looking for R&D Engineer with Python experience",
  "use_drive": false
}
```

### 3. Chat with AI Agent

```bash
POST http://127.0.0.1:8000/api/chat
Content-Type: application/json

{
  "message": "Download and analyze CVs from last 3 days for R&D Engineer"
}
```

**Natural Language Examples:**
- "Download CVs from today"
- "Show me CVs from last week for Data Scientist"
- "How many CVs came in last 3 days?"

### 4. Health Check

```bash
GET http://127.0.0.1:8000/health
```

## Project Structure

```
contact_workflow/
├── agent/
│   ├── chat_agent.py                # LangGraph chat agent
│   ├── tools/
│   │   ├── cv_review_tools.py       # CV analysis tools
│   │   └── cv_downloader_tool.py    # Date-based download
│   └── __init__.py
├── routes/
│   └── api.py                       # FastAPI routes
├── utils/
│   └── prompts.py                  # AI prompts
├── cv_collection/                  # Downloaded CVs storage
├── download_cvs_imap.py            # Manual CV downloader
├── test_auto_download.py           # Test automatic download
├── main.py                         # FastAPI app
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables
├── README.md                       # This file
└── AUTO_CV_DOWNLOAD_GUIDE.md       # Detailed automation guide
```

## How It Works

1. **CV Collection**: Script connects to Gmail via IMAP and downloads CV attachments
2. **Text Extraction**: Extracts text from PDF/DOCX files
3. **AI Analysis**: Gemini AI analyzes each resume for:
   - ATS compatibility score (0-100)
   - Key strengths
   - Areas for improvement
   - Relevant keywords
   - Overall assessment
4. **Ranking**: Sorts candidates by ATS score and returns top 10

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Example Response

```json
{
  "status": "success",
  "result": {
    "cv_folder": "F:\\...\\cv_collection",
    "downloaded_count": 5,
    "total_resumes_analyzed": 5,
    "top_10_resumes": [
      {
        "rank": 1,
        "file_name": "20251226_114626_john_doe.pdf",
        "sender": "john@example.com",
        "ats_score": 85,
        "strengths": [
          "Strong technical skills",
          "Relevant experience",
          "Clear quantifiable achievements"
        ],
        "improvements": [
          "Add more keywords",
          "Include certifications"
        ],
        "keywords": ["Python", "Machine Learning", "API"],
        "assessment": "Strong candidate with relevant experience..."
      }
    ]
  }
}
```

## Requirements

- Python 3.8+
- Gmail account with App Password enabled
- Google Gemini API key
- OpenAI API key (optional, for chat features)

## Scheduling Automatic Downloads

You can schedule automatic CV processing to run daily:

### Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 9:00 AM
4. Action: Start a program
   - Program: `C:\Path\To\Python\python.exe`
   - Arguments: `test_auto_download.py`
   - Start in: `F:\uni\HR agent final project\contact_workflow`

### Linux/Mac Cron
```bash
# Run every day at 9 AM
0 9 * * * cd /path/to/contact_workflow && python3 test_auto_download.py
```

This will automatically download and analyze new CVs every day!

## Troubleshooting

**Gmail Login Failed?**
- Make sure you're using an App Password, not your regular password
- Enable IMAP in Gmail settings

**No CVs Downloaded?**
- Check if your emails contain PDF/DOC/DOCX attachments
- Try increasing the `days_back` parameter

**API Errors?**
- Verify all environment variables are set in `.env`
- Check API keys are valid

## Documentation

- **Main Guide**: This README
- **Detailed Automation Guide**: [AUTO_CV_DOWNLOAD_GUIDE.md](AUTO_CV_DOWNLOAD_GUIDE.md)
- **API Documentation**: http://127.0.0.1:8000/docs (when server running)

## License

MIT License
