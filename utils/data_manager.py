import json
import os
from datetime import datetime

CONFIG_FILE = 'data/user_config.json'
ASSETS_FILE = 'data/assets.json'

def ensure_data_directory():
    """Ensure the data directory exists"""
    os.makedirs('data', exist_ok=True)

def load_config():
    """Load user configuration from JSON file"""
    ensure_data_directory()
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        # Return default configuration
        default_config = {
            'monthly_salary': 0,
            'daily_goal_percentage': 0,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        save_config(default_config)
        return default_config
    except json.JSONDecodeError:
        # Handle corrupted file - create backup and return default config
        backup_file(CONFIG_FILE)
        default_config = {
            'monthly_salary': 0,
            'daily_goal_percentage': 0,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        save_config(default_config)
        return default_config

def save_config(config):
    """Save user configuration to JSON file"""
    ensure_data_directory()
    
    config['updated_at'] = datetime.now().isoformat()
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        raise Exception(f"Failed to save configuration: {str(e)}")

def load_assets():
    """Load asset data from JSON file"""
    ensure_data_directory()
    
    try:
        with open(ASSETS_FILE, 'r') as f:
            assets = json.load(f)
        return assets
    except FileNotFoundError:
        # Return default assets
        default_assets = {
            'bank_balance': 0,
            'cash_eur': 0,
            'cash_usd': 0,
            'investments': 0,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        save_assets(default_assets)
        return default_assets
    except json.JSONDecodeError:
        # Handle corrupted file - create backup and return default assets
        backup_file(ASSETS_FILE)
        default_assets = {
            'bank_balance': 0,
            'cash_eur': 0,
            'cash_usd': 0,
            'investments': 0,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        save_assets(default_assets)
        return default_assets

def save_assets(assets):
    """Save asset data to JSON file"""
    ensure_data_directory()
    
    assets['updated_at'] = datetime.now().isoformat()
    
    try:
        with open(ASSETS_FILE, 'w') as f:
            json.dump(assets, f, indent=4)
    except Exception as e:
        raise Exception(f"Failed to save assets: {str(e)}")

def backup_file(file_path):
    """Create a backup of a corrupted file"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            os.rename(file_path, backup_path)
        except:
            # If rename fails, just delete the corrupted file
            os.remove(file_path)

def validate_config(config):
    """Validate configuration data"""
    required_fields = ['monthly_salary', 'daily_goal_percentage']
    
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate data types and ranges
    if not isinstance(config['monthly_salary'], (int, float)) or config['monthly_salary'] < 0:
        raise ValueError("Monthly salary must be a positive number")
    
    if not isinstance(config['daily_goal_percentage'], (int, float)) or not 0 <= config['daily_goal_percentage'] <= 100:
        raise ValueError("Daily goal percentage must be between 0 and 100")
    
    return True

def validate_assets(assets):
    """Validate asset data"""
    required_fields = ['bank_balance', 'cash_eur', 'cash_usd', 'investments']
    
    for field in required_fields:
        if field not in assets:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate data types
    for field in required_fields:
        if not isinstance(assets[field], (int, float)):
            raise ValueError(f"{field} must be a number")
    
    return True

def get_data_summary():
    """Get a summary of all stored data"""
    try:
        config = load_config()
        assets = load_assets()
        
        return {
            'config_exists': True,
            'assets_exists': True,
            'config_last_updated': config.get('updated_at', 'Unknown'),
            'assets_last_updated': assets.get('updated_at', 'Unknown'),
            'monthly_salary_configured': config.get('monthly_salary', 0) > 0,
            'assets_configured': any(assets.get(field, 0) > 0 for field in ['bank_balance', 'cash_eur', 'cash_usd', 'investments'])
        }
    except Exception as e:
        return {
            'config_exists': False,
            'assets_exists': False,
            'error': str(e)
        } 