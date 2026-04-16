# HR Agent Frontend

A modern, AI-powered HR automation dashboard built with React, Vite, and Tailwind CSS. This frontend connects to the HR Agent backend to provide CV screening, candidate management, and AI-assisted recruitment workflows.

![HR Agent Dashboard](https://img.shields.io/badge/React-18-blue) ![Vite](https://img.shields.io/badge/Vite-5-purple) ![Tailwind](https://img.shields.io/badge/Tailwind-3-cyan)

## ✨ Features

- **📊 Dashboard**: Real-time CV statistics and analytics
- **📝 CV Review**: Analyze and rank candidates with ATS scoring
- **📥 Download CVs**: Automated CV collection from Gmail
- **🤖 AI Assistant**: Natural language chat interface for HR tasks
- **📱 Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **🎨 Dark Theme**: Professional dark green aesthetic inspired by modern fintech apps

## 🛠 Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Lucide React** - Icon library
- **Framer Motion** - Animation library
- **Recharts** - Charting library
- **date-fns** - Date formatting

## 📋 Prerequisites

- Node.js 16.x or higher
- npm or yarn package manager
- HR Agent backend running on `http://127.0.0.1:8000`

## 🚀 Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**

   The `.env` file is already created with default settings:
   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8000
   ```

   Update this if your backend runs on a different URL.

## 💻 Development

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## 🏗 Building for Production

Create an optimized production build:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

## 📁 Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable React components
│   │   ├── ui/         # UI primitives (Button, Card, Input, etc.)
│   │   └── layout/     # Layout components (Sidebar, Header, etc.)
│   ├── pages/          # Page components
│   │   ├── Dashboard.jsx
│   │   ├── CVReview.jsx
│   │   ├── DownloadCVs.jsx
│   │   └── Chat.jsx
│   ├── services/       # API service layer
│   │   └── api.js
│   ├── utils/          # Helper functions and constants
│   │   ├── formatters.js
│   │   └── constants.js
│   ├── App.jsx         # Main application component
│   ├── index.css       # Global styles with Tailwind
│   └── main.jsx        # Application entry point
├── .env                # Environment variables
├── tailwind.config.js  # Tailwind CSS configuration
├── vite.config.js      # Vite configuration
└── package.json        # Dependencies and scripts
```

## 📄 Pages

### Dashboard (`/`)
- Overview of CV statistics
- Quick action cards
- Recent activity feed
- Top candidates list

### CV Review (`/cv-review`)
- Analyze CVs from local collection
- View ATS scores and rankings
- Filter and search candidates
- View detailed candidate profiles with:
  - Keywords and skills
  - Strengths
  - Areas for improvement
  - Overall assessment

### Download CVs (`/download`)
- Download CVs from Gmail by date range
- Filter by job position
- Optional job description for better matching
- Automatic analysis and ranking
- View download summary and top candidates

### AI Assistant (`/chat`)
- Natural language chat interface
- Ask questions about candidates
- Execute HR automation tasks
- Suggested prompts for common tasks
- Real-time streaming responses

## 🔌 API Integration

The frontend communicates with the backend through the API service layer ([src/services/api.js](src/services/api.js)):

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/review-cvs` | Review CVs from Gmail or Drive |
| POST | `/api/download-cvs-by-date` | Download CVs by date range |
| POST | `/api/chat` | Chat with AI agent |
| POST | `/api/chat/stream` | Streaming chat responses |

### Example API Usage

```javascript
import { apiService } from './services/api';

// Download CVs by date range
const result = await apiService.downloadCVsByDate({
  daysBack: 7,
  jobPosition: 'Software Engineer',
  jobDescription: 'Looking for full-stack developer with React and Python experience',
  analyze: true,
});

// Analyze existing CVs
const analysis = await apiService.reviewCVs({
  jobDescription: 'Senior Full Stack Developer role',
  useDrive: false,
  folderId: '',
});

// Chat with AI assistant
const response = await apiService.chat({
  message: 'Show me all CVs received in the last 3 days',
  conversationHistory: [],
});

// Streaming chat
await apiService.chatStream(
  { message: 'Analyze candidates for backend position' },
  (data) => console.log('Received:', data),
  (error) => console.error('Error:', error)
);
```

## 🎨 Styling & Design

The application uses a custom dark theme with Tailwind CSS, inspired by the provided design image:

### Color Palette
- **Primary Green**: `#00a862` to `#00643e`
- **Dark Background**: `#0a1f1c` to `#00201a`
- **Accent Cyan**: `#00d9b5`
- **Accent Emerald**: `#34d399`

### Typography
- **Body**: Inter font family
- **Headings**: Manrope font family

### Custom Tailwind Classes

Defined in [src/index.css](src/index.css):

- `.glass` - Glass morphism effect with backdrop blur
- `.gradient-text` - Gradient text from primary to cyan
- `.card` - Card component with dark background and borders
- `.card-hover` - Interactive hover effects for cards
- `.btn-primary` - Primary button with gradient background
- `.btn-secondary` - Secondary button with dark styling
- `.btn-outline` - Outline button with primary border
- `.badge-success` - Success badge (green)
- `.badge-warning` - Warning badge (yellow)
- `.badge-error` - Error badge (red)

## 🔧 Customization

### Changing Colors

Edit [tailwind.config.js](tailwind.config.js):

```javascript
colors: {
  primary: {
    500: '#00a862', // Your primary color
    600: '#008650',
    700: '#00643e',
  },
}
```

### Adding New Pages

1. Create component in `src/pages/YourPage.jsx`
2. Add route in `src/App.jsx`:
   ```jsx
   <Route path="your-route" element={<YourPage />} />
   ```
3. Add navigation in `src/components/layout/Sidebar.jsx`:
   ```jsx
   { name: 'Your Page', path: '/your-route', icon: YourIcon }
   ```

### Modifying API Base URL

Update [.env](.env):

```env
VITE_API_BASE_URL=https://your-backend-url.com
```

## 🐛 Troubleshooting

### Backend Connection Issues

If you see "Failed to connect to backend":

1. ✅ Ensure the backend is running: `cd backend && python main.py`
2. ✅ Check backend is accessible at `http://127.0.0.1:8000/health`
3. ✅ Verify CORS is enabled in backend
4. ✅ Confirm `VITE_API_BASE_URL` in `.env`

### Build Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

### Tailwind Styles Not Applied

1. Check `tailwind.config.js` content paths
2. Verify `@tailwind` directives in `src/index.css`
3. Restart dev server

### Network Error in Chat

The chat page tries streaming first, then falls back to regular API if streaming fails. If both fail:
- Check backend logs
- Verify `/api/chat` endpoint is working
- Test with Postman/curl

## 🌐 Browser Support

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari 14+
- ✅ iOS Safari
- ✅ Chrome Android

## 📸 Screenshots

### Dashboard
Modern overview with statistics, quick actions, and recent activity.

### CV Review
Advanced filtering, ATS scoring, and detailed candidate profiles.

### Download CVs
Automated Gmail integration with customizable date ranges and job filters.

### AI Assistant
Intelligent chat interface with suggested prompts and real-time responses.

## 🚀 Quick Start Guide

1. **Start Backend:**
   ```bash
   cd backend
   python main.py
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Open Browser:**
   Navigate to `http://localhost:5173`

4. **Test the App:**
   - Click "Analyze CVs" on CV Review page
   - Try downloading CVs from Gmail
   - Chat with the AI assistant

## 📦 Dependencies

### Core
- `react` - ^18.3.1
- `react-dom` - ^18.3.1
- `react-router-dom` - ^7.1.1

### HTTP & Data
- `axios` - ^1.7.9
- `date-fns` - ^4.1.0

### UI & Styling
- `tailwindcss` - ^3.4.17
- `lucide-react` - ^0.469.0
- `framer-motion` - ^11.15.0
- `recharts` - ^2.15.0

### Build Tools
- `vite` - ^6.0.5
- `@vitejs/plugin-react` - ^4.3.4

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly (all pages and API calls)
4. Ensure responsive design works
5. Submit a pull request

## 📄 License

This project is part of the HR Agent automation system.

## 🙏 Acknowledgments

- Design inspired by modern fintech applications
- Icons by [Lucide](https://lucide.dev/)
- Built with [React](https://react.dev/) and [Tailwind CSS](https://tailwindcss.com/)
- Powered by [OpenAI GPT-4](https://openai.com/) and [Google Gemini](https://deepmind.google/technologies/gemini/)

## 📞 Support

For issues:
1. Check backend is running and accessible
2. Review browser console for errors
3. Check backend logs in terminal
4. Verify all environment variables are set

---

**Built with ❤️ for modern HR automation**
