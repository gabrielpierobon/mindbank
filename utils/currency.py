import requests
import json
import os
from datetime import datetime, timedelta

# Cache file for exchange rates
CACHE_FILE = 'data/exchange_rates.json'
CACHE_DURATION_HOURS = 1  # Cache rates for 1 hour

# Fallback exchange rate (approximate USD to EUR)
FALLBACK_RATE = 0.85

def get_exchange_rate():
    """
    Get USD to EUR exchange rate with caching and fallback
    """
    try:
        # Try to get from cache first
        cached_rate = get_cached_rate()
        if cached_rate:
            return cached_rate
        
        # Fetch from API if cache is stale or doesn't exist
        api_rate = fetch_rate_from_api()
        if api_rate:
            cache_rate(api_rate)
            return api_rate
        
        # Fallback to static rate
        return FALLBACK_RATE
    
    except Exception as e:
        return FALLBACK_RATE

def get_cached_rate():
    """Get exchange rate from cache if still valid"""
    try:
        if not os.path.exists(CACHE_FILE):
            return None
        
        with open(CACHE_FILE, 'r') as f:
            cache_data = json.load(f)
        
        # Check if cache is still valid
        cached_time = datetime.fromisoformat(cache_data['timestamp'])
        now = datetime.now()
        
        if now - cached_time < timedelta(hours=CACHE_DURATION_HOURS):
            return cache_data['rate']
        
        return None
    
    except Exception as e:
        return None

def cache_rate(rate):
    """Cache the exchange rate with timestamp"""
    try:
        os.makedirs('data', exist_ok=True)
        
        cache_data = {
            'rate': rate,
            'timestamp': datetime.now().isoformat(),
            'source': 'api'
        }
        
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=4)
    
    except Exception as e:
        pass  # Fail silently if caching doesn't work

def fetch_rate_from_api():
    """
    Fetch exchange rate from a free API
    Using exchangerate-api.com (free tier: 1500 requests/month)
    """
    try:
        # Free API endpoint (no API key required for basic usage)
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        eur_rate = data['rates'].get('EUR')
        
        if eur_rate and isinstance(eur_rate, (int, float)):
            return round(eur_rate, 4)
        
        return None
    
    except requests.exceptions.RequestException:
        # Network error, timeout, etc.
        return None
    except (KeyError, ValueError, json.JSONDecodeError):
        # API response format error
        return None
    except Exception as e:
        # Any other error
        return None

def get_rate_info():
    """Get information about the current exchange rate and its source"""
    try:
        if not os.path.exists(CACHE_FILE):
            return {
                'rate': FALLBACK_RATE,
                'source': 'fallback',
                'last_updated': 'Never',
                'cache_valid': False
            }
        
        with open(CACHE_FILE, 'r') as f:
            cache_data = json.load(f)
        
        cached_time = datetime.fromisoformat(cache_data['timestamp'])
        now = datetime.now()
        cache_valid = now - cached_time < timedelta(hours=CACHE_DURATION_HOURS)
        
        return {
            'rate': cache_data.get('rate', FALLBACK_RATE),
            'source': cache_data.get('source', 'unknown'),
            'last_updated': cache_data.get('timestamp', 'Unknown'),
            'cache_valid': cache_valid,
            'cache_age_minutes': int((now - cached_time).total_seconds() / 60)
        }
    
    except Exception as e:
        return {
            'rate': FALLBACK_RATE,
            'source': 'fallback',
            'last_updated': 'Error',
            'cache_valid': False,
            'error': str(e)
        }

def convert_usd_to_eur(usd_amount):
    """Convert USD amount to EUR"""
    try:
        if not isinstance(usd_amount, (int, float)) or usd_amount < 0:
            return 0
        
        rate = get_exchange_rate()
        eur_amount = usd_amount * rate
        
        return round(eur_amount, 2)
    
    except Exception as e:
        return 0

def refresh_exchange_rate():
    """Force refresh of exchange rate from API"""
    try:
        # Remove cache file to force refresh
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        
        # Fetch new rate
        new_rate = fetch_rate_from_api()
        if new_rate:
            cache_rate(new_rate)
            return new_rate
        
        return FALLBACK_RATE
    
    except Exception as e:
        return FALLBACK_RATE 