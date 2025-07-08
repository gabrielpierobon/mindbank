/**
 * MindBank JavaScript Application
 * Handles real-time calculations, AJAX interactions, and UI updates
 */

class MindBankApp {
    constructor() {
        this.isLoading = false;
        this.debounceTimeout = null;
        this.currentExchangeRate = 0.85; // Fallback rate
        
        // Initialize the application
        this.init();
    }
    
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.onDOMReady());
        } else {
            this.onDOMReady();
        }
    }
    
    onDOMReady() {
        console.log('MindBank App Initialized');
        
        // Initialize common functionality
        this.initializeNotifications();
        this.setupErrorHandling();
        
        // Load exchange rate information
        this.loadExchangeRate();
        
        // Initialize page-specific functionality based on current page
        const currentPage = this.getCurrentPage();
        if (currentPage === 'dashboard') {
            this.initializeDashboard();
        } else if (currentPage === 'config') {
            this.initializeConfig();
        }
    }
    
    getCurrentPage() {
        const path = window.location.pathname;
        if (path === '/' || path === '/dashboard') {
            return 'dashboard';
        } else if (path === '/config') {
            return 'config';
        }
        return 'unknown';
    }
    
    // =====================================
    // Dashboard Functionality
    // =====================================
    
    initializeDashboard() {
        console.log('Initializing Dashboard');
        
        // Initialize goal slider
        this.initializeGoalSlider();
        
        // Update monthly progress display
        this.updateMonthlyProgress();
        
        // Setup refresh button
        this.setupRefreshButton();
        
        // Auto-refresh exchange rate and calculations every 5 minutes
        setInterval(() => {
            this.refreshExchangeRate();
            this.refreshDashboardData();
        }, 5 * 60 * 1000);
    }
    
    initializeGoalSlider() {
        const goalSlider = document.getElementById('goal-slider');
        if (!goalSlider) return;
        
        // Update percentage display when slider moves
        goalSlider.addEventListener('input', (e) => {
            const percentage = e.target.value;
            this.updateGoalPercentageDisplay(percentage);
            
            // Debounced update to server
            this.debouncedGoalUpdate(percentage);
        });
        
        // Also handle change event for better compatibility
        goalSlider.addEventListener('change', (e) => {
            const percentage = e.target.value;
            this.updateGoalOnServer(percentage);
        });
        
        // Initialize display
        this.updateGoalPercentageDisplay(goalSlider.value);
    }
    
    updateGoalPercentageDisplay(percentage) {
        const display = document.getElementById('goal-percentage');
        if (display) {
            display.textContent = `${percentage}%`;
        }
    }
    
    debouncedGoalUpdate(percentage) {
        // Clear existing timeout
        if (this.debounceTimeout) {
            clearTimeout(this.debounceTimeout);
        }
        
        // Set new timeout
        this.debounceTimeout = setTimeout(() => {
            this.updateGoalOnServer(percentage);
        }, 500); // 500ms delay
    }
    
    async updateGoalOnServer(percentage) {
        try {
            this.showLoading();
            
            const response = await fetch('/api/daily-goal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    goal_percentage: parseFloat(percentage)
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Update UI with new calculations
                this.updatePotentialIncome(data.potential_income);
                this.updateGlobalPosition(data.global_position);
                
                this.showNotification('Goal updated successfully!', 'success');
            } else {
                this.showNotification(data.message || 'Failed to update goal', 'error');
            }
            
        } catch (error) {
            console.error('Error updating goal:', error);
            this.showNotification('Network error. Please try again.', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    updatePotentialIncome(amount) {
        const elements = [
            document.getElementById('potential-income'),
            document.getElementById('potential-display')
        ];
        
        elements.forEach(el => {
            if (el) {
                el.textContent = `€${this.formatCurrency(amount)}`;
            }
        });
    }
    
    updateGlobalPosition(amount) {
        const element = document.getElementById('global-position');
        if (element) {
            element.textContent = `€${this.formatCurrency(amount)}`;
        }
    }
    
    updateMonthlyProgress() {
        const now = new Date();
        const currentDay = now.getDate();
        const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
        const progressPercentage = (currentDay / daysInMonth) * 100;
        
        // Update date display
        const dateElement = document.getElementById('current-date');
        if (dateElement) {
            dateElement.textContent = now.toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }
        
        // Update progress stats
        const daysPassed = document.getElementById('days-passed');
        const daysRemaining = document.getElementById('days-remaining');
        const monthProgress = document.getElementById('month-progress');
        const monthPercentage = document.getElementById('month-percentage');
        
        if (daysPassed) daysPassed.textContent = currentDay;
        if (daysRemaining) daysRemaining.textContent = daysInMonth - currentDay;
        if (monthProgress) monthProgress.style.width = `${progressPercentage}%`;
        if (monthPercentage) monthPercentage.textContent = `${Math.round(progressPercentage)}%`;
    }
    
    setupRefreshButton() {
        const refreshButton = document.getElementById('refresh-data');
        if (!refreshButton) return;
        
        refreshButton.addEventListener('click', async () => {
            await this.refreshDashboardData();
            await this.refreshExchangeRate();
        });
    }
    
    async refreshDashboardData() {
        try {
            this.showLoading();
            
            const response = await fetch('/api/dashboard-data');
            const data = await response.json();
            
            if (data.success) {
                // Update all dashboard values
                this.updateGlobalPosition(data.global_position);
                this.updatePotentialIncome(data.potential_income);
                
                // Update realized income
                const realizedElement = document.querySelector('.income-card.realized .income-amount');
                if (realizedElement) {
                    realizedElement.textContent = `€${this.formatCurrency(data.realized_income)}`;
                }
                
                // Update goal slider
                const goalSlider = document.getElementById('goal-slider');
                if (goalSlider && data.config.daily_goal_percentage !== undefined) {
                    goalSlider.value = data.config.daily_goal_percentage;
                    this.updateGoalPercentageDisplay(data.config.daily_goal_percentage);
                }
                
                this.showNotification('Dashboard data refreshed!', 'success');
            } else {
                this.showNotification(data.message || 'Failed to refresh data', 'error');
            }
            
        } catch (error) {
            console.error('Error refreshing dashboard:', error);
            this.showNotification('Failed to refresh dashboard data', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    // =====================================
    // Configuration Functionality
    // =====================================
    
    initializeConfig() {
        console.log('Initializing Configuration');
        
        // Initialize forms
        this.initializeIncomeForm();
        this.initializeAssetsForm();
        this.initializeGoalPercentageSync();
        
        // Setup exchange rate refresh
        this.setupExchangeRateRefresh();
        
        // Load and display exchange rate info
        this.updateExchangeRateDisplay();
    }
    
    initializeIncomeForm() {
        const form = document.getElementById('income-form');
        if (!form) return;
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.saveIncomeConfig(form);
        });
        
        // Real-time summary updates
        const salaryInput = document.getElementById('monthly-salary');
        if (salaryInput) {
            salaryInput.addEventListener('input', () => {
                this.updateSummaryDisplay();
            });
        }
    }
    
    initializeAssetsForm() {
        const form = document.getElementById('assets-form');
        if (!form) return;
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.saveAssetsConfig(form);
        });
        
        // Real-time summary updates
        const assetInputs = ['bank-balance', 'cash-eur', 'cash-usd', 'investments'];
        assetInputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', () => {
                    this.updateSummaryDisplay();
                    this.updateUsdConversion();
                });
            }
        });
    }
    
    initializeGoalPercentageSync() {
        const slider = document.getElementById('goal-percentage-slider');
        const input = document.getElementById('goal-percentage-input');
        
        if (slider && input) {
            // Sync slider to input
            slider.addEventListener('input', (e) => {
                input.value = e.target.value;
                this.updateSummaryDisplay();
            });
            
            // Sync input to slider
            input.addEventListener('input', (e) => {
                const value = Math.max(0, Math.min(100, parseInt(e.target.value) || 0));
                e.target.value = value;
                slider.value = value;
                this.updateSummaryDisplay();
            });
        }
    }
    
    async saveIncomeConfig(form) {
        try {
            this.showLoading();
            
            const formData = new FormData(form);
            const data = {
                monthly_salary: parseFloat(formData.get('monthly_salary')) || 0,
                daily_goal_percentage: parseFloat(formData.get('daily_goal_percentage')) || 0
            };
            
            const response = await fetch('/api/update-config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Income settings saved successfully!', 'success');
                this.updateSummaryDisplay();
            } else {
                this.showNotification(result.message || 'Failed to save income settings', 'error');
            }
            
        } catch (error) {
            console.error('Error saving income config:', error);
            this.showNotification('Network error. Please try again.', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    async saveAssetsConfig(form) {
        try {
            this.showLoading();
            
            const formData = new FormData(form);
            const data = {
                bank_balance: parseFloat(formData.get('bank_balance')) || 0,
                cash_eur: parseFloat(formData.get('cash_eur')) || 0,
                cash_usd: parseFloat(formData.get('cash_usd')) || 0,
                investments: parseFloat(formData.get('investments')) || 0
            };
            
            const response = await fetch('/api/update-assets', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Asset information saved successfully!', 'success');
                this.updateSummaryDisplay();
            } else {
                this.showNotification(result.message || 'Failed to save asset information', 'error');
            }
            
        } catch (error) {
            console.error('Error saving assets config:', error);
            this.showNotification('Network error. Please try again.', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    updateSummaryDisplay() {
        // Update salary summary
        const salaryInput = document.getElementById('monthly-salary');
        const salarySummary = document.getElementById('summary-salary');
        if (salaryInput && salarySummary) {
            const salary = parseFloat(salaryInput.value) || 0;
            salarySummary.textContent = `€${this.formatCurrency(salary)}`;
            
            // Update daily income potential
            const dailySummary = document.getElementById('summary-daily');
            if (dailySummary) {
                const dailyIncome = salary / 30;
                dailySummary.textContent = `€${this.formatCurrency(dailyIncome)}`;
            }
        }
        
        // Update assets summary
        const bankBalance = parseFloat(document.getElementById('bank-balance')?.value) || 0;
        const cashEur = parseFloat(document.getElementById('cash-eur')?.value) || 0;
        const cashUsd = parseFloat(document.getElementById('cash-usd')?.value) || 0;
        const investments = parseFloat(document.getElementById('investments')?.value) || 0;
        
        const totalAssets = bankBalance + cashEur + (cashUsd * this.currentExchangeRate) + investments;
        
        const assetsSummary = document.getElementById('summary-assets');
        if (assetsSummary) {
            assetsSummary.textContent = `€${this.formatCurrency(totalAssets)}`;
        }
        
        // Update goal summary
        const goalInput = document.getElementById('goal-percentage-input');
        const goalSummary = document.getElementById('summary-goal');
        if (goalInput && goalSummary) {
            goalSummary.textContent = `${goalInput.value}%`;
        }
    }
    
    updateUsdConversion() {
        const usdInput = document.getElementById('cash-usd');
        const conversionInfo = document.getElementById('usd-conversion-info');
        
        if (usdInput && conversionInfo) {
            const usdAmount = parseFloat(usdInput.value) || 0;
            const eurAmount = usdAmount * this.currentExchangeRate;
            conversionInfo.textContent = `≈ €${this.formatCurrency(eurAmount)} (Rate: $1 = €${this.currentExchangeRate.toFixed(4)})`;
        }
    }
    
    setupExchangeRateRefresh() {
        const refreshButton = document.getElementById('refresh-exchange-rate');
        if (!refreshButton) return;
        
        refreshButton.addEventListener('click', async () => {
            await this.refreshExchangeRate();
            this.updateSummaryDisplay();
            this.updateUsdConversion();
        });
    }
    
    // =====================================
    // Exchange Rate Functionality
    // =====================================
    
    async loadExchangeRate() {
        try {
            const response = await fetch('/api/exchange-rate');
            const data = await response.json();
            
            if (data.success) {
                this.currentExchangeRate = data.rate;
                this.updateUsdConversion();
            }
        } catch (error) {
            console.warn('Failed to load exchange rate:', error);
        }
    }
    
    async refreshExchangeRate() {
        try {
            this.showLoading();
            
            // Force refresh by calling the currency refresh endpoint
            const response = await fetch('/api/exchange-rate');
            const data = await response.json();
            
            if (data.success) {
                this.currentExchangeRate = data.rate;
                this.updateExchangeRateDisplay();
                this.updateUsdConversion();
                this.showNotification('Exchange rate updated!', 'success');
            } else {
                this.showNotification('Failed to update exchange rate', 'warning');
            }
            
        } catch (error) {
            console.error('Error refreshing exchange rate:', error);
            this.showNotification('Failed to refresh exchange rate', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    updateExchangeRateDisplay() {
        const rateValue = document.getElementById('current-rate');
        const rateTimestamp = document.getElementById('rate-timestamp');
        const rateSource = document.getElementById('rate-source');
        
        if (rateValue) {
            rateValue.textContent = `$1 = €${this.currentExchangeRate.toFixed(4)}`;
        }
        
        if (rateTimestamp) {
            rateTimestamp.textContent = new Date().toLocaleString();
        }
        
        if (rateSource) {
            rateSource.textContent = 'API/Cache';
        }
    }
    
    // =====================================
    // Utility Functions
    // =====================================
    
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    }
    
    showLoading() {
        this.isLoading = true;
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('hidden');
        }
    }
    
    hideLoading() {
        this.isLoading = false;
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }
    
    showNotification(message, type = 'info') {
        const notificationArea = document.getElementById('notification-area');
        if (!notificationArea) return;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        notificationArea.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    initializeNotifications() {
        // Clear any existing notifications on page load
        const notificationArea = document.getElementById('notification-area');
        if (notificationArea) {
            notificationArea.innerHTML = '';
        }
    }
    
    setupErrorHandling() {
        // Global error handler for uncaught errors
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.showNotification('An unexpected error occurred', 'error');
        });
        
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.showNotification('A network error occurred', 'error');
        });
    }
}

// Initialize the application when the script loads
window.mindBankApp = new MindBankApp();

// Export for potential use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MindBankApp;
} 