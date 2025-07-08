"""
Pytest configuration and fixtures for MindBank application tests
"""

import pytest
import tempfile
import shutil
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add the project root to the path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app
from utils.data_manager import CONFIG_FILE, ASSETS_FILE
from utils.currency import CACHE_FILE


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data files"""
    temp_dir = tempfile.mkdtemp()
    
    # Override the data file paths to use temp directory
    original_config_file = CONFIG_FILE
    original_assets_file = ASSETS_FILE
    original_cache_file = CACHE_FILE
    
    # Patch the file paths
    import utils.data_manager as dm
    import utils.currency as curr
    
    dm.CONFIG_FILE = os.path.join(temp_dir, 'user_config.json')
    dm.ASSETS_FILE = os.path.join(temp_dir, 'assets.json')
    curr.CACHE_FILE = os.path.join(temp_dir, 'exchange_rates.json')
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Restore original paths
    dm.CONFIG_FILE = original_config_file
    dm.ASSETS_FILE = original_assets_file
    curr.CACHE_FILE = original_cache_file


@pytest.fixture
def sample_config():
    """Sample user configuration data"""
    return {
        'monthly_salary': 3000.0,
        'daily_goal_percentage': 75.0,
        'created_at': '2024-01-01T00:00:00',
        'updated_at': '2024-01-15T12:00:00'
    }


@pytest.fixture
def sample_assets():
    """Sample asset data"""
    return {
        'bank_balance': 5000.0,
        'cash_eur': 200.0,
        'cash_usd': 100.0,
        'investments': 10000.0,
        'created_at': '2024-01-01T00:00:00',
        'updated_at': '2024-01-15T12:00:00'
    }


@pytest.fixture
def sample_exchange_rate():
    """Sample exchange rate data"""
    return {
        'rate': 0.8542,
        'timestamp': datetime.now().isoformat(),
        'source': 'api'
    }


@pytest.fixture
def mock_exchange_api():
    """Mock the exchange rate API response"""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'rates': {
                'EUR': 0.8542
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def populated_data_files(temp_data_dir, sample_config, sample_assets):
    """Create populated test data files"""
    # Create config file
    config_path = os.path.join(temp_data_dir, 'user_config.json')
    with open(config_path, 'w') as f:
        json.dump(sample_config, f, indent=4)
    
    # Create assets file
    assets_path = os.path.join(temp_data_dir, 'assets.json')
    with open(assets_path, 'w') as f:
        json.dump(sample_assets, f, indent=4)
    
    return {
        'config_path': config_path,
        'assets_path': assets_path,
        'temp_dir': temp_data_dir
    }


@pytest.fixture
def frozen_time():
    """Freeze time to a specific date for consistent testing"""
    frozen_date = datetime(2024, 7, 15, 12, 0, 0)  # July 15th, 2024, midday
    
    with patch('utils.calculations.datetime') as mock_datetime:
        mock_datetime.now.return_value = frozen_date
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        yield frozen_date


@pytest.fixture
def api_test_data():
    """Test data for API endpoint testing"""
    return {
        'valid_config': {
            'monthly_salary': 4000.0,
            'daily_goal_percentage': 80.0
        },
        'invalid_config': {
            'monthly_salary': -1000.0,  # Invalid negative salary
            'daily_goal_percentage': 150.0  # Invalid percentage > 100
        },
        'valid_assets': {
            'bank_balance': 2500.0,
            'cash_eur': 150.0,
            'cash_usd': 200.0,
            'investments': 8000.0
        },
        'invalid_assets': {
            'bank_balance': 'not_a_number',
            'cash_eur': 100.0,
            'cash_usd': 50.0,
            'investments': 5000.0
        },
        'valid_goal_update': {
            'goal_percentage': 90.0
        },
        'invalid_goal_update': {
            'goal_percentage': 120.0  # Invalid percentage > 100
        }
    }


@pytest.fixture
def mock_calendar():
    """Mock calendar module for consistent testing"""
    with patch('utils.calculations.calendar') as mock_cal:
        # Mock July 2024 has 31 days
        mock_cal.monthrange.return_value = (0, 31)  # (weekday, days_in_month)
        yield mock_cal


@pytest.fixture(autouse=True)
def reset_modules():
    """Reset module state before each test"""
    # Clear any cached data in modules
    import utils.data_manager as dm
    import utils.currency as curr
    
    # Reset any module-level caches if they exist
    if hasattr(dm, '_config_cache'):
        dm._config_cache = None
    if hasattr(dm, '_assets_cache'):
        dm._assets_cache = None
    if hasattr(curr, '_rate_cache'):
        curr._rate_cache = None


@pytest.fixture
def error_conditions():
    """Test data for error condition testing"""
    return {
        'corrupted_json': '{"invalid": json content',
        'missing_fields_config': {
            'monthly_salary': 3000.0
            # Missing daily_goal_percentage
        },
        'missing_fields_assets': {
            'bank_balance': 5000.0,
            'cash_eur': 200.0
            # Missing cash_usd and investments
        },
        'network_error': Exception("Network connection failed"),
        'api_error': {
            'error': 'Rate limit exceeded'
        }
    } 