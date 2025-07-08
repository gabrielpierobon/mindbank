from flask import Flask, render_template, request, jsonify
import os
from utils.data_manager import load_config, save_config, load_assets, save_assets
from utils.calculations import calculate_realized_income, calculate_potential_income, calculate_global_position
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
        data = request.get_json()
        
        # Validate input
        assets = {
            'bank_balance': float(data.get('bank_balance', 0)),
            'cash_eur': float(data.get('cash_eur', 0)),
            'cash_usd': float(data.get('cash_usd', 0)),
            'investments': float(data.get('investments', 0))
        }
        
        save_assets(assets)
        return jsonify({'success': True, 'message': 'Assets updated successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/update-config', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        data = request.get_json()
        
        config = {
            'monthly_salary': float(data.get('monthly_salary', 0)),
            'daily_goal_percentage': float(data.get('daily_goal_percentage', 0))
        }
        
        save_config(config)
        return jsonify({'success': True, 'message': 'Configuration updated successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/daily-goal', methods=['POST'])
def update_daily_goal():
    """Update daily goal percentage and return new calculations"""
    try:
        data = request.get_json()
        goal_percentage = float(data.get('goal_percentage', 0))
        
        # Validate percentage
        if not 0 <= goal_percentage <= 100:
            return jsonify({'success': False, 'message': 'Goal percentage must be between 0 and 100'}), 400
        
        # Load current config and update goal percentage
        config = load_config()
        config['daily_goal_percentage'] = goal_percentage
        save_config(config)
        
        # Recalculate everything
        assets = load_assets()
        realized_income = calculate_realized_income(config.get('monthly_salary', 0))
        potential_income = calculate_potential_income(config.get('monthly_salary', 0), goal_percentage)
        global_position = calculate_global_position(assets, realized_income, potential_income)
        
        return jsonify({
            'success': True,
            'potential_income': potential_income,
            'global_position': global_position,
            'goal_percentage': goal_percentage
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/dashboard-data')
def get_dashboard_data():
    """Get current dashboard data for AJAX refresh"""
    try:
        config = load_config()
        assets = load_assets()
        
        realized_income = calculate_realized_income(config.get('monthly_salary', 0))
        potential_income = calculate_potential_income(
            config.get('monthly_salary', 0), 
            config.get('daily_goal_percentage', 0)
        )
        global_position = calculate_global_position(assets, realized_income, potential_income)
        
        return jsonify({
            'success': True,
            'config': config,
            'assets': assets,
            'realized_income': realized_income,
            'potential_income': potential_income,
            'global_position': global_position
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/exchange-rate')
def get_current_exchange_rate():
    """Get current USD to EUR exchange rate"""
    try:
        rate = get_exchange_rate()
        return jsonify({'success': True, 'rate': rate})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000) 