# MindBank - Technical Architecture

## Technology Stack

### Backend: Python + Flask
- **Framework**: Flask (minimal web framework)
- **Language**: Python 3.8+
- **Purpose**: Handle HTTP requests, business logic, data persistence, and API endpoints

### Frontend: HTML + CSS + JavaScript
- **HTML5**: Semantic markup and structure
- **CSS3**: Styling, responsive design, animations
- **Vanilla JavaScript**: DOM manipulation, real-time calculations, AJAX requests
- **No frameworks**: No React, Vue, Angular, or other JavaScript frameworks

### Data Storage
- **Local Storage**: Browser localStorage for user preferences and session data
- **File-based**: JSON files for persistent data storage (initial implementation)
- **No Database**: No SQL or NoSQL databases for MVP

## Architecture Overview

```
┌─────────────────┐    HTTP Requests    ┌─────────────────┐
│   Frontend      │◄──────────────────►│   Flask App     │
│ (HTML/CSS/JS)   │                     │   (Python)      │
├─────────────────┤                     ├─────────────────┤
│ • Dashboard     │                     │ • Route Handlers│
│ • Config Forms  │                     │ • Business Logic│
│ • Real-time UI  │                     │ • Data Models   │
│ • Calculations  │                     │ • Currency API  │
└─────────────────┘                     └─────────────────┘
         ▲                                        ▲
         │                                        │
         ▼                                        ▼
┌─────────────────┐                     ┌─────────────────┐
│ Browser Storage │                     │  JSON Files     │
│ • User Session  │                     │ • User Config   │
│ • Temp Data     │                     │ • Asset Data    │
└─────────────────┘                     └─────────────────┘
```

## File Structure

```
mindbank/
├── app.py                 # Flask application entry point
├── config.py              # Application configuration
├── requirements.txt       # Python dependencies
├── static/               # Static assets
│   ├── css/
│   │   └── styles.css    # Main stylesheet
│   ├── js/
│   │   └── app.js        # Main JavaScript application
│   └── assets/           # Images, icons
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── dashboard.html    # Main dashboard
│   └── config.html       # Configuration page
├── data/                 # Data storage
│   ├── user_config.json  # User configuration
│   └── assets.json       # Asset data
└── utils/                # Utility modules
    ├── calculations.py   # Financial calculations
    ├── currency.py       # Currency conversion
    └── data_manager.py   # Data persistence
```

## Core Components

### 1. Flask Backend (`app.py`)

```python
from flask import Flask, render_template, request, jsonify
from utils.calculations import calculate_global_position
from utils.data_manager import load_config, save_config

app = Flask(__name__)

@app.route('/')
def dashboard():
    # Render main dashboard
    
@app.route('/config')
def config():
    # Render configuration page
    
@app.route('/api/update-assets', methods=['POST'])
def update_assets():
    # Handle asset updates
    
@app.route('/api/daily-goal', methods=['POST'])
def update_daily_goal():
    # Handle daily goal percentage updates
```

### 2. Financial Calculations (`utils/calculations.py`)

```python
from datetime import datetime
import calendar

def calculate_realized_income(monthly_salary):
    """Calculate income based on days passed in month"""
    
def calculate_potential_income(monthly_salary, goal_percentage):
    """Calculate today's potential income based on goal completion"""
    
def calculate_global_position(assets, realized_income, potential_income):
    """Calculate total financial position"""
    
def convert_usd_to_eur(usd_amount, exchange_rate):
    """Convert USD to EUR"""
```

### 3. Frontend JavaScript (`static/js/app.js`)

```javascript
class MindBankApp {
    constructor() {
        this.goalSlider = document.getElementById('goal-slider');
        this.initializeEventListeners();
        this.loadDashboardData();
    }
    
    initializeEventListeners() {
        // Handle slider changes
        // Handle form submissions
        // Handle real-time updates
    }
    
    updateDailyGoal(percentage) {
        // Send AJAX request to update goal
        // Update UI in real-time
    }
    
    refreshDashboard() {
        // Fetch latest data and update display
    }
}
```

### 4. Responsive CSS (`static/css/styles.css`)

```css
/* Mobile-first responsive design */
/* CSS Grid/Flexbox for layout */
/* Custom slider styling */
/* Card-based UI components */
/* Smooth animations for real-time updates */
```

## Data Flow

### 1. Configuration Flow
1. User inputs configuration data in forms
2. JavaScript validates and sends data to Flask
3. Flask processes and saves to JSON files
4. Success/error response returned to frontend

### 2. Dashboard Flow
1. Flask loads user configuration and calculates positions
2. Template renders with initial data
3. JavaScript handles real-time goal slider updates
4. AJAX requests update calculations without page reload

### 3. Real-time Updates
1. User moves goal completion slider
2. JavaScript calculates new potential income
3. AJAX request sent to Flask backend
4. Backend recalculates global position
5. JSON response updates frontend display

## Key Technical Features

### 1. Real-time Calculations
- JavaScript handles slider movements for immediate feedback
- Debounced AJAX requests to backend for persistence
- No page reloads for better user experience

### 2. Responsive Design
- Mobile-first CSS approach
- Flexible grid layouts
- Touch-friendly slider controls

### 3. Data Persistence
- JSON file storage for simplicity
- Automatic backups of configuration
- Error handling for data corruption

### 4. Currency Conversion
- External API integration for USD/EUR rates
- Caching mechanism for rate limiting
- Fallback static rates if API unavailable

## Security Considerations

### 1. Data Privacy
- All data stored locally
- No external data transmission except currency rates
- No user authentication required for MVP

### 2. Input Validation
- Server-side validation for all inputs
- JavaScript validation for user experience
- Sanitization of user inputs

### 3. Error Handling
- Graceful degradation for API failures
- User-friendly error messages
- Logging for debugging

## Performance Optimization

### 1. Frontend
- Minified CSS and JavaScript for production
- Efficient DOM manipulation
- Debounced input handling

### 2. Backend
- Lightweight Flask configuration
- Efficient file I/O operations
- Caching for repeated calculations

## Development Workflow

### 1. Local Development
```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

### 2. File Watching
- Manual refresh during development
- No build tools or bundlers
- Direct file editing and testing

## Testing Strategy

### 1. Manual Testing
- Browser testing across devices
- Functional testing of all features
- Edge case testing (end of month, leap years)

### 2. Unit Testing
- Python unittest for calculation functions
- JavaScript testing in browser console
- Data persistence testing

## Deployment Considerations

### 1. Simple Deployment
- Single Python file execution
- Static file serving through Flask
- No complex build processes

### 2. Production Readiness
- Environment-based configuration
- Proper error logging
- Performance monitoring 