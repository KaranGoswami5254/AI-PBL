// Reports specific functionality
class Reports {
    static init() {
        this.initCharts();
        this.renderExpenseData();
        this.setupPrintButton();
        this.showBudgetAlerts();
    }

    static initCharts() {
        // Category Chart
        const categoryCtx = document.getElementById('categoryChart')?.getContext('2d');
        if (categoryCtx) {
            ChartUtils.initCategoryChart(categoryCtx, reportsData.categories);
        }

        // Monthly Chart
        const monthlyCtx = document.getElementById('monthlyChart')?.getContext('2d');
        if (monthlyCtx) {
            ChartUtils.initMonthlyChart(monthlyCtx, reportsData.monthlyData);
        }
    }

    static renderExpenseData() {
        const tbody = document.querySelector('#expense-data tbody');
        if (!tbody) return;

        tbody.innerHTML = Object.entries(reportsData.categories).map(([category, amount]) => {
            const percentage = (amount / reportsData.totalSpent * 100).toFixed(1);
            
            // Find matching budget if exists
            let budgetInfo = 'No budget set';
            const budget = reportsData.budgets.find(b => b.category === category);
            if (budget) {
                budgetInfo = `$${budget.amount.toFixed(2)} (${budget.period})`;
            }

            return `
                <tr>
                    <td>${category}</td>
                    <td>$${amount.toFixed(2)}</td>
                    <td>${percentage}%</td>
                    <td>${budgetInfo}</td>
                </tr>
            `;
        }).join('');
    }

    static setupPrintButton() {
        document.querySelector('.print-btn')?.addEventListener('click', () => {
            window.print();
        });
    }

    static showBudgetAlerts() {
        reportsData.budgets.forEach(budget => {
            const spent = reportsData.categories[budget.category] || 0;
    
            if (spent > budget.amount) {
                alert(`⚠️ Budget exceeded for "${budget.category}"!
    Spent: $${spent.toFixed(2)} | Budget: $${budget.amount.toFixed(2)}`);
            }
        });
    }
    
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => Reports.init());
