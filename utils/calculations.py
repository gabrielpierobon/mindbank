from datetime import datetime
import calendar
from utils.currency import get_exchange_rate

def calculate_realized_income(monthly_salary):
    """
    Calculate income based on days passed in the current month
    Formula: (Current Day / Days in Month) × Monthly Salary
    """
    if not monthly_salary or monthly_salary <= 0:
        return 0
    
    try:
        now = datetime.now()
        current_day = now.day
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        
        realized_income = (current_day / days_in_month) * monthly_salary
        return round(realized_income, 2)
    
    except Exception as e:
        return 0

def calculate_potential_income(monthly_salary, goal_percentage):
    """
    Calculate today's potential income based on goal completion
    Formula: (Monthly Salary / Days in Month) × Goal Completion %
    """
    if not monthly_salary or monthly_salary <= 0 or goal_percentage < 0:
        return 0
    
    try:
        now = datetime.now()
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        
        daily_income = monthly_salary / days_in_month
        potential_income = daily_income * (goal_percentage / 100)
        
        return round(potential_income, 2)
    
    except Exception as e:
        return 0

def calculate_total_assets(assets):
    """Calculate total assets value in EUR"""
    try:
        # Get USD to EUR exchange rate
        exchange_rate = get_exchange_rate()
        
        # Convert USD cash to EUR
        cash_usd_in_eur = assets.get('cash_usd', 0) * exchange_rate
        
        total_assets = (
            assets.get('bank_balance', 0) +
            assets.get('cash_eur', 0) +
            cash_usd_in_eur +
            assets.get('investments', 0)
        )
        
        return round(total_assets, 2)
    
    except Exception as e:
        # Fallback calculation without currency conversion
        total_assets = (
            assets.get('bank_balance', 0) +
            assets.get('cash_eur', 0) +
            assets.get('cash_usd', 0) +  # Treat USD as EUR in fallback
            assets.get('investments', 0)
        )
        return round(total_assets, 2)

def calculate_global_position(assets, realized_income, potential_income):
    """
    Calculate total financial position including assets and income
    """
    try:
        total_assets = calculate_total_assets(assets)
        global_position = total_assets + realized_income + potential_income
        
        return round(global_position, 2)
    
    except Exception as e:
        return 0

def get_asset_breakdown(assets):
    """Get detailed breakdown of assets with EUR conversion"""
    try:
        exchange_rate = get_exchange_rate()
        
        breakdown = {
            'bank_balance': {
                'value': assets.get('bank_balance', 0),
                'currency': 'EUR',
                'value_eur': assets.get('bank_balance', 0)
            },
            'cash_eur': {
                'value': assets.get('cash_eur', 0),
                'currency': 'EUR',
                'value_eur': assets.get('cash_eur', 0)
            },
            'cash_usd': {
                'value': assets.get('cash_usd', 0),
                'currency': 'USD',
                'value_eur': round(assets.get('cash_usd', 0) * exchange_rate, 2),
                'exchange_rate': exchange_rate
            },
            'investments': {
                'value': assets.get('investments', 0),
                'currency': 'EUR',
                'value_eur': assets.get('investments', 0)
            }
        }
        
        # Calculate total
        total_eur = sum(item['value_eur'] for item in breakdown.values())
        breakdown['total'] = {
            'value_eur': round(total_eur, 2),
            'currency': 'EUR'
        }
        
        return breakdown
    
    except Exception as e:
        # Fallback breakdown
        return {
            'bank_balance': {'value': assets.get('bank_balance', 0), 'currency': 'EUR', 'value_eur': assets.get('bank_balance', 0)},
            'cash_eur': {'value': assets.get('cash_eur', 0), 'currency': 'EUR', 'value_eur': assets.get('cash_eur', 0)},
            'cash_usd': {'value': assets.get('cash_usd', 0), 'currency': 'USD', 'value_eur': assets.get('cash_usd', 0)},
            'investments': {'value': assets.get('investments', 0), 'currency': 'EUR', 'value_eur': assets.get('investments', 0)},
            'total': {'value_eur': sum(assets.get(key, 0) for key in ['bank_balance', 'cash_eur', 'cash_usd', 'investments']), 'currency': 'EUR'}
        }

def get_income_breakdown(monthly_salary, goal_percentage):
    """Get detailed breakdown of income components"""
    try:
        now = datetime.now()
        current_day = now.day
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        
        realized_income = calculate_realized_income(monthly_salary)
        potential_income = calculate_potential_income(monthly_salary, goal_percentage)
        
        # Calculate remaining potential for the month
        remaining_days = days_in_month - current_day
        daily_income = monthly_salary / days_in_month if monthly_salary > 0 else 0
        remaining_potential = remaining_days * daily_income
        
        breakdown = {
            'monthly_salary': monthly_salary,
            'days_in_month': days_in_month,
            'current_day': current_day,
            'remaining_days': remaining_days,
            'daily_income': round(daily_income, 2),
            'realized_income': realized_income,
            'potential_income': potential_income,
            'remaining_potential': round(remaining_potential, 2),
            'total_earned_today': round(realized_income + potential_income, 2),
            'progress_percentage': round((current_day / days_in_month) * 100, 1)
        }
        
        return breakdown
    
    except Exception as e:
        return {
            'monthly_salary': monthly_salary or 0,
            'days_in_month': 30,
            'current_day': 1,
            'remaining_days': 29,
            'daily_income': 0,
            'realized_income': 0,
            'potential_income': 0,
            'remaining_potential': 0,
            'total_earned_today': 0,
            'progress_percentage': 0
        }

def calculate_monthly_progress():
    """Calculate progress through the current month"""
    try:
        now = datetime.now()
        current_day = now.day
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        
        progress_percentage = (current_day / days_in_month) * 100
        
        return {
            'current_day': current_day,
            'days_in_month': days_in_month,
            'progress_percentage': round(progress_percentage, 1),
            'remaining_days': days_in_month - current_day,
            'month_name': now.strftime('%B'),
            'year': now.year
        }
    
    except Exception as e:
        return {
            'current_day': 1,
            'days_in_month': 30,
            'progress_percentage': 0,
            'remaining_days': 29,
            'month_name': 'Unknown',
            'year': datetime.now().year
        } 