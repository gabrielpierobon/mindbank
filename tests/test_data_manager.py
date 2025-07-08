"""
Unit tests for utils.data_manager module
Tests data persistence, validation, and error handling
"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, mock_open
from datetime import datetime

from utils.data_manager import (
    load_config, save_config, load_assets, save_assets,
    validate_config, validate_assets, get_data_summary,
    backup_file, ensure_data_directory
)


class TestDataManagerCore:
    """Test core data manager functionality"""
    
    def test_ensure_data_directory(self, temp_data_dir):
        """Test that data directory creation works"""
        new_dir = os.path.join(temp_data_dir, 'new_data')
        
        # Patch the data directory constant
        with patch('utils.data_manager.os.makedirs') as mock_makedirs:
            ensure_data_directory()
            mock_makedirs.assert_called_once_with('data', exist_ok=True)


class TestConfigOperations:
    """Test configuration file operations"""
    
    def test_load_config_existing_file(self, temp_data_dir, sample_config):
        """Test loading existing configuration file"""
        # Create config file
        config_path = os.path.join(temp_data_dir, 'user_config.json')
        with open(config_path, 'w') as f:
            json.dump(sample_config, f)
        
        # Load config
        loaded_config = load_config()
        
        assert loaded_config['monthly_salary'] == sample_config['monthly_salary']
        assert loaded_config['daily_goal_percentage'] == sample_config['daily_goal_percentage']
    
    def test_load_config_missing_file(self, temp_data_dir):
        """Test loading config when file doesn't exist - should create default"""
        loaded_config = load_config()
        
        assert loaded_config['monthly_salary'] == 0
        assert loaded_config['daily_goal_percentage'] == 0
        assert 'created_at' in loaded_config
        assert 'updated_at' in loaded_config
    
    def test_load_config_corrupted_file(self, temp_data_dir):
        """Test loading corrupted config file - should backup and create new"""
        config_path = os.path.join(temp_data_dir, 'user_config.json')
        
        # Create corrupted file
        with open(config_path, 'w') as f:
            f.write('{"invalid": json content')
        
        with patch('utils.data_manager.backup_file') as mock_backup:
            loaded_config = load_config()
            
            # Should have called backup
            mock_backup.assert_called_once()
            
            # Should return default config
            assert loaded_config['monthly_salary'] == 0
            assert loaded_config['daily_goal_percentage'] == 0
    
    def test_save_config_success(self, temp_data_dir, sample_config):
        """Test successful config saving"""
        save_config(sample_config)
        
        # Verify file was created and contains correct data
        config_path = os.path.join(temp_data_dir, 'user_config.json')
        assert os.path.exists(config_path)
        
        with open(config_path, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data['monthly_salary'] == sample_config['monthly_salary']
        assert saved_data['daily_goal_percentage'] == sample_config['daily_goal_percentage']
        assert 'updated_at' in saved_data
    
    def test_save_config_file_error(self, temp_data_dir, sample_config):
        """Test config saving with file write error"""
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(Exception) as exc_info:
                save_config(sample_config)
            
            assert "Failed to save configuration" in str(exc_info.value)


class TestAssetOperations:
    """Test asset file operations"""
    
    def test_load_assets_existing_file(self, temp_data_dir, sample_assets):
        """Test loading existing assets file"""
        assets_path = os.path.join(temp_data_dir, 'assets.json')
        with open(assets_path, 'w') as f:
            json.dump(sample_assets, f)
        
        loaded_assets = load_assets()
        
        assert loaded_assets['bank_balance'] == sample_assets['bank_balance']
        assert loaded_assets['cash_eur'] == sample_assets['cash_eur']
        assert loaded_assets['cash_usd'] == sample_assets['cash_usd']
        assert loaded_assets['investments'] == sample_assets['investments']
    
    def test_load_assets_missing_file(self, temp_data_dir):
        """Test loading assets when file doesn't exist - should create default"""
        loaded_assets = load_assets()
        
        assert loaded_assets['bank_balance'] == 0
        assert loaded_assets['cash_eur'] == 0
        assert loaded_assets['cash_usd'] == 0
        assert loaded_assets['investments'] == 0
        assert 'created_at' in loaded_assets
        assert 'updated_at' in loaded_assets
    
    def test_load_assets_corrupted_file(self, temp_data_dir):
        """Test loading corrupted assets file"""
        assets_path = os.path.join(temp_data_dir, 'assets.json')
        
        with open(assets_path, 'w') as f:
            f.write('{"corrupted": json}')
        
        with patch('utils.data_manager.backup_file') as mock_backup:
            loaded_assets = load_assets()
            
            mock_backup.assert_called_once()
            assert loaded_assets['bank_balance'] == 0
    
    def test_save_assets_success(self, temp_data_dir, sample_assets):
        """Test successful assets saving"""
        save_assets(sample_assets)
        
        assets_path = os.path.join(temp_data_dir, 'assets.json')
        assert os.path.exists(assets_path)
        
        with open(assets_path, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data['bank_balance'] == sample_assets['bank_balance']
        assert saved_data['cash_eur'] == sample_assets['cash_eur']
        assert 'updated_at' in saved_data
    
    def test_save_assets_file_error(self, temp_data_dir, sample_assets):
        """Test assets saving with file write error"""
        with patch('builtins.open', side_effect=IOError("Disk full")):
            with pytest.raises(Exception) as exc_info:
                save_assets(sample_assets)
            
            assert "Failed to save assets" in str(exc_info.value)


class TestValidation:
    """Test data validation functions"""
    
    def test_validate_config_valid(self, sample_config):
        """Test validation of valid config"""
        result = validate_config(sample_config)
        assert result is True
    
    def test_validate_config_missing_fields(self):
        """Test validation with missing required fields"""
        invalid_config = {'monthly_salary': 3000.0}  # Missing daily_goal_percentage
        
        with pytest.raises(ValueError) as exc_info:
            validate_config(invalid_config)
        
        assert "Missing required field: daily_goal_percentage" in str(exc_info.value)
    
    def test_validate_config_negative_salary(self):
        """Test validation with negative salary"""
        invalid_config = {
            'monthly_salary': -1000.0,
            'daily_goal_percentage': 50.0
        }
        
        with pytest.raises(ValueError) as exc_info:
            validate_config(invalid_config)
        
        assert "Monthly salary must be a positive number" in str(exc_info.value)
    
    def test_validate_config_invalid_goal_percentage(self):
        """Test validation with invalid goal percentage"""
        invalid_config = {
            'monthly_salary': 3000.0,
            'daily_goal_percentage': 150.0  # > 100
        }
        
        with pytest.raises(ValueError) as exc_info:
            validate_config(invalid_config)
        
        assert "Daily goal percentage must be between 0 and 100" in str(exc_info.value)
    
    def test_validate_assets_valid(self, sample_assets):
        """Test validation of valid assets"""
        result = validate_assets(sample_assets)
        assert result is True
    
    def test_validate_assets_missing_fields(self):
        """Test validation with missing asset fields"""
        invalid_assets = {
            'bank_balance': 5000.0,
            'cash_eur': 200.0
            # Missing cash_usd and investments
        }
        
        with pytest.raises(ValueError) as exc_info:
            validate_assets(invalid_assets)
        
        assert "Missing required field" in str(exc_info.value)
    
    def test_validate_assets_invalid_types(self):
        """Test validation with invalid data types"""
        invalid_assets = {
            'bank_balance': 'not_a_number',
            'cash_eur': 200.0,
            'cash_usd': 100.0,
            'investments': 5000.0
        }
        
        with pytest.raises(ValueError) as exc_info:
            validate_assets(invalid_assets)
        
        assert "must be a number" in str(exc_info.value)


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_backup_file_exists(self, temp_data_dir):
        """Test backing up an existing file"""
        # Create a file to backup
        test_file = os.path.join(temp_data_dir, 'test_file.json')
        with open(test_file, 'w') as f:
            f.write('{"test": "data"}')
        
        with patch('utils.data_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = '20240715_120000'
            
            backup_file(test_file)
            
            # Original file should be gone, backup should exist
            assert not os.path.exists(test_file)
            backup_path = f"{test_file}.backup.20240715_120000"
            assert os.path.exists(backup_path)
    
    def test_backup_file_not_exists(self, temp_data_dir):
        """Test backing up a non-existent file"""
        non_existent_file = os.path.join(temp_data_dir, 'does_not_exist.json')
        
        # Should not raise an error
        backup_file(non_existent_file)
    
    def test_backup_file_rename_fails(self, temp_data_dir):
        """Test backup when rename fails - should delete file"""
        test_file = os.path.join(temp_data_dir, 'test_file.json')
        with open(test_file, 'w') as f:
            f.write('{"test": "data"}')
        
        with patch('utils.data_manager.os.rename', side_effect=OSError("Permission denied")):
            with patch('utils.data_manager.os.remove') as mock_remove:
                backup_file(test_file)
                mock_remove.assert_called_once_with(test_file)
    
    def test_get_data_summary_success(self, populated_data_files):
        """Test getting data summary with existing files"""
        summary = get_data_summary()
        
        assert summary['config_exists'] is True
        assert summary['assets_exists'] is True
        assert summary['monthly_salary_configured'] is True
        assert summary['assets_configured'] is True
        assert 'config_last_updated' in summary
        assert 'assets_last_updated' in summary
    
    def test_get_data_summary_no_data(self, temp_data_dir):
        """Test getting data summary with no existing data"""
        summary = get_data_summary()
        
        assert summary['config_exists'] is True  # Default config gets created
        assert summary['assets_exists'] is True  # Default assets get created
        assert summary['monthly_salary_configured'] is False  # Default is 0
        assert summary['assets_configured'] is False  # Default is all 0
    
    def test_get_data_summary_error(self, temp_data_dir):
        """Test getting data summary with file access error"""
        with patch('utils.data_manager.load_config', side_effect=Exception("File access error")):
            summary = get_data_summary()
            
            assert summary['config_exists'] is False
            assert summary['assets_exists'] is False
            assert 'error' in summary


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_config_with_zero_values(self, temp_data_dir):
        """Test config with zero values"""
        zero_config = {
            'monthly_salary': 0.0,
            'daily_goal_percentage': 0.0
        }
        
        # Should be valid
        assert validate_config(zero_config) is True
        
        # Should save and load correctly
        save_config(zero_config)
        loaded = load_config()
        
        assert loaded['monthly_salary'] == 0.0
        assert loaded['daily_goal_percentage'] == 0.0
    
    def test_assets_with_zero_values(self, temp_data_dir):
        """Test assets with zero values"""
        zero_assets = {
            'bank_balance': 0.0,
            'cash_eur': 0.0,
            'cash_usd': 0.0,
            'investments': 0.0
        }
        
        # Should be valid
        assert validate_assets(zero_assets) is True
        
        # Should save and load correctly
        save_assets(zero_assets)
        loaded = load_assets()
        
        assert loaded['bank_balance'] == 0.0
        assert loaded['investments'] == 0.0
    
    def test_large_number_values(self, temp_data_dir):
        """Test with very large numbers"""
        large_config = {
            'monthly_salary': 999999999.99,
            'daily_goal_percentage': 100.0
        }
        
        large_assets = {
            'bank_balance': 1000000000.0,
            'cash_eur': 999999.99,
            'cash_usd': 888888.88,
            'investments': 5000000000.0
        }
        
        # Should validate and save/load correctly
        assert validate_config(large_config) is True
        assert validate_assets(large_assets) is True
        
        save_config(large_config)
        save_assets(large_assets)
        
        loaded_config = load_config()
        loaded_assets = load_assets()
        
        assert loaded_config['monthly_salary'] == large_config['monthly_salary']
        assert loaded_assets['investments'] == large_assets['investments']
    
    def test_precision_handling(self, temp_data_dir):
        """Test decimal precision handling"""
        precise_config = {
            'monthly_salary': 3000.123456789,
            'daily_goal_percentage': 75.55555
        }
        
        save_config(precise_config)
        loaded = load_config()
        
        # Should preserve precision within JSON limits
        assert abs(loaded['monthly_salary'] - precise_config['monthly_salary']) < 0.000001
        assert abs(loaded['daily_goal_percentage'] - precise_config['daily_goal_percentage']) < 0.000001 