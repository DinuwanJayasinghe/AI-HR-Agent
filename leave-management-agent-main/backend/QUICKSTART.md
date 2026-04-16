# Quick Start Guide

This guide will help you get the Leave Management System up and running in minutes.

## Prerequisites

- Python 3.8+ installed
- Node.js 16+ installed
- Gmail account with App Password configured
- OpenAI API key

## Step-by-Step Setup

### 1. Backend Setup

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment Variables
Create a `.env` file in the root directory:
```
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
OPENAI_API_KEY=sk-your-openai-key
HR_EMAIL=hr@company.com
IMAP_SERVER=imap.gmail.com
SMTP_SERVER=smtp.gmail.com
```

#### Initialize Database
The database will be created automatically when you first run the system. Default employees will be seeded.

### 2. Frontend Setup

#### Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### 3. Running the System

You need to run TWO processes:

#### Terminal 1: Start the API Server
```bash
python api_server.py
```
This starts the Flask API on http://localhost:5000

#### Terminal 2: Start the Frontend
```bash
cd frontend
npm run dev
```
This starts the React frontend on http://localhost:5173

#### Terminal 3 (Optional): Start Email Agent
```bash
python main.py
```
This starts the background email processing agent

### 4. Access the Application

Open your browser and go to:
```
http://localhost:5173
```

You should see the Leave Management System dashboard!

## Quick Testing

### Add a Test Employee

1. Click "Add Employee" in the dashboard or employees section
2. Fill in the form:
   - Name: Test User
   - Email: test@company.com
   - Manager: manager@company.com
   - Leave Balances: Default values (15, 10, 5)
3. Click "Add Employee"

### View Employee Details

1. Go to the "Employees" section
2. Click on any employee card
3. You can view and edit their leave balances

### Simulate Leave Request (via Email)

Send an email to your configured EMAIL_ADDRESS with:
- Subject: Leave Request
- Body:
```
Hi,

I would like to request leave from January 15, 2026 to January 20, 2026 (5 days) for vacation purposes.

Reason: Family vacation

Thank you!
```

The email agent will process it automatically if running!

## Troubleshooting

### Port Already in Use

If port 5000 or 5173 is already in use:

**For API (Port 5000)**:
Edit `api_server.py` line 135:
```python
app.run(debug=True, port=5001)  # Change to 5001
```
Then update `frontend/src/services/api.js` line 3:
```javascript
const API_BASE_URL = 'http://localhost:5001/api';
```

**For Frontend (Port 5173)**:
Create `frontend/vite.config.js`:
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000  // Change to desired port
  }
})
```

### CORS Errors

If you see CORS errors in the browser console:
1. Make sure the API server is running
2. Check that the API_BASE_URL in `frontend/src/services/api.js` matches your API server URL

### Database Not Found

The database will be created automatically at `data/employees.db` on first run. Make sure the `data` directory exists or will be created.

### Gmail Authentication Failed

1. Make sure 2FA is enabled on your Google account
2. Generate a new App Password: https://myaccount.google.com/apppasswords
3. Use the 16-character password (no spaces) in your `.env` file

## Default Users

The system comes with two default employees:
- **John Doe** (john.doe@company.com)
  - Vacation: 15 days
  - Sick Leave: 10 days
  - Personal Leave: 5 days

- **Jane Smith** (jane.smith@company.com)
  - Vacation: 20 days
  - Sick Leave: 10 days
  - Personal Leave: 5 days

## Features Overview

### Dashboard
- View total employees
- See aggregate leave statistics
- Quick action cards for common tasks
- Recent employee activity

### Employees
- Grid view of all employees
- Search by name or email
- Add new employees with initial leave balances
- Click to view detailed employee profile
- Edit leave balances directly

### Leave Requests
- View all leave requests (when processed via email)
- Filter by status: All, Pending, Approved, Rejected
- Color-coded status badges
- Detailed request information

## Next Steps

1. **Customize Policies**: Edit leave policies in the backend
2. **Add Real Employees**: Use the "Add Employee" feature
3. **Test Email Integration**: Send a test leave request email
4. **Explore Analytics**: (Coming soon)
5. **Configure Notifications**: Set up email templates

## Support

For issues or questions:
1. Check the main [README.md](README.md)
2. Review the [frontend/README.md](frontend/README.md)
3. Check API server logs for errors
4. Check browser console for frontend errors

## Architecture Summary

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Browser    │ ───> │  React App   │ ───> │  Flask API   │
│ (Port 5173)  │      │  (Frontend)  │      │ (Port 5000)  │
└──────────────┘      └──────────────┘      └──────────────┘
                                                    │
                                                    ▼
                                             ┌──────────────┐
                                             │  SQLite DB   │
                                             └──────────────┘
                                                    ▲
                                                    │
                                             ┌──────────────┐
                                             │ Email Agent  │
                                             │ (Background) │
                                             └──────────────┘
```

Enjoy using the Leave Management System!
