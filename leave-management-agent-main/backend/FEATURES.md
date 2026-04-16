# Frontend Features Documentation

This document describes all the features and components of the Leave Management System frontend.

## Overview

The frontend is a modern, Gmail-inspired interface built with React.js and Tailwind CSS. It provides a clean, intuitive way to manage employees and their leave balances.

## Main Components

### 1. Sidebar Navigation

**Location**: Left side of the screen (collapsible)

**Features**:
- Collapsible sidebar (click arrow to collapse/expand)
- Active tab highlighting
- Icons for each section
- Smooth transitions

**Menu Items**:
- **Dashboard**: Home view with statistics
- **Employees**: Manage employee information
- **Leave Requests**: View and process requests
- **Analytics**: Future analytics dashboard
- **Settings**: System configuration (coming soon)
- **Logout**: Sign out option

**Design**:
- Primary blue color scheme
- Active items have blue background
- Hover effects on all items
- Icons from Lucide React library

---

### 2. Header Bar

**Location**: Top of the screen (fixed)

**Features**:
- **Search Bar**: Global search for employees and requests
  - Magnifying glass icon
  - Placeholder text for guidance
  - Focus ring on click

- **Notifications Bell**:
  - Red dot indicator for new notifications
  - Click to view notifications (future feature)

- **User Profile**:
  - Admin name and email display
  - Profile avatar with initials
  - Click for user menu (future feature)

**Design**:
- White background with subtle border
- Sticky positioning (stays at top when scrolling)
- Responsive layout

---

### 3. Dashboard View

**Main Statistics Cards** (4 cards in a row):

1. **Total Employees**
   - Blue theme
   - User icon
   - Shows count of all employees
   - Growth indicator ("+2 this month")

2. **Total Leave Days**
   - Green theme
   - Calendar icon
   - Sum of all available leave days
   - Across all employees and types

3. **Pending Requests**
   - Yellow/Orange theme
   - Clock icon
   - Number of requests awaiting approval

4. **Approved Today**
   - Primary blue theme
   - Check circle icon
   - Requests approved in last 24 hours

**Employees Overview Section**:
- List of all employees with:
  - Profile avatar (first letter of name)
  - Full name
  - Email address
  - Total leave days available
- Hover effect on each row
- Scroll if list is long

**Quick Action Cards** (3 cards in a row):

1. **Add New Employee** (Blue gradient)
   - Call-to-action button
   - Opens employee creation modal

2. **Process Requests** (Green gradient)
   - Navigate to leave requests
   - Quick access to pending items

3. **Generate Report** (Purple gradient)
   - Future feature for analytics
   - Report generation functionality

---

### 4. Employees Section

**Main Features**:

**Search & Filter**:
- Search bar at top
- Real-time filtering by name or email
- Shows count of filtered results

**Employee Grid**:
- Responsive 3-column grid (adjusts for screen size)
- Each card shows:
  - Profile avatar (colored circle with initial)
  - Employee name (clickable)
  - Email address with icon
  - Three leave balance boxes:
    - **Vacation** (Blue box): Days available
    - **Sick Leave** (Green box): Days available
    - **Personal Leave** (Purple box): Days available
  - Manager email (if assigned)
- Hover effect: Shadow and border color change
- Click to view details

**Add Employee Button**:
- Top right corner
- Primary blue button
- Plus icon
- Opens modal dialog

**Empty State**:
- Shows when no employees exist
- Calendar icon (grayed)
- Helpful message
- Prompt to add first employee

---

### 5. Add Employee Modal

**Modal Features**:
- Centered overlay with backdrop
- Close button (X) at top right
- Click outside to close

**Form Sections**:

1. **Basic Information**:
   - **Full Name** (required)
     - Text input
     - Icon: User
     - Placeholder: "John Doe"

   - **Email Address** (required)
     - Email input with validation
     - Icon: Mail
     - Placeholder: "john.doe@company.com"

   - **Manager Email** (optional)
     - Email input
     - Icon: UserCog
     - Placeholder: "manager@company.com"

2. **Initial Leave Balances**:
   Three number inputs in a row:
   - **Vacation Days** (default: 15)
   - **Sick Leave Days** (default: 10)
   - **Personal Leave Days** (default: 5)
   - Each can be adjusted
   - Minimum value: 0

**Action Buttons**:
- **Cancel**: Gray button, closes modal
- **Add Employee**: Blue button, submits form

**Validation**:
- Name and Email are required
- Email format validation
- Error messages if validation fails

---

### 6. Employee Details View

**Header**:
- Back button (returns to employee list)
- Edit Balances button (blue)
- When editing: Cancel and Save buttons

**Profile Section** (Blue gradient banner):
- Large profile avatar (white circle)
- Employee name (large, bold)
- Email address with icon
- Manager email with icon
- White text on blue background

**Statistics Cards** (4 cards in a row):
1. **Total Leave Days** (Gray)
2. **Vacation** (Blue)
3. **Sick Leave** (Green)
4. **Personal Leave** (Purple)

Each shows large number and label

**Leave Balance Management**:
- Three input fields for each leave type
- **View Mode**:
  - Grayed out, read-only
  - Shows current values

- **Edit Mode** (when Edit Balances clicked):
  - Colored backgrounds (blue, green, purple)
  - Editable number inputs
  - Larger, bold font
  - Focus rings on click
  - Warning message at bottom

**Leave History** (Placeholder):
- Section for future leave history
- Currently shows "No leave history available"
- Will display past requests when implemented

---

### 7. Leave Requests Section

**Statistics Row** (4 cards):
1. **Total Requests** (Gray)
2. **Pending** (Yellow)
3. **Approved** (Green)
4. **Rejected** (Red)

Each with:
- Count number
- Colored background
- Relevant icon

**Filter Bar**:
- Filter icon
- Four button filters:
  - All (show everything)
  - Pending (yellow)
  - Approved (green)
  - Rejected (red)
- Active filter is highlighted
- Click to switch filters

**Request Cards Grid**:
Each card shows:
- **Employee Info**:
  - Avatar with initial
  - Name
  - Email

- **Status Badge**:
  - Top right corner
  - Color coded:
    - Yellow: Pending (clock icon)
    - Green: Approved (check icon)
    - Red: Rejected (X icon)

- **Request Details**:
  - Leave Type
  - Start Date
  - End Date
  - Number of Days
  - Reason (expandable)

- **Action Buttons** (only for pending):
  - Approve (green button)
  - Reject (red button)

**Empty State**:
- Shows when no requests match filter
- Calendar icon
- Contextual message based on filter
- Note about email processing

---

## Color Scheme

### Primary Colors:
- **Primary Blue**: `#0ea5e9` (buttons, links, active states)
- **Success Green**: `#10b981` (approved, success messages)
- **Warning Yellow**: `#f59e0b` (pending, warnings)
- **Danger Red**: `#ef4444` (rejected, errors)
- **Purple**: `#a855f7` (personal leave, accents)

### Neutral Colors:
- **Gray 50**: `#f9fafb` (background)
- **Gray 100**: `#f3f4f6` (hover states)
- **Gray 200**: `#e5e7eb` (borders)
- **Gray 600**: `#4b5563` (secondary text)
- **Gray 900**: `#111827` (primary text)

### Gradient Backgrounds:
- Blue gradient: Primary to darker primary
- Green gradient: Success green to darker
- Purple gradient: Purple to darker

---

## Responsive Design

### Desktop (1024px+):
- Full sidebar visible
- 3-column grids
- 4 statistics cards in a row
- Larger spacing

### Tablet (768px - 1023px):
- Sidebar can collapse
- 2-column grids
- 2 statistics cards per row
- Adjusted spacing

### Mobile (<768px):
- Collapsed sidebar (icons only)
- Single column layouts
- Stacked cards
- Touch-friendly buttons
- Smaller text sizes

---

## Interactions & Animations

### Hover Effects:
- **Cards**: Shadow increases, border color changes
- **Buttons**: Background color darkens slightly
- **Links**: Underline appears
- **Inputs**: Border color changes to blue

### Click Effects:
- **Buttons**: Slight scale down
- **Cards**: Navigate to detail view
- **Inputs**: Focus ring appears

### Transitions:
- All color changes: 200ms ease
- Sidebar collapse: 300ms ease
- Shadow changes: Smooth transition
- Loading spinner: Continuous rotation

### Loading States:
- Spinner animation (rotating circle)
- Centered on screen
- Blue primary color
- Shows during data fetching

---

## Accessibility Features

### Keyboard Navigation:
- Tab through interactive elements
- Enter to activate buttons
- Escape to close modals

### Screen Reader Support:
- Semantic HTML elements
- ARIA labels where needed
- Alt text for icons
- Proper heading hierarchy

### Visual Indicators:
- Focus rings on interactive elements
- Clear button states
- High contrast colors
- Consistent icons

---

## Future Enhancements

### Planned Features:
1. **Analytics Dashboard**:
   - Charts and graphs
   - Trends over time
   - Department breakdown

2. **Settings Panel**:
   - Email configuration
   - Policy customization
   - User preferences

3. **Notifications System**:
   - Real-time updates
   - Bell icon dropdown
   - Mark as read

4. **Search Enhancement**:
   - Global search results
   - Filter by multiple criteria
   - Advanced search options

5. **Calendar Integration**:
   - Visual calendar view
   - Drag and drop requests
   - Monthly/weekly views

6. **Export Functionality**:
   - CSV export
   - PDF reports
   - Email reports

7. **User Authentication**:
   - Login page
   - Role-based access
   - Password reset

8. **Mobile App**:
   - Native iOS/Android app
   - Push notifications
   - Offline support

---

## Technical Details

### State Management:
- React hooks (useState, useEffect)
- Local component state
- Props drilling for simple data
- Future: Context API or Redux if needed

### API Calls:
- Axios for HTTP requests
- Async/await pattern
- Error handling with try/catch
- Loading states during fetch

### Performance:
- Lazy loading of components
- Debounced search
- Memoization where needed
- Optimized re-renders

### Browser Support:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## Design Philosophy

The interface follows these principles:

1. **Clarity**: Clear labels, obvious actions
2. **Consistency**: Same patterns throughout
3. **Feedback**: Visual confirmation of actions
4. **Efficiency**: Quick access to common tasks
5. **Beauty**: Clean, modern aesthetic
6. **Accessibility**: Usable by everyone
7. **Responsiveness**: Works on all devices

---

This completes the features documentation. The interface is designed to be intuitive and user-friendly while providing all the functionality needed to manage employee leave efficiently.
