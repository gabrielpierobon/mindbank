# MindBank - Personal Banking & Motivation App

## Product Overview

MindBank is a personal financial tracking application designed to monitor liquid assets and motivate daily productivity through gamified income realization. The app combines traditional asset tracking with a unique feature that allows users to "earn" their daily income by completing daily goals.

## Core Concept

The application tracks your current financial position across multiple asset types and adds a motivational layer by showing potential daily earnings based on goal completion. This creates a direct connection between daily productivity and financial growth visualization.

## Key Features

### 1. Asset Tracking
- **Bank Account Balance**: Primary liquid asset tracking
- **Physical Cash (EUR)**: Metallic cash possession in Euros
- **Physical Cash (USD)**: Metallic cash in USD, automatically converted to EUR
- **Investment Portfolio**: Current value of investments and securities

### 2. Daily Income Realization System
The app calculates and displays hypothetical income in two components:

#### Component A: Realized Monthly Income
- Automatically calculates earned income based on days passed in the current month
- Formula: `(Current Day / Days in Month) × Monthly Salary`
- Example: If today is July 8th, you've "earned" 8/31 of your monthly income

#### Component B: Today's Potential Income
- Daily income potential based on goal completion percentage
- Formula: `(Monthly Salary / Days in Month) × Goal Completion %`
- Controlled by a 0-100% slider representing daily goal achievement
- Real-time adjustment as user moves the slider

### 3. Configuration Management
User-configurable settings for:
- Monthly income amount
- Bank account balance
- Physical cash amounts (EUR and USD)
- Current investment values
- Daily goals definition (initially just percentage-based)

### 4. Dashboard Display
- **Global Position**: Total financial position including all assets plus hypothetical income
- **Asset Breakdown**: Detailed view of each asset category
- **Income Visualization**: Clear separation between realized and potential daily income
- **Motivation Metrics**: Progress indicators and achievement visualization

## User Stories

### Primary User Stories
1. **As a user**, I want to see my total liquid assets in one place so I can understand my financial position
2. **As a user**, I want to track my daily productivity impact on my financial goals so I stay motivated
3. **As a user**, I want to see how my daily efforts translate to income realization so I can make better decisions about my time
4. **As a user**, I want to configure my asset values so the app reflects my actual financial situation

### Secondary User Stories
1. **As a user**, I want to see my progress through the month so I understand my earning trajectory
2. **As a user**, I want to adjust my daily goal completion so I can see real-time impact on my finances
3. **As a user**, I want to easily update my asset values so my financial picture stays current

## Success Metrics
- Daily app engagement and goal completion percentage updates
- Increased user motivation to complete daily tasks
- Accurate financial position tracking
- User retention and regular asset updates

## Technical Requirements
- Responsive web application
- Real-time calculation updates
- Secure local data storage
- Currency conversion capabilities
- Intuitive slider and form controls

## Future Enhancements (Post-MVP)
- Multiple currency support
- Investment portfolio integration
- Historical tracking and analytics
- Goal setting and tracking beyond percentage
- Export capabilities
- Mobile app version

## Success Definition
The MVP is successful if users can:
1. Configure their basic financial information
2. See their total financial position accurately
3. Use the daily goal slider to visualize income impact
4. Feel motivated to increase their daily productivity based on financial visualization 