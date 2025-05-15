// Dashboard specific functionality
class Dashboard {
    static init() {
        this.renderSummaryCards();
        this.renderRecentExpenses();
        this.renderBudgetOverview();
        this.initCategoryChart();
    }

    static renderSummaryCards() {
        const container = document.getElementById('summary-cards');
        if (!container) return;

        const cards = [
            {
                type: 'primary',
                icon: 'bi-cash-stack',
                value: `$${dashboardData.totalSpent.toFixed(2)}`,
                label: 'Total Spent'
            },
            {
                type: 'info',
                icon: 'bi-calendar-month',
                value: dashboardData.expenseCount,
                label: 'Expenses'
            },
            {
                type: 'success',
                icon: 'bi-wallet2',
                value: dashboardData.budgetCount,
                label: 'Budgets'
            },
            {
                type: 'danger',
                icon: 'bi-exclamation-triangle',
                value: '3',
                label: 'Alerts'
            }
        ];

        container.innerHTML = cards.map(card => `
            <div class="col-md-3">
                <div class="card-counter ${card.type}">
                    <i class="bi ${card.icon}"></i>
                    <span class="count-numbers">${card.value}</span>
                    <span class="count-name">${card.label}</span>
                </div>
            </div>
        `).join('');
    }

    static renderRecentExpenses() {
        const tbody = document.querySelector('#recent-expenses tbody');
        if (!tbody) return;

        tbody.innerHTML = dashboardData.recentExpenses.map(expense => `
            <tr>
                <td>${new Date(expense.date).toLocaleDateString()}</td>
                <td>${expense.category}</td>
                <td>$${expense.amount.toFixed(2)}</td>
            </tr>
        `).join('');
    }

    static renderBudgetOverview() {
        const tbody = document.querySelector('#budget-overview tbody');
        if (!tbody) return;

        tbody.innerHTML = dashboardData.budgets.map(budget => {
            const spent = dashboardData.categories[budget.category] || 0;
            const remaining = budget.amount - spent;
            const percent = (spent / budget.amount) * 100;
            
            let progressClass = 'bg-success';
            if (percent > 90) progressClass = 'bg-danger';
            else if (percent > 70) progressClass = 'bg-warning';

            return `
                <tr>
                    <td>${budget.category}</td>
                    <td>$${budget.amount.toFixed(2)}</td>
                    <td>$${spent.toFixed(2)}</td>
                    <td>$${remaining.toFixed(2)}</td>
                    <td>
                        <div class="progress">
                            <div class="progress-bar ${progressClass}" 
                                 role="progressbar" 
                                 style="width: ${percent}%" 
                                 aria-valuenow="${percent}" 
                                 aria-valuemin="0" 
                                 aria-valuemax="100">
                                ${Math.round(percent)}%
                            </div>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    }

    static initCategoryChart() {
        const ctx = document.getElementById('categoryChart')?.getContext('2d');
        if (ctx) {
            ChartUtils.initCategoryChart(ctx, dashboardData.categories);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => Dashboard.init());