"""
Unit tests for utils.currency module
Tests exchange rate API integration, caching, and error handling
"""

import pytest
import json
import os
import tempfile
import requests
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, MagicMock

from utils.currency import (
    get_exchange_rate, get_cached_rate, cache_rate,
    fetch_rate_from_api, FALLBACK_RATE, get_rate_info, convert_usd_to_eur
)


class TestCacheOperations:
    """Test currency cache operations"""
    
    def test_cache_rate_success(self, temp_data_dir, sample_exchange_rate):
        """Test successful rate caching"""
        cache_rate(sample_exchange_rate['rate'])
        
        # Verify cache file was created
        cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
        assert os.path.exists(cache_path)
        
        # Verify cache content
        with open(cache_path, 'r') as f:
            cached_data = json.load(f)
        
        assert cached_data['rate'] == sample_exchange_rate['rate']
        assert 'timestamp' in cached_data
        assert cached_data['source'] == 'api'
    
    def test_cache_rate_file_error(self, temp_data_dir):
        """Test cache saving with file write error"""
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            # Should not raise exception, just fail silently
            cache_rate(0.85)
    
    def test_get_cached_rate_success(self, temp_data_dir):
        """Test successful rate loading from cache"""
        # Create cache file
        cache_data = {
            'rate': 0.8542,
            'timestamp': datetime.now().isoformat(),
            'source': 'api'
        }
        
        cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)
        
        loaded_rate = get_cached_rate()
        
        assert loaded_rate == cache_data['rate']
    
    def test_get_cached_rate_missing_file(self, temp_data_dir):
        """Test loading from non-existent cache file"""
        result = get_cached_rate()
        assert result is None
    
    def test_get_cached_rate_corrupted_file(self, temp_data_dir):
        """Test loading from corrupted cache file"""
        cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
        with open(cache_path, 'w') as f:
            f.write('{"corrupted": json}')
        
        result = get_cached_rate()
        assert result is None
    
    def test_get_cached_rate_missing_fields(self, temp_data_dir):
        """Test loading from cache with missing required fields"""
        cache_data = {
            'timestamp': datetime.now().isoformat()
            # Missing 'rate' field
        }
        
        cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)
        
        result = get_cached_rate()
        assert result is None


class TestCacheValidation:
    """Test cache validity checking"""
    
    def test_cache_valid_fresh_cache(self, temp_data_dir):
        """Test cache validation with fresh data"""
        # Create fresh cache (5 minutes ago)
        cache_data = {
            'rate': 0.8542,
            'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
            'source': 'api'
        }
        
        cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)
        
        # Fresh cache should return a rate (not None)
        assert get_cached_rate() is not None
    
    def test_cache_invalid_expired_cache(self, temp_data_dir):
        """Test cache validation with expired data"""
        # Create expired cache (2 hours ago)
        cache_data = {
            'rate': 0.8542,
            'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
            'source': 'api'
        }
        
        cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)
        
        # Expired cache should return None
        assert get_cached_rate() is None
    
    def test_cache_edge_case_exactly_one_hour(self, temp_data_dir):
        """Test cache validation at exactly one hour boundary"""
        # Create cache exactly 1 hour ago
        cache_data = {
            'rate': 0.8542,
            'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
            'source': 'api'
        }
        
        cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)
        
        # Should be invalid (>= 1 hour is expired) - returns None
        assert get_cached_rate() is None
    
    def test_cache_no_cache_file(self, temp_data_dir):
        """Test cache validation with no cache file"""
        # No cache file should return None
        assert get_cached_rate() is None
    
    def test_cache_corrupted_cache(self, temp_data_dir):
        """Test cache validation with corrupted cache file"""
        cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
        with open(cache_path, 'w') as f:
            f.write('{"invalid": json}')
        
        # Corrupted cache should return None
        assert get_cached_rate() is None
    
    def test_cache_invalid_timestamp(self, temp_data_dir):
        """Test cache validation with invalid timestamp format"""
        cache_data = {
            'rate': 0.8542,
            'timestamp': 'invalid-timestamp-format',
            'source': 'api'
        }
        
        cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)
        
        # Invalid timestamp should return None
        assert get_cached_rate() is None


class TestAPIFetching:
    """Test exchange rate API fetching"""
    
    def test_fetch_rate_from_api_success(self, mock_exchange_api):
        """Test successful API rate fetching"""
        rate = fetch_rate_from_api()
        
        assert rate == 0.8542
        mock_exchange_api.assert_called_once()
        
        # Verify correct API endpoint was called
        args, kwargs = mock_exchange_api.call_args
        assert 'https://api.exchangerate-api.com/v4/latest/USD' in args[0]
    
    def test_fetch_rate_from_api_network_error(self):
        """Test API fetching with network error"""
        with patch('requests.get', side_effect=requests.RequestException("Network error")):
            rate = fetch_rate_from_api()
            assert rate is None
    
    def test_fetch_rate_from_api_timeout(self):
        """Test API fetching with timeout"""
        with patch('requests.get', side_effect=requests.Timeout("Request timeout")):
            rate = fetch_rate_from_api()
            assert rate is None
    
    def test_fetch_rate_from_api_http_error(self):
        """Test API fetching with HTTP error status"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
            mock_get.return_value = mock_response
            
            rate = fetch_rate_from_api()
            assert rate is None
    
    def test_fetch_rate_from_api_invalid_response_structure(self):
        """Test API fetching with invalid response structure"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                'invalid': 'structure'
                # Missing 'rates' field
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            rate = fetch_rate_from_api()
            assert rate is None
    
    def test_fetch_rate_from_api_missing_eur_rate(self):
        """Test API fetching when EUR rate is missing"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                'rates': {
                    'GBP': 0.7583,
                    'JPY': 110.0
                    # Missing 'EUR'
                }
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            rate = fetch_rate_from_api()
            assert rate is None
    
    def test_fetch_rate_from_api_json_decode_error(self):
        """Test API fetching with JSON decode error"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            rate = fetch_rate_from_api()
            assert rate is None
    
    def test_fetch_rate_from_api_unexpected_exception(self):
        """Test API fetching with unexpected exception"""
        with patch('requests.get', side_effect=Exception("Unexpected error")):
            rate = fetch_rate_from_api()
            assert rate is None


class TestMainFunction:
    """Test main get_exchange_rate function"""
    
    def test_get_rate_with_valid_cache(self, temp_data_dir):
        """Test getting rate when cache is valid"""
        # Create valid cache
        cache_data = {
            'rate': 0.8542,
            'timestamp': (datetime.now() - timedelta(minutes=30)).isoformat(),
            'source': 'api'
        }
        
        cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)
        
        with patch('utils.currency.fetch_rate_from_api') as mock_api:
            rate = get_exchange_rate()
            
            assert rate == 0.8542
            # API should not be called when cache is valid
            mock_api.assert_not_called()
    
    def test_get_rate_with_expired_cache_api_success(self, temp_data_dir, mock_exchange_api):
        """Test getting rate when cache is expired but API succeeds"""
        # Create expired cache
        cache_data = {
            'rate': 0.8000,  # Old rate
            'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
            'source': 'api'
        }
        
        cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)
        
        rate = get_exchange_rate()
        
        # Should get new rate from API
        assert rate == 0.8542
        mock_exchange_api.assert_called_once()
    
    def test_get_rate_with_expired_cache_api_failure(self, temp_data_dir):
        """Test getting rate when cache is expired and API fails"""
        # Create expired cache
        cache_data = {
            'rate': 0.8000,
            'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
            'source': 'api'
        }
        
        cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)
        
        with patch('utils.currency.fetch_rate_from_api', return_value=None):
            rate = get_exchange_rate()
            
            # Should fall back to fallback rate when cache expired and API fails
            assert rate == FALLBACK_RATE
    
    def test_get_rate_no_cache_api_success(self, temp_data_dir, mock_exchange_api):
        """Test getting rate when no cache exists and API succeeds"""
        rate = get_exchange_rate()
        
        assert rate == 0.8542
        mock_exchange_api.assert_called_once()
    
    def test_get_rate_no_cache_api_failure(self, temp_data_dir):
        """Test getting rate when no cache exists and API fails"""
        with patch('utils.currency.fetch_rate_from_api', return_value=None):
            rate = get_exchange_rate()
            
            # Should return fallback rate
            assert rate == FALLBACK_RATE
    
    def test_get_rate_cache_corruption_api_success(self, temp_data_dir, mock_exchange_api):
        """Test getting rate when cache is corrupted but API succeeds"""
        # Create corrupted cache
        cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
        with open(cache_path, 'w') as f:
            f.write('{"corrupted": json}')
        
        rate = get_exchange_rate()
        
        assert rate == 0.8542
        mock_exchange_api.assert_called_once()
    
    def test_get_rate_cache_corruption_api_failure(self, temp_data_dir):
        """Test getting rate when cache is corrupted and API fails"""
        # Create corrupted cache
        cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
        with open(cache_path, 'w') as f:
            f.write('{"corrupted": json}')
        
        with patch('utils.currency.fetch_rate_from_api', return_value=None):
            rate = get_exchange_rate()
            
            # Should return fallback rate
            assert rate == FALLBACK_RATE


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_extreme_exchange_rates(self, temp_data_dir):
        """Test with extreme exchange rate values"""
        extreme_rates = [0.0001, 999999.0, 0.5, 2.0]
        
        for test_rate in extreme_rates:
            # Clear cache before each iteration to ensure fresh API call
            cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
            if os.path.exists(cache_path):
                os.remove(cache_path)
                
            with patch('utils.currency.fetch_rate_from_api', return_value=test_rate):
                rate = get_exchange_rate()
                assert rate == test_rate
    
    def test_zero_exchange_rate(self, temp_data_dir):
        """Test with zero exchange rate from API"""
        with patch('utils.currency.fetch_rate_from_api', return_value=0.0):
            rate = get_exchange_rate()
            # Zero rate should be considered valid (though unrealistic)
            assert rate == 0.0
    
    def test_negative_exchange_rate(self, temp_data_dir):
        """Test with negative exchange rate from API"""
        with patch('utils.currency.fetch_rate_from_api', return_value=-0.5):
            rate = get_exchange_rate()
            # Negative rate should be considered valid by the module
            assert rate == -0.5
    
    def test_very_old_cache(self, temp_data_dir):
        """Test with very old cache data"""
        # Create cache from last year
        cache_data = {
            'rate': 0.7500,
            'timestamp': (datetime.now() - timedelta(days=365)).isoformat(),
            'source': 'api'
        }
        
        cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)
        
        with patch('utils.currency.fetch_rate_from_api', return_value=None):
            rate = get_exchange_rate()
            
            # Should return fallback rate when very old cache and API fails
            assert rate == FALLBACK_RATE
    
    def test_future_timestamp_cache(self, temp_data_dir):
        """Test with cache that has future timestamp"""
        # Create cache with future timestamp
        cache_data = {
            'rate': 0.8800,
            'timestamp': (datetime.now() + timedelta(hours=1)).isoformat(),
            'source': 'api'
        }
        
        cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)
        
        # Future timestamp should be considered valid - cache should return the rate
        assert get_cached_rate() is not None
        
        with patch('utils.currency.fetch_rate_from_api') as mock_api:
            rate = get_exchange_rate()
            
            assert rate == 0.8800
            mock_api.assert_not_called()


class TestConcurrency:
    """Test concurrent access and file locking scenarios"""
    
    def test_simultaneous_cache_write(self, temp_data_dir):
        """Test behavior when cache is written simultaneously"""
        # This tests the resilience of the caching mechanism
        # when multiple processes might be writing at the same time
        
        def write_cache():
            cache_rate(0.8500)
        
        # Simulate concurrent writes
        import threading
        threads = []
        for i in range(5):
            t = threading.Thread(target=write_cache)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Should have a valid cache file after all writes
        rate = get_cached_rate()
        assert rate == 0.8500
    
    def test_cache_read_during_write(self, temp_data_dir):
        """Test reading cache while it's being written"""
        import threading
        import time
        
        def slow_write():
            # Simulate slow write operation
            cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
            with open(cache_path, 'w') as f:
                f.write('{"rate": 0.8')
                time.sleep(0.1)  # Delay to simulate incomplete write
                f.write('500, "timestamp": "' + datetime.now().isoformat() + '", "source": "api"}')
        
        write_thread = threading.Thread(target=slow_write)
        write_thread.start()
        
        time.sleep(0.05)  # Start reading while write is in progress
        
        # Should handle incomplete file gracefully
        rate = get_cached_rate()
        # Might be None due to incomplete JSON, which is acceptable
        
        write_thread.join()
        
        # After write completes, should be able to read
        rate = get_cached_rate()
        assert rate == 0.8500


class TestFallbackBehavior:
    """Test fallback rate behavior"""
    
    def test_fallback_rate_constant(self):
        """Test that fallback rate is reasonable"""
        # Verify fallback rate is within reasonable bounds for EUR/USD
        assert 0.5 <= FALLBACK_RATE <= 1.5
        assert isinstance(FALLBACK_RATE, float)
    
    def test_fallback_used_when_all_fails(self, temp_data_dir):
        """Test fallback is used when both cache and API fail"""
        # No cache file exists
        # API returns None
        with patch('utils.currency.fetch_rate_from_api', return_value=None):
            rate = get_exchange_rate()
            assert rate == FALLBACK_RATE
    
    def test_fallback_not_used_when_cache_available(self, temp_data_dir):
        """Test fallback is not used when cache is available"""
        # Create valid cache
        cache_data = {
            'rate': 0.9000,
            'timestamp': datetime.now().isoformat(),
            'source': 'api'
        }
        
        cache_path = os.path.join(temp_data_dir, 'exchange_rates.json')
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f)
        
        with patch('utils.currency.fetch_rate_from_api', return_value=None):
            rate = get_exchange_rate()
            # Should use cache, not fallback
            assert rate == 0.9000
            assert rate != FALLBACK_RATE


class TestAPITimeout:
    """Test API timeout behavior"""
    
    def test_api_request_has_timeout(self):
        """Test that API requests include timeout"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {'rates': {'EUR': 0.85}}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            fetch_rate_from_api()
            
            # Verify timeout was specified
            args, kwargs = mock_get.call_args
            assert 'timeout' in kwargs
            assert kwargs['timeout'] == 5  # Should be 5 seconds
    
    def test_api_timeout_behavior(self):
        """Test behavior when API times out"""
        with patch('requests.get', side_effect=requests.Timeout("Request timed out")):
            rate = fetch_rate_from_api()
            assert rate is None 