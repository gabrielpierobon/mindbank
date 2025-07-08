"""
Unit tests for utils.calculations module
Tests financial calculations, time-based calculations, and edge cases
"""

import pytest
import calendar
from datetime import datetime
from unittest.mock import patch, Mock

from utils.calculations import (
    calculate_realized_income, calculate_potential_income,
    calculate_total_assets, calculate_global_position,
    calculate_monthly_progress, calculate_realized_monthly_income,
    calculate_potential_daily_income, get_monthly_progress,
    validate_percentage
)


class TestRealizedIncome:
    """Test realized income calculations"""
    
    def test_basic_calculation(self, frozen_time, mock_calendar):
        """Test basic realized income calculation"""
        monthly_salary = 3000.0
        
        # July 15th (day 15 of 31-day month)
        result = calculate_realized_income(monthly_salary)
        
        # Expected: (15 days / 31 days) * 3000 = 1451.61 (no goal percentage since not provided)
        expected = (15 / 31) * 3000
        assert abs(result - expected) < 0.01
    
    def test_zero_salary(self, frozen_time, mock_calendar):
        """Test with zero salary"""
        result = calculate_realized_monthly_income(0.0, 75.0)
        assert result == 0.0
    
    def test_zero_goal_percentage(self, frozen_time, mock_calendar):
        """Test with zero goal percentage"""
        result = calculate_realized_monthly_income(3000.0, 0.0)
        assert result == 0.0
    
    def test_hundred_percent_goal(self, frozen_time, mock_calendar):
        """Test with 100% goal achievement"""
        monthly_salary = 3000.0
        goal_percentage = 100.0
        
        result = calculate_realized_monthly_income(monthly_salary, goal_percentage)
        
        # Expected: (15 days / 31 days) * 3000 * 1.0 = 1451.61
        expected = (15 / 31) * 3000 * 1.0
        assert abs(result - expected) < 0.01
    
    def test_first_day_of_month(self, mock_calendar):
        """Test calculation on first day of month"""
        with patch('utils.calculations.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 7, 1, 12, 0, 0)
            
            result = calculate_realized_monthly_income(3000.0, 75.0)
            
            # Expected: (1 day / 31 days) * 3000 * 0.75 = 72.58
            expected = (1 / 31) * 3000 * 0.75
            assert abs(result - expected) < 0.01
    
    def test_last_day_of_month(self, mock_calendar):
        """Test calculation on last day of month"""
        with patch('utils.calculations.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 7, 31, 12, 0, 0)
            
            result = calculate_realized_monthly_income(3000.0, 75.0)
            
            # Expected: (31 days / 31 days) * 3000 * 0.75 = 2250.0
            expected = (31 / 31) * 3000 * 0.75
            assert abs(result - expected) < 0.01
    
    def test_february_leap_year(self):
        """Test calculation in February of leap year"""
        with patch('utils.calculations.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 2, 15, 12, 0, 0)  # Leap year
            
            with patch('utils.calculations.calendar') as mock_cal:
                mock_cal.monthrange.return_value = (0, 29)  # February 2024 has 29 days
                
                result = calculate_realized_monthly_income(3000.0, 50.0)
                
                # Expected: (15 days / 29 days) * 3000 * 0.5 = 775.86
                expected = (15 / 29) * 3000 * 0.5
                assert abs(result - expected) < 0.01
    
    def test_large_salary(self, frozen_time, mock_calendar):
        """Test with very large salary"""
        monthly_salary = 1000000.0
        goal_percentage = 90.0
        
        result = calculate_realized_monthly_income(monthly_salary, goal_percentage)
        
        expected = (15 / 31) * 1000000 * 0.9
        assert abs(result - expected) < 1.0  # Allow for larger rounding with big numbers


class TestPotentialDailyIncome:
    """Test potential daily income calculations"""
    
    def test_basic_calculation(self, frozen_time, mock_calendar):
        """Test basic potential income calculation"""
        monthly_salary = 3000.0
        goal_percentage = 75.0
        
        result = calculate_potential_daily_income(monthly_salary, goal_percentage)
        
        # Days remaining: 31 - 15 = 16 days
        # Daily salary: 3000 / 31 = 96.77
        # Potential: 16 * 96.77 * 0.75 = 1161.29
        expected = (31 - 15) * (3000 / 31) * 0.75
        assert abs(result - expected) < 0.01
    
    def test_zero_salary(self, frozen_time, mock_calendar):
        """Test with zero salary"""
        result = calculate_potential_daily_income(0.0, 75.0)
        assert result == 0.0
    
    def test_zero_goal_percentage(self, frozen_time, mock_calendar):
        """Test with zero goal percentage"""
        result = calculate_potential_daily_income(3000.0, 0.0)
        assert result == 0.0
    
    def test_last_day_of_month(self, mock_calendar):
        """Test potential income on last day of month"""
        with patch('utils.calculations.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 7, 31, 12, 0, 0)
            
            result = calculate_potential_daily_income(3000.0, 75.0)
            
            # Days remaining: 31 - 31 = 0 days
            assert result == 0.0
    
    def test_first_day_of_month(self, mock_calendar):
        """Test potential income on first day of month"""
        with patch('utils.calculations.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 7, 1, 12, 0, 0)
            
            result = calculate_potential_daily_income(3000.0, 50.0)
            
            # Days remaining: 31 - 1 = 30 days
            # Daily salary: 3000 / 31 = 96.77
            # Potential: 30 * 96.77 * 0.5 = 1451.61
            expected = (31 - 1) * (3000 / 31) * 0.5
            assert abs(result - expected) < 0.01


class TestTotalAssets:
    """Test total assets calculation"""
    
    def test_basic_calculation(self, sample_assets):
        """Test basic assets calculation without currency conversion"""
        result = calculate_total_assets(sample_assets)
        
        # Bank + EUR + USD (no conversion) + Investments
        # 5000 + 200 + 100 + 10000 = 15300
        expected = 5000.0 + 200.0 + 100.0 + 10000.0
        assert result == expected
    
    def test_with_usd_conversion(self, sample_assets):
        """Test assets calculation with USD to EUR conversion"""
        usd_to_eur_rate = 0.85
        
        result = calculate_total_assets(sample_assets, usd_to_eur_rate)
        
        # Bank + EUR + USD*rate + Investments
        # 5000 + 200 + (100 * 0.85) + 10000 = 15285
        expected = 5000.0 + 200.0 + (100.0 * 0.85) + 10000.0
        assert result == expected
    
    def test_zero_assets(self):
        """Test with all zero assets"""
        zero_assets = {
            'bank_balance': 0.0,
            'cash_eur': 0.0,
            'cash_usd': 0.0,
            'investments': 0.0
        }
        
        result = calculate_total_assets(zero_assets)
        assert result == 0.0
    
    def test_negative_assets(self):
        """Test with negative assets (debt)"""
        negative_assets = {
            'bank_balance': -1000.0,  # Overdraft
            'cash_eur': 200.0,
            'cash_usd': 100.0,
            'investments': 5000.0
        }
        
        result = calculate_total_assets(negative_assets)
        expected = -1000.0 + 200.0 + 100.0 + 5000.0
        assert result == expected
    
    def test_large_assets(self):
        """Test with very large asset values"""
        large_assets = {
            'bank_balance': 10000000.0,
            'cash_eur': 50000.0,
            'cash_usd': 25000.0,
            'investments': 5000000.0
        }
        
        result = calculate_total_assets(large_assets, 0.9)
        expected = 10000000.0 + 50000.0 + (25000.0 * 0.9) + 5000000.0
        assert result == expected


class TestGlobalPosition:
    """Test global position calculation"""
    
    def test_complete_calculation(self, frozen_time, mock_calendar, sample_assets):
        """Test complete global position calculation"""
        monthly_salary = 3000.0
        goal_percentage = 75.0
        usd_to_eur_rate = 0.85
        
        result = calculate_global_position(
            sample_assets, monthly_salary, goal_percentage, usd_to_eur_rate
        )
        
        # Assets: 5000 + 200 + (100 * 0.85) + 10000 = 15285
        assets = 5000.0 + 200.0 + (100.0 * 0.85) + 10000.0
        
        # Realized: (15/31) * 3000 * 0.75 = 1088.71
        realized = (15 / 31) * 3000 * 0.75
        
        # Potential: (16/31) * 3000 * 0.75 = 1161.29
        potential = (31 - 15) * (3000 / 31) * 0.75
        
        expected = assets + realized + potential
        assert abs(result - expected) < 0.01
    
    def test_zero_everything(self):
        """Test with all zero values"""
        zero_assets = {
            'bank_balance': 0.0,
            'cash_eur': 0.0,
            'cash_usd': 0.0,
            'investments': 0.0
        }
        
        result = calculate_global_position(zero_assets, 0.0, 0.0)
        assert result == 0.0
    
    def test_without_usd_conversion(self, frozen_time, mock_calendar, sample_assets):
        """Test global position without USD conversion"""
        monthly_salary = 3000.0
        goal_percentage = 50.0
        
        result = calculate_global_position(sample_assets, monthly_salary, goal_percentage)
        
        # Assets without conversion: 5000 + 200 + 100 + 10000 = 15300
        assets = 15300.0
        
        # Realized: (15/31) * 3000 * 0.5 = 725.81
        realized = (15 / 31) * 3000 * 0.5
        
        # Potential: (16/31) * 3000 * 0.5 = 774.19
        potential = (31 - 15) * (3000 / 31) * 0.5
        
        expected = assets + realized + potential
        assert abs(result - expected) < 0.01


class TestMonthlyProgress:
    """Test monthly progress calculation"""
    
    def test_mid_month_progress(self, frozen_time, mock_calendar):
        """Test progress in middle of month"""
        progress = get_monthly_progress()
        
        # July 15th of 31-day month
        expected = 15 / 31
        assert abs(progress - expected) < 0.01
    
    def test_first_day_progress(self, mock_calendar):
        """Test progress on first day"""
        with patch('utils.calculations.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 7, 1, 12, 0, 0)
            
            progress = get_monthly_progress()
            expected = 1 / 31
            assert abs(progress - expected) < 0.01
    
    def test_last_day_progress(self, mock_calendar):
        """Test progress on last day"""
        with patch('utils.calculations.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 7, 31, 12, 0, 0)
            
            progress = get_monthly_progress()
            expected = 31 / 31
            assert progress == 1.0
    
    def test_february_progress(self):
        """Test progress in February"""
        with patch('utils.calculations.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 2, 14, 12, 0, 0)
            
            with patch('utils.calculations.calendar') as mock_cal:
                mock_cal.monthrange.return_value = (0, 29)  # February 2024
                
                progress = get_monthly_progress()
                expected = 14 / 29
                assert abs(progress - expected) < 0.01


class TestValidatePercentage:
    """Test percentage validation"""
    
    def test_valid_percentages(self):
        """Test valid percentage values"""
        assert validate_percentage(0.0) is True
        assert validate_percentage(50.0) is True
        assert validate_percentage(100.0) is True
        assert validate_percentage(75.5) is True
    
    def test_invalid_percentages(self):
        """Test invalid percentage values"""
        with pytest.raises(ValueError):
            validate_percentage(-1.0)
        
        with pytest.raises(ValueError):
            validate_percentage(101.0)
        
        with pytest.raises(ValueError):
            validate_percentage(150.0)
    
    def test_edge_case_percentages(self):
        """Test edge case percentage values"""
        assert validate_percentage(0.0001) is True
        assert validate_percentage(99.9999) is True
        
        with pytest.raises(ValueError):
            validate_percentage(-0.0001)
        
        with pytest.raises(ValueError):
            validate_percentage(100.0001)
    
    def test_non_numeric_percentages(self):
        """Test non-numeric percentage values"""
        with pytest.raises(TypeError):
            validate_percentage("50")
        
        with pytest.raises(TypeError):
            validate_percentage(None)
        
        with pytest.raises(TypeError):
            validate_percentage([50.0])


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_very_small_numbers(self, frozen_time, mock_calendar):
        """Test calculations with very small numbers"""
        monthly_salary = 0.01
        goal_percentage = 0.01
        
        realized = calculate_realized_monthly_income(monthly_salary, goal_percentage)
        potential = calculate_potential_daily_income(monthly_salary, goal_percentage)
        
        # Should handle without errors and return small positive values
        assert realized >= 0
        assert potential >= 0
        assert realized < 1.0
        assert potential < 1.0
    
    def test_very_large_numbers(self, frozen_time, mock_calendar):
        """Test calculations with very large numbers"""
        monthly_salary = 1000000000.0  # 1 billion
        goal_percentage = 99.99
        
        realized = calculate_realized_monthly_income(monthly_salary, goal_percentage)
        potential = calculate_potential_daily_income(monthly_salary, goal_percentage)
        
        # Should handle without overflow
        assert realized > 0
        assert potential > 0
        assert realized < monthly_salary  # Should be less than total salary
    
    def test_floating_point_precision(self, frozen_time, mock_calendar):
        """Test floating point precision handling"""
        # Use numbers that can cause floating point precision issues
        monthly_salary = 3000.33333333
        goal_percentage = 66.66666666
        
        realized = calculate_realized_monthly_income(monthly_salary, goal_percentage)
        potential = calculate_potential_daily_income(monthly_salary, goal_percentage)
        
        # Should return reasonable results despite precision issues
        assert isinstance(realized, float)
        assert isinstance(potential, float)
        assert realized > 0
        assert potential > 0
    
    def test_monthly_day_boundaries(self):
        """Test calculations across different month lengths"""
        test_cases = [
            (1, 31),   # January
            (2, 28),   # February (non-leap)
            (2, 29),   # February (leap)
            (4, 30),   # April
            (12, 31),  # December
        ]
        
        for month, days in test_cases:
            with patch('utils.calculations.datetime') as mock_datetime:
                mock_datetime.now.return_value = datetime(2024, month, days // 2, 12, 0, 0)
                
                with patch('utils.calculations.calendar') as mock_cal:
                    mock_cal.monthrange.return_value = (0, days)
                    
                    realized = calculate_realized_monthly_income(3000.0, 75.0)
                    potential = calculate_potential_daily_income(3000.0, 75.0)
                    
                    assert realized >= 0
                    assert potential >= 0
    
    def test_decimal_goal_percentages(self, frozen_time, mock_calendar):
        """Test with precise decimal goal percentages"""
        test_percentages = [0.1, 0.5, 12.345, 87.654321, 99.999]
        
        for percentage in test_percentages:
            realized = calculate_realized_monthly_income(3000.0, percentage)
            potential = calculate_potential_daily_income(3000.0, percentage)
            
            assert realized >= 0
            assert potential >= 0
            
            # Verify calculations are proportional to percentage
            if percentage > 0:
                assert realized > 0
                assert potential > 0


class TestIntegrationScenarios:
    """Test realistic integration scenarios"""
    
    def test_realistic_user_scenario_1(self, mock_calendar):
        """Test scenario: Mid-career professional, mid-month"""
        with patch('utils.calculations.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 6, 15, 14, 0, 0)  # June 15
            
            with patch('utils.calculations.calendar') as mock_cal:
                mock_cal.monthrange.return_value = (0, 30)  # June has 30 days
                
                assets = {
                    'bank_balance': 12000.0,
                    'cash_eur': 500.0,
                    'cash_usd': 300.0,
                    'investments': 45000.0
                }
                
                monthly_salary = 4500.0
                goal_percentage = 80.0
                usd_rate = 0.92
                
                global_pos = calculate_global_position(assets, monthly_salary, goal_percentage, usd_rate)
                progress = get_monthly_progress()
                
                # Verify realistic ranges
                assert global_pos > 50000  # Should be substantial
                assert 0.4 < progress < 0.6  # Mid-month
    
    def test_realistic_user_scenario_2(self, mock_calendar):
        """Test scenario: Entry-level worker, end of month"""
        with patch('utils.calculations.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 3, 28, 18, 0, 0)  # March 28
            
            with patch('utils.calculations.calendar') as mock_cal:
                mock_cal.monthrange.return_value = (0, 31)  # March has 31 days
                
                assets = {
                    'bank_balance': 2500.0,
                    'cash_eur': 150.0,
                    'cash_usd': 50.0,
                    'investments': 1000.0
                }
                
                monthly_salary = 2200.0
                goal_percentage = 65.0
                
                realized = calculate_realized_monthly_income(monthly_salary, goal_percentage)
                potential = calculate_potential_daily_income(monthly_salary, goal_percentage)
                
                # Near end of month, realized should be much higher than potential
                assert realized > potential
                assert realized > 1000  # Most of month completed
                assert potential < 300   # Few days remaining
    
    def test_realistic_user_scenario_3(self, mock_calendar):
        """Test scenario: High earner with significant assets"""
        with patch('utils.calculations.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 12, 10, 9, 0, 0)  # December 10
            
            with patch('utils.calculations.calendar') as mock_cal:
                mock_cal.monthrange.return_value = (0, 31)  # December has 31 days
                
                assets = {
                    'bank_balance': 50000.0,
                    'cash_eur': 2000.0,
                    'cash_usd': 5000.0,
                    'investments': 250000.0
                }
                
                monthly_salary = 8000.0
                goal_percentage = 95.0
                usd_rate = 0.88
                
                total_assets = calculate_total_assets(assets, usd_rate)
                global_pos = calculate_global_position(assets, monthly_salary, goal_percentage, usd_rate)
                
                # Assets should dominate the calculation
                assert total_assets > 300000
                assert global_pos > total_assets  # Income adds to position
                assert (global_pos - total_assets) < total_assets * 0.1  # But income is smaller proportion 