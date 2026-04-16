# HR Face Recognition System

A comprehensive HR management system with face recognition capabilities for attendance tracking. This project consists of a FastAPI backend for face recognition and employee management, and a Flutter frontend for cross-platform mobile and desktop support.

## Features

- **Face Recognition Attendance**: Real-time face recognition for employee check-in/check-out
- **Employee Management**: Complete CRUD operations for employee records
- **Attendance Tracking**: Automated attendance logging with location tracking
- **Leave Management**: Employee leave requests and approval system
- **Payroll Management**: Salary calculations and payroll processing
- **Geolocation**: Location-based attendance verification
- **Scheduled Tasks**: Automated daily attendance marking using APScheduler

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Relational database for data persistence
- **SQLAlchemy**: SQL toolkit and ORM
- **face-recognition**: Face detection and recognition library
- **OpenCV**: Computer vision and image processing
- **APScheduler**: Background task scheduling
- **Uvicorn**: ASGI server

### Frontend
- **Flutter**: Cross-platform UI framework (iOS, Android, Web, Desktop)
- **Dart SDK**: Version 3.9.2+
- **Camera**: Native camera access
- **Geolocator**: GPS location services
- **HTTP**: RESTful API communication

## Prerequisites

### Backend Requirements
- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)
- CMake (for dlib/face-recognition compilation)
- Visual Studio Build Tools (Windows) or build-essential (Linux)

### Frontend Requirements
- Flutter SDK 3.9.2 or higher
- Dart SDK (included with Flutter)
- Android Studio (for Android development)
- Xcode (for iOS/macOS development, macOS only)
- Chrome (for web development)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd facerec
```

### 2. Backend Setup

#### Step 1: Create a Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

#### Step 2: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: Installing `face-recognition` may take some time as it compiles dlib. Make sure you have CMake and appropriate build tools installed.

#### Step 3: Setup PostgreSQL Database

1. Install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)

2. Create a new database:
```sql
CREATE DATABASE face_rec;
```

3. Update database credentials in `backend/core/config.py`:
```python
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "your_password"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DB = "face_rec"
```

#### Step 4: Initialize Database

The database tables will be created automatically when you first run the application. Optionally, you can run the SQL migration:

```bash
# If you have additional SQL scripts
psql -U postgres -d face_rec -f add_location_columns.sql
```

### 3. Frontend Setup

#### Step 1: Install Flutter

Follow the official Flutter installation guide for your operating system:
- [Flutter Installation Guide](https://docs.flutter.dev/get-started/install)

Verify Flutter installation:
```bash
flutter doctor
```

#### Step 2: Navigate to Frontend Directory

```bash
cd ../frontend
```

#### Step 3: Install Dependencies

```bash
flutter pub get
```

#### Step 4: Configure API Endpoint

Update the backend API URL in your Flutter app to match your backend server address. Look for API configuration files in the `lib` directory and update the base URL:

```dart
// Example: lib/config/api_config.dart or similar
const String BASE_URL = "http://localhost:8000";
// For Android emulator: "http://10.0.2.2:8000"
// For physical device: "http://YOUR_IP:8000"
```

## Running the Application

### 1. Start the Backend Server

```bash
# Make sure you're in the backend directory and virtual environment is activated
cd backend
python main.py
```

The backend server will start on `http://0.0.0.0:8000`

**API Documentation** will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 2. Start the Frontend Application

#### For Android:
```bash
cd frontend
flutter run
```

#### For iOS (macOS only):
```bash
cd frontend
flutter run -d ios
```

#### For Web:
```bash
cd frontend
flutter run -d chrome
```

#### For Windows:
```bash
cd frontend
flutter run -d windows
```

#### For Linux:
```bash
cd frontend
flutter run -d linux
```

#### For macOS:
```bash
cd frontend
flutter run -d macos
```

## Project Structure

```
facerec/
├── backend/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── app.py              # FastAPI application setup
│   │   ├── config.py           # Configuration settings
│   │   ├── database.py         # Database connection
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── crud.py             # Database operations
│   │   ├── face_recog.py       # Face recognition logic
│   │   ├── recognize.py        # Face recognition utilities
│   │   ├── scheduler.py        # APScheduler tasks
│   │   └── utils.py            # Helper functions
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── employee.py         # Employee endpoints
│   │   ├── attendance.py       # Attendance endpoints
│   │   ├── leave.py            # Leave management endpoints
│   │   └── payroll.py          # Payroll endpoints
│   ├── main.py                 # Application entry point
│   ├── requirements.txt        # Python dependencies
│   └── add_location_columns.sql
│
└── frontend/
    ├── lib/                    # Flutter source code
    ├── android/                # Android specific files
    ├── ios/                    # iOS specific files
    ├── web/                    # Web specific files
    ├── windows/                # Windows specific files
    ├── linux/                  # Linux specific files
    ├── macos/                  # macOS specific files
    └── pubspec.yaml            # Flutter dependencies
```

## Configuration

### Backend Configuration (`backend/core/config.py`)

- **DATABASE_URL**: PostgreSQL connection string
- **TIMEZONE**: Application timezone (default: Asia/Colombo)
- **MODEL**: Face recognition model (default: "hog")
- **TOLERANCE**: Face recognition tolerance (default: 0.45)
- **INACTIVITY_MINUTES**: Inactivity timeout (default: 10)

### Environment Variables (Optional)

You can set environment variables instead of hardcoding in config.py:

```bash
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=your_password
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=face_rec
```

## API Endpoints

### Employee Management
- `POST /employees/` - Create new employee
- `GET /employees/` - List all employees
- `GET /employees/{id}` - Get employee details
- `PUT /employees/{id}` - Update employee
- `DELETE /employees/{id}` - Delete employee

### Attendance
- `POST /attendance/checkin` - Check in with face recognition
- `POST /attendance/checkout` - Check out
- `GET /attendance/` - Get attendance records

### Leave Management
- `POST /leave/` - Submit leave request
- `GET /leave/` - Get leave requests
- `PUT /leave/{id}` - Update leave status

### Payroll
- `POST /payroll/` - Process payroll
- `GET /payroll/` - Get payroll records

## Troubleshooting

### Backend Issues

**Issue**: `face-recognition` installation fails
- **Solution**: Install CMake and Visual Studio Build Tools (Windows) or build-essential (Linux)
  ```bash
  # Windows: Download from https://visualstudio.microsoft.com/downloads/
  # Ubuntu/Debian:
  sudo apt-get install build-essential cmake
  # macOS:
  brew install cmake
  ```

**Issue**: Database connection error
- **Solution**: Verify PostgreSQL is running and credentials in `config.py` are correct
  ```bash
  # Check PostgreSQL status
  # Windows:
  pg_ctl status
  # Linux:
  sudo systemctl status postgresql
  ```

**Issue**: Port 8000 already in use
- **Solution**: Change port in `main.py` or kill the process using port 8000

### Frontend Issues

**Issue**: `flutter doctor` shows errors
- **Solution**: Follow the instructions provided by `flutter doctor` to resolve platform-specific issues

**Issue**: Cannot connect to backend from Android emulator
- **Solution**: Use `http://10.0.2.2:8000` instead of `localhost:8000`

**Issue**: Cannot connect to backend from physical device
- **Solution**:
  1. Ensure device and computer are on the same network
  2. Use your computer's IP address (e.g., `http://192.168.1.100:8000`)
  3. Update firewall settings to allow connections on port 8000

**Issue**: Camera permission denied
- **Solution**:
  - **Android**: Add permissions in `android/app/src/main/AndroidManifest.xml`
  - **iOS**: Add usage description in `ios/Runner/Info.plist`

## Development

### Running Tests

#### Backend Tests
```bash
cd backend
pytest
```

#### Frontend Tests
```bash
cd frontend
flutter test
```

### Building for Production

#### Backend
```bash
# Create requirements.txt with pinned versions
pip freeze > requirements.txt

# Use gunicorn for production
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.core.app:app
```

#### Frontend

**Android APK:**
```bash
flutter build apk --release
```

**iOS IPA:**
```bash
flutter build ipa --release
```

**Web:**
```bash
flutter build web --release
```

**Windows:**
```bash
flutter build windows --release
```

## Security Considerations

1. **Change default credentials**: Update PostgreSQL password in production
2. **Use environment variables**: Don't commit sensitive data to version control
3. **Enable HTTPS**: Use SSL/TLS certificates in production
4. **Implement authentication**: Add JWT or OAuth2 for API security
5. **Validate inputs**: Ensure all API inputs are properly validated
6. **Secure face data**: Encrypt face encodings in the database

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Contact the development team

## Acknowledgments

- FastAPI for the excellent web framework
- Face Recognition library for making face recognition accessible
- Flutter team for the amazing cross-platform framework
- PostgreSQL for reliable database management
