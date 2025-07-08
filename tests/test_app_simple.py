"""
Integration tests for the Flask application (simplified)
Tests the actual API endpoints as they exist in the app
"""

import pytest
import json
from unittest.mock import patch


class TestBasicRoutes:
    """Test basic page routes"""
    
    def test_dashboard_route(self, client):
        """Test dashboard page loads"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'html' in response.data.lower()
    
    def test_config_route(self, client):
        """Test configuration page loads"""
        response = client.get('/config')
        assert response.status_code == 200
        assert b'html' in response.data.lower()


class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_dashboard_data_endpoint(self, client, temp_data_dir):
        """Test dashboard data API endpoint"""
        with patch('utils.currency.get_exchange_rate', return_value=0.85):
            response = client.get('/api/dashboard-data')
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Should have main data sections
            assert 'assets' in data
            assert 'config' in data
            assert 'global_position' in data
            assert 'realized_income' in data
            assert 'potential_income' in data
    
    def test_update_config_endpoint(self, client, temp_data_dir):
        """Test config update API endpoint"""
        config_data = {
            'monthly_salary': 3500.0,
            'daily_goal_percentage': 80.0
        }
        
        response = client.post('/api/update-config',
                              json=config_data,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'message' in data
    
    def test_update_assets_endpoint(self, client, temp_data_dir):
        """Test assets update API endpoint"""
        assets_data = {
            'bank_balance': 6000.0,
            'cash_eur': 250.0,
            'cash_usd': 150.0,
            'investments': 12000.0
        }
        
        response = client.post('/api/update-assets',
                              json=assets_data,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'message' in data
    
    def test_daily_goal_endpoint(self, client, temp_data_dir):
        """Test daily goal update API endpoint"""
        goal_data = {'goal_percentage': 85.0}
        
        response = client.post('/api/daily-goal',
                              json=goal_data,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        assert 'goal_percentage' in data
    
    def test_exchange_rate_endpoint(self, client):
        """Test exchange rate API endpoint"""
        with patch('app.get_exchange_rate', return_value=0.87):
            response = client.get('/api/exchange-rate')
            
            assert response.status_code == 200
            data = response.get_json()
            
            assert 'rate' in data
            assert data['rate'] == 0.87


class TestErrorHandling:
    """Test basic error handling"""
    
    def test_invalid_json_request(self, client, temp_data_dir):
        """Test handling of invalid JSON"""
        response = client.post('/api/update-config',
                              data='{"invalid": json}',
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_missing_json_request(self, client, temp_data_dir):
        """Test handling of missing JSON data"""
        response = client.post('/api/update-config')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_nonexistent_route(self, client):
        """Test 404 for non-existent routes"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404


class TestWorkflow:
    """Test basic user workflow"""
    
    def test_complete_workflow(self, client, temp_data_dir):
        """Test a complete user workflow"""
        # Step 1: Update configuration
        config_data = {
            'monthly_salary': 4000.0,
            'daily_goal_percentage': 75.0
        }
        
        response = client.post('/api/update-config',
                              json=config_data,
                              content_type='application/json')
        assert response.status_code == 200
        
        # Step 2: Update assets
        assets_data = {
            'bank_balance': 8000.0,
            'cash_eur': 500.0,
            'cash_usd': 300.0,
            'investments': 25000.0
        }
        
        response = client.post('/api/update-assets',
                              json=assets_data,
                              content_type='application/json')
        assert response.status_code == 200
        
        # Step 3: Get dashboard data
        with patch('utils.currency.get_exchange_rate', return_value=0.85):
            response = client.get('/api/dashboard-data')
            assert response.status_code == 200
            
            data = response.get_json()
            
            # Verify data was saved and calculations work
            assert data['config']['monthly_salary'] == 4000.0
            assert data['assets']['bank_balance'] == 8000.0
            assert 'global_position' in data['calculations']
            assert data['calculations']['global_position'] > 30000  # Should be substantial 