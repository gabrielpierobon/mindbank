"""
Unit tests for utils.data_manager module (simplified)
Tests the actual functions as they exist in the codebase
"""

import pytest
import json
import os
from unittest.mock import patch, mock_open

from utils.data_manager import (
    load_config, save_config, load_assets, save_assets,
    validate_config, validate_assets, get_data_summary
)


class TestConfigOperations:
    """Test configuration file operations"""
    
    def test_load_config_basic(self, temp_data_dir):
        """Test loading configuration"""
        # Create a config file
        config_data = {
            'monthly_salary': 3000.0,
            'daily_goal_percentage': 75.0
        }
        
        config_path = os.path.join(temp_data_dir, 'user_config.json')
        with open(config_path, 'w') as f:
            json.dump(config_data, f)
        
        # Test loading
        loaded_config = load_config()
        
        assert loaded_config['monthly_salary'] == 3000.0
        assert loaded_config['daily_goal_percentage'] == 75.0
    
    def test_save_config_basic(self, temp_data_dir):
        """Test saving configuration"""
        config_data = {
            'monthly_salary': 4000.0,
            'daily_goal_percentage': 80.0
        }
        
        save_config(config_data)
        
        # Verify file was created
        config_path = os.path.join(temp_data_dir, 'user_config.json')
        assert os.path.exists(config_path)
        
        # Verify content
        with open(config_path, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data['monthly_salary'] == 4000.0
        assert saved_data['daily_goal_percentage'] == 80.0


class TestAssetOperations:
    """Test asset file operations"""
    
    def test_load_assets_basic(self, temp_data_dir):
        """Test loading assets"""
        assets_data = {
            'bank_balance': 5000.0,
            'cash_eur': 200.0,
            'cash_usd': 100.0,
            'investments': 10000.0
        }
        
        assets_path = os.path.join(temp_data_dir, 'assets.json')
        with open(assets_path, 'w') as f:
            json.dump(assets_data, f)
        
        loaded_assets = load_assets()
        
        assert loaded_assets['bank_balance'] == 5000.0
        assert loaded_assets['cash_eur'] == 200.0
        assert loaded_assets['investments'] == 10000.0
    
    def test_save_assets_basic(self, temp_data_dir):
        """Test saving assets"""
        assets_data = {
            'bank_balance': 7000.0,
            'cash_eur': 300.0,
            'cash_usd': 150.0,
            'investments': 12000.0
        }
        
        save_assets(assets_data)
        
        # Verify file was created
        assets_path = os.path.join(temp_data_dir, 'assets.json')
        assert os.path.exists(assets_path)
        
        # Verify content
        with open(assets_path, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data['bank_balance'] == 7000.0
        assert saved_data['investments'] == 12000.0


class TestValidation:
    """Test validation functions"""
    
    def test_validate_config_valid(self):
        """Test validation with valid config"""
        valid_config = {
            'monthly_salary': 3000.0,
            'daily_goal_percentage': 75.0
        }
        
        result = validate_config(valid_config)
        assert result is True
    
    def test_validate_config_invalid_salary(self):
        """Test validation with invalid salary"""
        invalid_config = {
            'monthly_salary': -1000.0,  # Negative
            'daily_goal_percentage': 75.0
        }
        
        with pytest.raises(ValueError):
            validate_config(invalid_config)
    
    def test_validate_assets_valid(self):
        """Test validation with valid assets"""
        valid_assets = {
            'bank_balance': 5000.0,
            'cash_eur': 200.0,
            'cash_usd': 100.0,
            'investments': 10000.0
        }
        
        result = validate_assets(valid_assets)
        assert result is True
    
    def test_validate_assets_invalid_type(self):
        """Test validation with invalid asset type"""
        invalid_assets = {
            'bank_balance': 'not_a_number',  # Should be float
            'cash_eur': 200.0,
            'cash_usd': 100.0,
            'investments': 10000.0
        }
        
        with pytest.raises(ValueError):
            validate_assets(invalid_assets)


class TestDataSummary:
    """Test data summary function"""
    
    def test_get_data_summary_basic(self, temp_data_dir):
        """Test getting data summary"""
        # Create some data files first
        config_data = {'monthly_salary': 3000.0, 'daily_goal_percentage': 75.0}
        assets_data = {'bank_balance': 5000.0, 'cash_eur': 200.0, 'cash_usd': 100.0, 'investments': 10000.0}
        
        save_config(config_data)
        save_assets(assets_data)
        
        summary = get_data_summary()
        
        assert 'config_exists' in summary
        assert 'assets_exists' in summary
        assert 'monthly_salary_configured' in summary
        assert 'assets_configured' in summary


class TestErrorHandling:
    """Test error handling"""
    
    def test_load_config_file_not_found(self, temp_data_dir):
        """Test loading config when file doesn't exist"""
        # Should return default config or handle gracefully
        config = load_config()
        assert isinstance(config, dict)
    
    def test_load_assets_file_not_found(self, temp_data_dir):
        """Test loading assets when file doesn't exist"""
        # Should return default assets or handle gracefully  
        assets = load_assets()
        assert isinstance(assets, dict)
    
    def test_save_config_with_file_error(self, temp_data_dir):
        """Test save config with file write error"""
        config_data = {'monthly_salary': 3000.0, 'daily_goal_percentage': 75.0}
        
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            # Should handle error gracefully
            with pytest.raises(Exception):
                save_config(config_data) 