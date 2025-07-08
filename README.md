# MindBank - Personal Banking & Motivation App

MindBank is a personal financial tracking application that monitors liquid assets and motivates daily productivity through gamified income realization. Track your financial position and stay motivated by seeing how your daily goals directly impact your income potential.

## 🌟 Features

### Core Functionality
- **Real-time Asset Tracking**: Monitor bank accounts, physical cash (EUR/USD), and investments
- **Daily Goal Integration**: Adjust your daily goal completion (0-100%) and see instant income impact
- **Income Visualization**: Track both realized monthly income and daily potential earnings
- **Global Financial Position**: See your total wealth including assets and income projections
- **Currency Conversion**: Automatic USD to EUR conversion with live exchange rates

### Key Benefits
- **Motivation Through Visualization**: Connect daily productivity to financial growth
- **Comprehensive Asset View**: All your liquid assets in one dashboard
- **Real-time Calculations**: Instant updates as you adjust your daily goals
- **Mobile Responsive**: Works perfectly on desktop, tablet, and mobile devices
- **Data Privacy**: All financial data stored locally on your device

## 🏗️ Technology Stack

- **Backend**: Python + Flask (minimal web framework)
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript (no frameworks)
- **Data Storage**: JSON files (local file system)
- **Styling**: Custom CSS with CSS Grid/Flexbox
- **APIs**: Exchange rate integration for currency conversion

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Modern web browser (Chrome, Firefox, Safari, Edge)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/gabrielpierobon/mindbank.git
cd mindbank
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

### 5. Open Your Browser
Navigate to `http://localhost:5555` to start using MindBank!

## 💼 Usage Guide

### First-Time Setup
1. **Launch the Application**: Open `http://localhost:5555` in your browser
2. **Configure Your Profile**: Click "Set Up Your Profile" to enter your financial information
3. **Enter Monthly Salary**: Input your gross monthly salary in euros
4. **Add Asset Information**: Enter your bank balance, cash amounts, and investment values
5. **Set Daily Goal**: Use the slider to set your current daily goal completion percentage

### Daily Usage
1. **Adjust Daily Goals**: Use the slider on the dashboard to update your goal completion
2. **Monitor Global Position**: See your total financial position including potential earnings
3. **Track Monthly Progress**: View your progress through the current month
4. **Update Asset Values**: Regularly update your asset information in Settings

### Key Concepts

#### Realized Income
- Calculated as: `(Current Day / Days in Month) × Monthly Salary`
- Automatically updates based on the current date
- Represents income you've "earned" based on time passed

#### Potential Income
- Calculated as: `(Monthly Salary / Days in Month) × Goal Completion %`
- Updates in real-time as you adjust the goal slider
- Represents today's earning potential based on your productivity

#### Global Position
- Total of: `Assets + Realized Income + Potential Income`
- Your complete financial picture including projected earnings
- Updates instantly with goal adjustments

## 🎯 How It Works

### The Motivation System
MindBank connects your daily productivity to financial visualization:

1. **Set Your Monthly Salary**: This becomes your earning target
2. **Track Daily Progress**: See how much you've "earned" based on days passed
3. **Adjust Daily Goals**: Use the 0-100% slider to reflect your productivity
4. **See Instant Impact**: Watch your global position change with goal adjustments
5. **Stay Motivated**: Higher goal completion = higher financial position

### Asset Management
- **Bank Account**: Your primary liquid asset balance
- **Physical Cash (EUR)**: Euro cash you have on hand
- **Physical Cash (USD)**: US dollar cash (auto-converted to EUR)
- **Investments**: Current market value of your portfolio

## 📱 Interface Overview

### Dashboard
- **Global Position Card**: Your total financial position
- **Daily Goal Slider**: Interactive 0-100% goal completion
- **Income Breakdown**: Realized vs. potential income visualization
- **Asset Cards**: Individual asset values and totals
- **Monthly Progress**: Visual progress through current month
- **Quick Actions**: Easy access to settings and data refresh

### Settings
- **Income Configuration**: Set monthly salary and daily goals
- **Asset Management**: Update all asset values
- **Exchange Rate Info**: Current USD/EUR conversion rates
- **Summary View**: Real-time preview of your financial summary

## 🔧 Configuration

### Environment Setup
The application works out-of-the-box with default settings. All configuration is handled through the web interface.

### Data Storage
- Configuration stored in: `data/user_config.json`
- Asset data stored in: `data/assets.json`
- Exchange rates cached in: `data/exchange_rates.json`

### Customization
You can modify:
- Exchange rate update frequency (default: 1 hour cache)
- Dashboard auto-refresh interval (default: 5 minutes)
- Currency conversion sources
- Visual theme colors in `static/css/styles.css`

## 🛡️ Security & Privacy

### Data Privacy
- **Local Storage Only**: All financial data stays on your device
- **No External Transmission**: Asset and income data never leaves your computer
- **Secure by Design**: No user authentication required - your data, your device

### Exchange Rate Data
- Only exchange rate information is fetched from external APIs
- No personal or financial data is transmitted
- Graceful fallback to static rates if API unavailable

## 🌐 Browser Compatibility

### Fully Supported
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Mobile Support
- iOS Safari 14+
- Chrome Mobile 90+
- Firefox Mobile 88+

## 📊 File Structure

```
mindbank/
├── app.py                  # Flask application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── static/                # Static assets
│   ├── css/
│   │   └── styles.css     # Main stylesheet
│   ├── js/
│   │   └── app.js         # JavaScript application
│   └── assets/            # Images and icons
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── dashboard.html     # Main dashboard
│   └── config.html        # Configuration page
├── utils/                 # Utility modules
│   ├── data_manager.py    # Data persistence
│   ├── calculations.py    # Financial calculations
│   └── currency.py        # Currency conversion
├── data/                  # Data storage (auto-created)
│   ├── user_config.json   # User configuration
│   ├── assets.json        # Asset data
│   └── exchange_rates.json # Cached exchange rates
└── venv/                  # Virtual environment
```

## 🔄 Development

### Running in Development Mode
The application runs in debug mode by default during development:
```bash
python app.py
```

### Making Changes
- **Frontend**: Edit HTML templates, CSS, or JavaScript files
- **Backend**: Modify Python files in `utils/` or `app.py`
- **Styling**: Update `static/css/styles.css`
- **Features**: Add new calculations in `utils/calculations.py`

### Adding Features
1. Backend logic in appropriate `utils/` module
2. API endpoints in `app.py`
3. Frontend templates in `templates/`
4. Styling in `static/css/styles.css`
5. JavaScript interactions in `static/js/app.js`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

### Common Issues

**Application won't start:**
- Ensure Python 3.8+ is installed
- Activate virtual environment
- Install dependencies: `pip install -r requirements.txt`

**Exchange rates not updating:**
- Check internet connection
- API may have rate limits (falls back to static rates)

**Data not saving:**
- Ensure `data/` directory has write permissions
- Check browser console for JavaScript errors

### Getting Help
- Check browser console for error messages
- Verify all dependencies are installed
- Ensure virtual environment is activated

## 🎯 Roadmap

### Upcoming Features
- Historical data tracking and analytics
- Multiple currency support
- Investment portfolio integration
- Data export capabilities
- Advanced goal setting and tracking
- Mobile app version

### Performance Improvements
- Progressive loading for large datasets
- Service worker for offline functionality
- Enhanced caching mechanisms

---

**MindBank** - Track your wealth, achieve your goals. 💰

Built with ❤️ using Python + Flask + Vanilla JavaScript 