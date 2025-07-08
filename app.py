from flask import Flask, render_template, request, jsonify
import os
from utils.data_manager import load_config, save_config, load_assets, save_assets
from utils.calculations import calculate_realized_income, calculate_potential_income, calculate_global_position, get_monthly_progress, calculate_total_assets
from utils.currency import get_exchange_rate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mindbank_secret_key_2024'

@app.route('/')
def dashboard():
    """Main dashboard page"""
    try:
        config = load_config()
        assets = load_assets()
        
        # Calculate income components
        realized_income = calculate_realized_income(config.get('monthly_salary', 0))
        potential_income = calculate_potential_income(
            config.get('monthly_salary', 0), 
            config.get('daily_goal_percentage', 0)
        )
        
        # Calculate global position
        global_position = calculate_global_position(assets, realized_income, potential_income)
        
        return render_template('dashboard.html', 
                             config=config,
                             assets=assets,
                             realized_income=realized_income,
                             potential_income=potential_income,
                             global_position=global_position)
    except Exception as e:
        # If no config exists, redirect to config page
        return render_template('dashboard.html', 
                             config={},
                             assets={},
                             realized_income=0,
                             potential_income=0,
                             global_position=0,
                             first_time=True)

@app.route('/config')
def config():
    """Configuration page"""
    try:
        config = load_config()
        assets = load_assets()
    except:
        config = {}
        assets = {}
    
    return render_template('config.html', config=config, assets=assets)

@app.route('/api/update-assets', methods=['POST'])
def update_assets():
    """Update asset values"""
    try:
        # Check if request has JSON data
        if not request.is_json:
            return jsonify({'success': False, 'error': 'JSON data required'}), 400
        
        data = request.get_json()
        if data is None:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        required_fields = ['bank_balance', 'cash_eur', 'cash_usd', 'investments']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Validate and convert input
        assets = {}
        for field in required_fields:
            try:
                assets[field] = float(data[field])
            except (ValueError, TypeError):
                return jsonify({'success': False, 'error': f'Invalid value for {field}: must be a number'}), 400
        
        # Try to save assets
        try:
            save_assets(assets)
        except Exception as save_error:
            return jsonify({'success': False, 'error': f'Failed to save assets: {str(save_error)}'}), 500
        
        return jsonify({'success': True, 'message': 'Assets updated successfully', 'assets': assets})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/update-config', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        # Check if request has JSON data
        if not request.is_json:
            return jsonify({'success': False, 'error': 'JSON data required'}), 400
        
        data = request.get_json()
        if data is None:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        required_fields = ['monthly_salary', 'daily_goal_percentage']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Validate and convert input
        try:
            monthly_salary = float(data['monthly_salary'])
            daily_goal_percentage = float(data['daily_goal_percentage'])
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Invalid numeric values provided'}), 400
        
        # Validate ranges
        if monthly_salary < 0:
            return jsonify({'success': False, 'error': 'Monthly salary must be non-negative'}), 400
        if not 0 <= daily_goal_percentage <= 100:
            return jsonify({'success': False, 'error': 'Daily goal percentage must be between 0 and 100'}), 400
        
        config = {
            'monthly_salary': monthly_salary,
            'daily_goal_percentage': daily_goal_percentage
        }
        
        # Try to save config
        try:
            save_config(config)
        except Exception as save_error:
            return jsonify({'success': False, 'error': f'Failed to save configuration: {str(save_error)}'}), 500
        
        return jsonify({'success': True, 'message': 'Configuration updated successfully', 'config': config})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/daily-goal', methods=['POST'])
def update_daily_goal():
    """Update daily goal percentage and return new calculations"""
    try:
        # Check if request has JSON data
        if not request.is_json:
            return jsonify({'success': False, 'error': 'JSON data required'}), 400
        
        data = request.get_json()
        if data is None:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        # Validate goal_percentage field
        if 'goal_percentage' not in data:
            return jsonify({'success': False, 'error': 'Missing required field: goal_percentage'}), 400
        
        try:
            goal_percentage = float(data['goal_percentage'])
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Invalid goal_percentage: must be a number'}), 400
        
        # Validate percentage range
        if not 0 <= goal_percentage <= 100:
            return jsonify({'success': False, 'error': 'Goal percentage must be between 0 and 100'}), 400
        
        # Load current config and update goal percentage
        try:
            config = load_config()
            config['daily_goal_percentage'] = goal_percentage
            save_config(config)
        except Exception as config_error:
            return jsonify({'success': False, 'error': f'Failed to update configuration: {str(config_error)}'}), 500
        
        # Recalculate everything
        try:
            assets = load_assets()
            realized_income = calculate_realized_income(config.get('monthly_salary', 0))
            potential_income = calculate_potential_income(config.get('monthly_salary', 0), goal_percentage)
            global_position = calculate_global_position(assets, realized_income, potential_income)
        except Exception as calc_error:
            return jsonify({'success': False, 'error': f'Failed to calculate values: {str(calc_error)}'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Daily goal updated successfully',
            'potential_income': potential_income,
            'global_position': global_position,
            'goal_percentage': goal_percentage
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/dashboard-data')
def get_dashboard_data():
    """Get current dashboard data for AJAX refresh"""
    try:
        # Load data with error handling
        try:
            config = load_config()
            assets = load_assets()
        except Exception as load_error:
            return jsonify({'success': False, 'error': f'Failed to load data: {str(load_error)}'}), 500
        
        # Get exchange rate
        try:
            exchange_rate = get_exchange_rate()
        except Exception:
            exchange_rate = None  # Fallback to no conversion
        
        # Calculate values with error handling
        try:
            realized_income = calculate_realized_income(config.get('monthly_salary', 0))
            potential_income = calculate_potential_income(
                config.get('monthly_salary', 0), 
                config.get('daily_goal_percentage', 0)
            )
            global_position = calculate_global_position(assets, realized_income, potential_income, exchange_rate)
            monthly_progress = get_monthly_progress()
        except Exception as calc_error:
            return jsonify({'success': False, 'error': f'Failed to calculate values: {str(calc_error)}'}), 500
        
        response_data = {
            'success': True,
            'config': config,
            'assets': assets,
            'calculations': {
                'realized_income': realized_income,
                'potential_income': potential_income,
                'global_position': global_position,
                'monthly_progress': monthly_progress,
                'total_assets': calculate_total_assets(assets, exchange_rate)
            },
            'realized_income': realized_income,
            'potential_income': potential_income,
            'global_position': global_position
        }
        
        if exchange_rate is not None:
            response_data['exchange_rate'] = exchange_rate
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/exchange-rate')
def get_current_exchange_rate():
    """Get current USD to EUR exchange rate"""
    try:
        import datetime
        rate = get_exchange_rate()
        timestamp = datetime.datetime.now().isoformat()
        return jsonify({'success': True, 'rate': rate, 'source': 'exchangerate-api', 'timestamp': timestamp})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5555) 