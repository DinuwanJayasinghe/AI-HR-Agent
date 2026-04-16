# Leave Management System - Frontend

A modern, Gmail-like interface for managing employee leave requests built with React.js and Tailwind CSS.

## Features

- **Dashboard**: Overview of employees, leave statistics, and quick actions
- **Employee Management**: View, add, and manage employee information and leave balances
- **Leave Requests**: Track and manage leave requests with filtering options
- **Real-time Updates**: Automatic data refresh from backend API
- **Responsive Design**: Clean, modern interface that works on all devices

## Tech Stack

- React.js 18
- Vite (Build tool)
- Tailwind CSS (Styling)
- Axios (API calls)
- Lucide React (Icons)

## Getting Started

### Prerequisites

- Node.js 16+ installed
- Backend API server running on port 5000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to:
```
http://localhost:5173
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout/
│   │   │   ├── Sidebar.jsx       # Navigation sidebar
│   │   │   └── Header.jsx        # Top header with search
│   │   ├── Dashboard/
│   │   │   └── Dashboard.jsx     # Main dashboard view
│   │   ├── Employees/
│   │   │   ├── Employees.jsx     # Employee list
│   │   │   ├── EmployeeDetails.jsx
│   │   │   └── AddEmployeeModal.jsx
│   │   └── LeaveRequests/
│   │       └── LeaveRequests.jsx # Leave requests view
│   ├── services/
│   │   └── api.js                # API integration
│   ├── App.jsx                   # Main app component
│   └── index.css                 # Global styles
├── tailwind.config.js
└── package.json
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## API Integration

The frontend connects to the backend API running on `http://localhost:5000/api`

### Endpoints Used:
- `GET /api/employees` - Fetch all employees
- `GET /api/employees/:email` - Fetch specific employee
- `POST /api/employees` - Add new employee
- `GET /api/leave-balance/:email` - Get leave balance
- `PUT /api/leave-balance/:email` - Update leave balance
- `GET /api/stats` - Get dashboard statistics
- `GET /api/leave-requests` - Get all leave requests

## Features by Section

### Dashboard
- Employee statistics overview
- Total leave days tracking
- Pending and approved requests count
- Quick action cards
- Recent employees list

### Employees
- Grid view of all employees
- Search functionality
- Leave balance cards (Vacation, Sick Leave, Personal Leave)
- Add new employees
- Edit employee leave balances
- Detailed employee view

### Leave Requests
- List of all leave requests
- Filter by status (All, Pending, Approved, Rejected)
- Status badges with color coding
- Request details (dates, type, reason)
- Action buttons for pending requests

## Styling

The application uses Tailwind CSS with a custom color palette:
- Primary: Blue shades (used throughout the interface)
- Success: Green (approved items)
- Warning: Yellow (pending items)
- Danger: Red (rejected items)

The design follows Gmail's clean, card-based interface pattern with:
- Clear visual hierarchy
- Consistent spacing and borders
- Smooth transitions and hover effects
- Responsive grid layouts
