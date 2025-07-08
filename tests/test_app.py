"""
Integration tests for the Flask application
Tests all API endpoints, error handling, and complete workflows
"""

import pytest
import json
from unittest.mock import patch, Mock
from flask import url_for

from app import app


class TestAppConfiguration:
    """Test Flask application configuration"""
    
    def test_app_in_testing_mode(self, client):
        """Test that app is properly configured for testing"""
        assert app.config['TESTING'] is True
    
    def test_app_secret_key_set(self, client):
        """Test that secret key is configured"""
        assert app.config['SECRET_KEY'] is not None


class TestStaticRoutes:
    """Test static page routes"""
    
    def test_dashboard_route(self, client):
        """Test dashboard page loads successfully"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'MindBank' in response.data
        assert b'Global Position' in response.data
    
    def test_config_route(self, client):
        """Test configuration page loads successfully"""
        response = client.get('/config')
        
        assert response.status_code == 200
        assert b'Configuration' in response.data
        assert b'Monthly Salary' in response.data


class TestUpdateAssetsAPI:
    """Test /api/update-assets endpoint"""
    
    def test_update_assets_success(self, client, temp_data_dir, api_test_data):
        """Test successful asset update"""
        response = client.post('/api/update-assets',
                              json=api_test_data['valid_assets'],
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'message' in data
        assert 'assets' in data
        assert data['assets']['bank_balance'] == api_test_data['valid_assets']['bank_balance']
    
    def test_update_assets_invalid_data(self, client, temp_data_dir, api_test_data):
        """Test asset update with invalid data"""
        response = client.post('/api/update-assets',
                              json=api_test_data['invalid_assets'],
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert 'error' in data
        assert 'must be a number' in data['error']
    
    def test_update_assets_missing_fields(self, client, temp_data_dir):
        """Test asset update with missing required fields"""
        incomplete_assets = {
            'bank_balance': 5000.0,
            'cash_eur': 200.0
            # Missing cash_usd and investments
        }
        
        response = client.post('/api/update-assets',
                              json=incomplete_assets,
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert 'error' in data
    
    def test_update_assets_no_json(self, client, temp_data_dir):
        """Test asset update without JSON data"""
        response = client.post('/api/update-assets')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert 'error' in data
        assert 'JSON data required' in data['error']
    
    def test_update_assets_file_save_error(self, client, temp_data_dir, api_test_data):
        """Test asset update with file save error"""
        with patch('app.save_assets', side_effect=Exception("Save failed")):
            response = client.post('/api/update-assets',
                                  json=api_test_data['valid_assets'],
                                  content_type='application/json')
            
            assert response.status_code == 500
            data = response.get_json()
            
            assert data['success'] is False
            assert 'error' in data


class TestUpdateConfigAPI:
    """Test /api/update-config endpoint"""
    
    def test_update_config_success(self, client, temp_data_dir, api_test_data):
        """Test successful config update"""
        response = client.post('/api/update-config',
                              json=api_test_data['valid_config'],
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'message' in data
        assert 'config' in data
        assert data['config']['monthly_salary'] == api_test_data['valid_config']['monthly_salary']
    
    def test_update_config_invalid_data(self, client, temp_data_dir, api_test_data):
        """Test config update with invalid data"""
        response = client.post('/api/update-config',
                              json=api_test_data['invalid_config'],
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert 'error' in data
    
    def test_update_config_missing_fields(self, client, temp_data_dir):
        """Test config update with missing required fields"""
        incomplete_config = {
            'monthly_salary': 3000.0
            # Missing daily_goal_percentage
        }
        
        response = client.post('/api/update-config',
                              json=incomplete_config,
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert 'error' in data
    
    def test_update_config_no_json(self, client, temp_data_dir):
        """Test config update without JSON data"""
        response = client.post('/api/update-config')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert 'error' in data


class TestDailyGoalAPI:
    """Test /api/daily-goal endpoint"""
    
    def test_update_daily_goal_success(self, client, temp_data_dir, api_test_data):
        """Test successful daily goal update"""
        response = client.post('/api/daily-goal',
                              json=api_test_data['valid_goal_update'],
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'message' in data
        assert 'goal_percentage' in data
        assert data['goal_percentage'] == api_test_data['valid_goal_update']['goal_percentage']
    
    def test_update_daily_goal_invalid_percentage(self, client, temp_data_dir, api_test_data):
        """Test daily goal update with invalid percentage"""
        response = client.post('/api/daily-goal',
                              json=api_test_data['invalid_goal_update'],
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert 'error' in data
    
    def test_update_daily_goal_missing_field(self, client, temp_data_dir):
        """Test daily goal update with missing goal_percentage field"""
        response = client.post('/api/daily-goal',
                              json={'other_field': 'value'},
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert 'error' in data
        assert 'goal_percentage' in data['error']
    
    def test_update_daily_goal_no_json(self, client, temp_data_dir):
        """Test daily goal update without JSON data"""
        response = client.post('/api/daily-goal')
        
        assert response.status_code == 400
        data = response.get_json()
        
        assert data['success'] is False
        assert 'error' in data


class TestDashboardDataAPI:
    """Test /api/dashboard-data endpoint"""
    
    def test_dashboard_data_success(self, client, populated_data_files, mock_exchange_api):
        """Test successful dashboard data retrieval"""
        response = client.get('/api/dashboard-data')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'assets' in data
        assert 'config' in data
        assert 'calculations' in data
        assert 'exchange_rate' in data
        
        # Verify structure of calculations
        calculations = data['calculations']
        assert 'realized_income' in calculations
        assert 'potential_income' in calculations
        assert 'total_assets' in calculations
        assert 'global_position' in calculations
        assert 'monthly_progress' in calculations
        
        # Verify all values are numeric
        assert isinstance(calculations['realized_income'], (int, float))
        assert isinstance(calculations['potential_income'], (int, float))
        assert isinstance(calculations['total_assets'], (int, float))
        assert isinstance(calculations['global_position'], (int, float))
        assert isinstance(calculations['monthly_progress'], (int, float))
    
    def test_dashboard_data_with_usd_conversion(self, client, populated_data_files, mock_exchange_api):
        """Test dashboard data with USD to EUR conversion"""
        response = client.get('/api/dashboard-data')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Should have exchange rate from mock
        assert data['exchange_rate'] == 0.8542
        
        # Total assets should include converted USD
        calculations = data['calculations']
        expected_total = 5000.0 + 200.0 + (100.0 * 0.8542) + 10000.0
        assert abs(calculations['total_assets'] - expected_total) < 0.01
    
    def test_dashboard_data_exchange_rate_failure(self, client, populated_data_files):
        """Test dashboard data when exchange rate API fails"""
        with patch('app.get_exchange_rate', return_value=0.85):  # Fallback rate
            response = client.get('/api/dashboard-data')
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Should use fallback exchange rate
            assert data['exchange_rate'] == 0.85
    
    def test_dashboard_data_data_loading_error(self, client, temp_data_dir):
        """Test dashboard data when data loading fails"""
        with patch('app.load_config', side_effect=Exception("Load failed")):
            response = client.get('/api/dashboard-data')
            
            assert response.status_code == 500
            data = response.get_json()
            
            assert 'error' in data
    
    def test_dashboard_data_calculation_error(self, client, populated_data_files):
        """Test dashboard data when calculations fail"""
        with patch('app.calculate_global_position', side_effect=Exception("Calc failed")):
            response = client.get('/api/dashboard-data')
            
            assert response.status_code == 500
            data = response.get_json()
            
            assert 'error' in data


class TestExchangeRateAPI:
    """Test /api/exchange-rate endpoint"""
    
    def test_exchange_rate_success(self, client, mock_exchange_api):
        """Test successful exchange rate retrieval"""
        response = client.get('/api/exchange-rate')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'rate' in data
        assert 'source' in data
        assert 'timestamp' in data
        assert data['rate'] == 0.8542
    
    def test_exchange_rate_api_failure(self, client):
        """Test exchange rate retrieval when API fails"""
        with patch('app.get_exchange_rate', return_value=0.85):  # Fallback
            response = client.get('/api/exchange-rate')
            
            assert response.status_code == 200
            data = response.get_json()
            
            assert data['rate'] == 0.85
            assert 'source' in data
    
    def test_exchange_rate_exception(self, client):
        """Test exchange rate retrieval with exception"""
        with patch('app.get_exchange_rate', side_effect=Exception("Rate failed")):
            response = client.get('/api/exchange-rate')
            
            assert response.status_code == 500
            data = response.get_json()
            
            assert 'error' in data


class TestHTTPMethods:
    """Test HTTP method restrictions"""
    
    def test_get_method_not_allowed_on_post_endpoints(self, client):
        """Test that GET is not allowed on POST-only endpoints"""
        post_endpoints = [
            '/api/update-assets',
            '/api/update-config',
            '/api/daily-goal'
        ]
        
        for endpoint in post_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 405  # Method Not Allowed
    
    def test_post_method_not_allowed_on_get_endpoints(self, client):
        """Test that POST is not allowed on GET-only endpoints"""
        get_endpoints = [
            '/api/dashboard-data',
            '/api/exchange-rate'
        ]
        
        for endpoint in get_endpoints:
            response = client.post(endpoint, json={'test': 'data'})
            assert response.status_code == 405  # Method Not Allowed


class TestErrorHandling:
    """Test application error handling"""
    
    def test_404_for_nonexistent_route(self, client):
        """Test 404 response for non-existent routes"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
    
    def test_invalid_json_handling(self, client):
        """Test handling of invalid JSON in requests"""
        response = client.post('/api/update-assets',
                              data='{"invalid": json}',
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_content_type_validation(self, client):
        """Test that endpoints require proper content type"""
        response = client.post('/api/update-assets',
                              data='{"valid": "json"}',
                              content_type='text/plain')
        
        assert response.status_code == 400


class TestCompleteWorkflows:
    """Test complete user workflows"""
    
    def test_complete_setup_workflow(self, client, temp_data_dir, mock_exchange_api):
        """Test complete user setup workflow"""
        # Step 1: User configures salary and initial goal
        config_data = {
            'monthly_salary': 4000.0,
            'daily_goal_percentage': 80.0
        }
        
        response = client.post('/api/update-config',
                              json=config_data,
                              content_type='application/json')
        assert response.status_code == 200
        
        # Step 2: User enters asset information
        assets_data = {
            'bank_balance': 8000.0,
            'cash_eur': 300.0,
            'cash_usd': 500.0,
            'investments': 25000.0
        }
        
        response = client.post('/api/update-assets',
                              json=assets_data,
                              content_type='application/json')
        assert response.status_code == 200
        
        # Step 3: User views dashboard
        response = client.get('/api/dashboard-data')
        assert response.status_code == 200
        
        data = response.get_json()
        
        # Verify complete calculation
        assert data['config']['monthly_salary'] == 4000.0
        assert data['assets']['bank_balance'] == 8000.0
        assert data['calculations']['global_position'] > 30000  # Should be substantial
    
    def test_daily_goal_adjustment_workflow(self, client, populated_data_files, mock_exchange_api):
        """Test daily goal adjustment workflow"""
        # Step 1: Get initial dashboard data
        response = client.get('/api/dashboard-data')
        assert response.status_code == 200
        initial_data = response.get_json()
        initial_position = initial_data['calculations']['global_position']
        
        # Step 2: Adjust daily goal
        new_goal_data = {'goal_percentage': 95.0}
        
        response = client.post('/api/daily-goal',
                              json=new_goal_data,
                              content_type='application/json')
        assert response.status_code == 200
        
        # Step 3: Get updated dashboard data
        response = client.get('/api/dashboard-data')
        assert response.status_code == 200
        updated_data = response.get_json()
        updated_position = updated_data['calculations']['global_position']
        
        # Verify goal was updated and position changed
        assert updated_data['config']['daily_goal_percentage'] == 95.0
        assert updated_position > initial_position  # Higher goal should increase position
    
    def test_asset_update_workflow(self, client, populated_data_files, mock_exchange_api):
        """Test asset update workflow"""
        # Step 1: Get initial assets
        response = client.get('/api/dashboard-data')
        assert response.status_code == 200
        initial_data = response.get_json()
        initial_total_assets = initial_data['calculations']['total_assets']
        
        # Step 2: Update assets (add money to bank)
        updated_assets = {
            'bank_balance': 7000.0,  # Increased from 5000
            'cash_eur': 200.0,
            'cash_usd': 100.0,
            'investments': 10000.0
        }
        
        response = client.post('/api/update-assets',
                              json=updated_assets,
                              content_type='application/json')
        assert response.status_code == 200
        
        # Step 3: Verify changes reflected in dashboard
        response = client.get('/api/dashboard-data')
        assert response.status_code == 200
        updated_data = response.get_json()
        new_total_assets = updated_data['calculations']['total_assets']
        
        # Should have increased by 2000 EUR
        assert abs((new_total_assets - initial_total_assets) - 2000.0) < 1.0
    
    def test_error_recovery_workflow(self, client, temp_data_dir):
        """Test error recovery workflow"""
        # Step 1: Try to submit invalid data
        invalid_config = {
            'monthly_salary': -1000.0,  # Invalid
            'daily_goal_percentage': 150.0  # Invalid
        }
        
        response = client.post('/api/update-config',
                              json=invalid_config,
                              content_type='application/json')
        assert response.status_code == 400
        
        # Step 2: Submit corrected data
        valid_config = {
            'monthly_salary': 3500.0,
            'daily_goal_percentage': 75.0
        }
        
        response = client.post('/api/update-config',
                              json=valid_config,
                              content_type='application/json')
        assert response.status_code == 200
        
        # Step 3: Verify system recovered and data is correct
        response = client.get('/api/dashboard-data')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['config']['monthly_salary'] == 3500.0
        assert data['config']['daily_goal_percentage'] == 75.0


class TestResponseFormats:
    """Test API response formats"""
    
    def test_success_response_format(self, client, temp_data_dir, api_test_data):
        """Test that success responses have consistent format"""
        response = client.post('/api/update-config',
                              json=api_test_data['valid_config'],
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Standard success format
        assert 'success' in data
        assert data['success'] is True
        assert 'message' in data
        assert isinstance(data['message'], str)
    
    def test_error_response_format(self, client, temp_data_dir, api_test_data):
        """Test that error responses have consistent format"""
        response = client.post('/api/update-config',
                              json=api_test_data['invalid_config'],
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        
        # Standard error format
        assert 'success' in data
        assert data['success'] is False
        assert 'error' in data
        assert isinstance(data['error'], str)
    
    def test_json_content_type(self, client):
        """Test that API responses have correct content type"""
        response = client.get('/api/dashboard-data')
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'


class TestDataPersistence:
    """Test data persistence across requests"""
    
    def test_config_persistence(self, client, temp_data_dir):
        """Test that configuration persists across requests"""
        config_data = {
            'monthly_salary': 5500.0,
            'daily_goal_percentage': 85.0
        }
        
        # Set config
        response = client.post('/api/update-config',
                              json=config_data,
                              content_type='application/json')
        assert response.status_code == 200
        
        # Retrieve config in new request
        response = client.get('/api/dashboard-data')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['config']['monthly_salary'] == 5500.0
        assert data['config']['daily_goal_percentage'] == 85.0
    
    def test_assets_persistence(self, client, temp_data_dir):
        """Test that assets persist across requests"""
        assets_data = {
            'bank_balance': 15000.0,
            'cash_eur': 750.0,
            'cash_usd': 200.0,
            'investments': 50000.0
        }
        
        # Set assets
        response = client.post('/api/update-assets',
                              json=assets_data,
                              content_type='application/json')
        assert response.status_code == 200
        
        # Retrieve assets in new request
        response = client.get('/api/dashboard-data')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['assets']['bank_balance'] == 15000.0
        assert data['assets']['cash_eur'] == 750.0
        assert data['assets']['investments'] == 50000.0 