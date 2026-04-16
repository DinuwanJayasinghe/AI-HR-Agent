# Leave Management Agent

Fully automated leave management system that monitors Gmail 24/7 and processes leave requests using LangGraph and LLM reasoning.

## Architecture

```
Email Inbox → LangGraph Agent → Policy Engine → SQLite DB → Decision → Email Response
                                                    ↓
                                              HR Approval Loop
```

### Components

- **Email Reader**: IMAP-based inbox monitoring
- **LangGraph State Machine**: Orchestrates the entire workflow
- **Policy Engine**: JSON-based rule evaluation
- **SQLite Database**: Employee records and leave balances
- **Email Sender**: SMTP-based automated responses
- **HR Listener**: Monitors and processes HR approval emails

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
OPENAI_API_KEY=sk-your-key
HR_EMAIL=hr@company.com
```

### 3. Gmail App Password Setup

1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Generate App Password: https://myaccount.google.com/apppasswords
4. Use the 16-character password in `.env`

### 4. Run the Agent

```bash
python main.py
```

## How It Works

### Leave Request Flow

1. **Email Detection**: Monitors inbox for emails with "Leave" in subject
2. **Information Extraction**: LLM extracts dates, days, reason
3. **Validation**: Checks for required fields
4. **Categorization**: Classifies leave type (Vacation, Sick, etc.)
5. **Policy Check**: Evaluates against company rules
6. **Balance Check**: Verifies available leave days
7. **Decision Routing**:
   - Auto-approve if within limits
   - Auto-reject if insufficient balance
   - Send to HR if exceeds threshold
8. **HR Approval** (if needed):
   - Email sent to HR
   - Agent waits for APPROVE/REJECT reply
9. **Database Update**: Deducts days from balance
10. **Final Email**: Sends approval/rejection to employee

### HR Approval Process

When HR approval is required:
- Agent sends detailed email to HR
- HR replies with **APPROVE** or **REJECT**
- Agent automatically processes the decision
- Updates database and notifies employee

## Policy Configuration

Edit `data/policies.json` to customize rules:

```json
{
  "Vacation": { "max_days_without_hr": 5 },
  "Sick Leave": { "max_days_without_hr": 3 },
  "Maternity/Paternity": { "always_hr": true }
}
```

## Database Schema

### employees
- email (PRIMARY KEY)
- name
- manager_email

### leave_balance
- email (FOREIGN KEY)
- leave_type
- balance

## Extending the System

### Add New Leave Types

1. Update `data/policies.json`
2. Add default balance in `database.py`
3. Update categorization prompt if needed

### Add New Notification Channels

Extend `email_sender.py` to support:
- Slack webhooks
- SMS via Twilio
- Push notifications

### Add Calendar Integration

Integrate with Google Calendar API to auto-block approved leave dates.

## Frontend Interface

A modern, Gmail-like web interface built with React.js and Tailwind CSS for managing the leave system.

### Running the Frontend

1. **Install Frontend Dependencies**:
```bash
cd frontend
npm install
```

2. **Start the API Server** (from root directory):
```bash
pip install flask flask-cors
python api_server.py
```

3. **Start the Frontend** (in a new terminal):
```bash
cd frontend
npm run dev
```

4. **Access the Application**:
- Frontend: http://localhost:5173
- API: http://localhost:5000

### Frontend Features

- **Dashboard**: Overview with statistics and quick actions
- **Employee Management**: Add, view, and edit employees and their leave balances
- **Leave Requests**: View and filter all leave requests by status
- **Real-time Data**: Automatic synchronization with backend
- **Responsive Design**: Works on desktop, tablet, and mobile devices

See [frontend/README.md](frontend/README.md) for more details.

## Complete System Architecture

```
┌─────────────────┐
│   Web Browser   │ → React Frontend (Port 5173)
└─────────────────┘
         ↓
┌─────────────────┐
│   Flask API     │ ← HTTP REST API (Port 5000)
└─────────────────┘
         ↓
┌─────────────────┐
│  SQLite DB      │ ← Employee & Leave Data
└─────────────────┘
         ↑
┌─────────────────┐
│  Email Agent    │ ← Processes Gmail Leave Requests (Background)
└─────────────────┘
```

## Production Considerations

- Use proper logging instead of print statements
- Add retry logic for email operations
- Implement error notifications
- Set up monitoring/alerting
- Use database migrations for schema changes
- Add unit and integration tests
- Use PostgreSQL instead of SQLite in production
- Add authentication and authorization to the API
- Deploy frontend and backend separately with proper CORS configuration
