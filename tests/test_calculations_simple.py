"""
Unit tests for utils.calculations module (simplified)
Tests the actual functions as they exist in the codebase
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from utils.calculations import (
    calculate_realized_income, calculate_potential_income,
    calculate_total_assets, calculate_global_position,
    calculate_monthly_progress
)


class TestRealizedIncome:
    """Test realized income calculations"""
    
    def test_calculate_realized_income_basic(self):
        """Test basic realized income calculation"""
        with patch('utils.calculations.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 7, 15)  # July 15th
            
            with patch('utils.calculations.calendar') as mock_calendar:
                mock_calendar.monthrange.return_value = (0, 31)  # July has 31 days
                
                result = calculate_realized_income(3000.0)
                
                # Expected: (15/31) * 3000 = 1451.61
                expected = (15 / 31) * 3000
                assert abs(result - expected) < 0.01
    
    def test_calculate_realized_income_zero_salary(self):
        """Test with zero salary"""
        result = calculate_realized_income(0)
        assert result == 0
    
    def test_calculate_realized_income_negative_salary(self):
        """Test with negative salary"""
        result = calculate_realized_income(-1000)
        assert result == 0


class TestPotentialIncome:
    """Test potential income calculations"""
    
    def test_calculate_potential_income_basic(self):
        """Test basic potential income calculation"""
        with patch('utils.calculations.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 7, 15)  # July 15th
            
            with patch('utils.calculations.calendar') as mock_calendar:
                mock_calendar.monthrange.return_value = (0, 31)  # July has 31 days
                
                result = calculate_potential_income(3000.0, 75.0)
                
                # Expected: (3000/31) * 0.75 = 72.58
                daily_income = 3000 / 31
                expected = daily_income * 0.75
                assert abs(result - expected) < 0.01
    
    def test_calculate_potential_income_zero_goal(self):
        """Test with zero goal percentage"""
        result = calculate_potential_income(3000.0, 0)
        assert result == 0
    
    def test_calculate_potential_income_negative_goal(self):
        """Test with negative goal percentage"""
        result = calculate_potential_income(3000.0, -10)
        assert result == 0


class TestTotalAssets:
    """Test total assets calculation"""
    
    def test_calculate_total_assets_basic(self):
        """Test basic total assets calculation"""
        assets = {
            'bank_balance': 5000.0,
            'cash_eur': 200.0,
            'cash_usd': 100.0,
            'investments': 10000.0
        }
        
        # Test with explicit exchange rate
        result = calculate_total_assets(assets, 0.85)
        
        # Expected: 5000 + 200 + (100 * 0.85) + 10000 = 15285
        expected = 5000 + 200 + (100 * 0.85) + 10000
        assert abs(result - expected) < 0.01
    
    def test_calculate_total_assets_exchange_error(self):
        """Test total assets calculation when no exchange rate provided"""
        assets = {
            'bank_balance': 5000.0,
            'cash_eur': 200.0,
            'cash_usd': 100.0,
            'investments': 10000.0
        }
        
        # Test without exchange rate - should treat USD as EUR
        result = calculate_total_assets(assets)
        
        # Should treat USD as EUR (1:1)
        expected = 5000 + 200 + 100 + 10000
        assert result == expected


class TestGlobalPosition:
    """Test global position calculation"""
    
    def test_calculate_global_position_basic(self):
        """Test basic global position calculation"""
        assets = {
            'bank_balance': 5000.0,
            'cash_eur': 200.0,
            'cash_usd': 100.0,
            'investments': 10000.0
        }
        
        realized_income = 1500.0
        potential_income = 500.0
        
        # Test with explicit exchange rate
        result = calculate_global_position(assets, realized_income, potential_income, 0.85)
        
        # Total assets: 5000 + 200 + (100 * 0.85) + 10000 = 15285
        # Global position: 15285 + 1500 + 500 = 17285
        expected = 15285 + 1500 + 500
        assert abs(result - expected) < 0.01


class TestMonthlyProgress:
    """Test monthly progress calculation"""
    
    def test_calculate_monthly_progress_basic(self):
        """Test basic monthly progress calculation"""
        mock_date = datetime(2024, 7, 15)  # July 15th
        
        with patch('utils.calculations.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_date
            
            with patch('utils.calculations.calendar') as mock_calendar:
                mock_calendar.monthrange.return_value = (0, 31)  # July has 31 days
                
                result = calculate_monthly_progress()
                
                assert result['current_day'] == 15
                assert result['days_in_month'] == 31
                assert result['remaining_days'] == 16
                assert result['year'] == 2024
                assert abs(result['progress_percentage'] - (15/31)*100) < 0.1


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_functions_handle_exceptions(self):
        """Test that functions handle exceptions gracefully"""
        # Test with invalid inputs that might cause exceptions
        assert calculate_realized_income(None) == 0
        assert calculate_potential_income(None, None) == 0
        
        # Test with empty assets
        empty_assets = {}
        result = calculate_total_assets(empty_assets)
        assert result == 0.0
        
        # Test global position with invalid inputs
        result = calculate_global_position({}, None, None)
        assert result == 0
    
    def test_monthly_progress_handles_exceptions(self):
        """Test monthly progress handles datetime exceptions"""
        with patch('utils.calculations.datetime', side_effect=Exception("Date error")):
            result = calculate_monthly_progress()
            
            # Should return sensible defaults
            assert result['current_day'] == 1
            assert result['days_in_month'] == 30
            assert result['progress_percentage'] == 0 