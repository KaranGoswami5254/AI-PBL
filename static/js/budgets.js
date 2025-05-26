
class BudgetManager {
    static init() {
        this.currentEditId = null;
        this.renderBudgetsTable();
        this.setupForm();
        this.setupDeleteModal();
    }

    static renderBudgetsTable() {
        const tbody = document.querySelector('#budgets-table tbody');
        if (!tbody) return;

        tbody.innerHTML = budgetsData.budgets.map(budget => `
            <tr data-id="${budget.id}">
                <td>${budget.category}</td>
                <td>$${budget.amount.toFixed(2)}</td>
                <td>${this.formatPeriod(budget.period)}</td>
                <td class="budget-actions">
                    <button class="btn btn-sm btn-outline-primary edit-budget" 
                            data-id="${budget.id}">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger delete-budget" 
                            data-id="${budget.id}">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        this.setupTableEvents();
    }

    static formatPeriod(period) {
        const periods = {
            'weekly': 'Weekly',
            'monthly': 'Monthly',
            'yearly': 'Yearly'
        };
        return periods[period] || period;
    }

    static setupTableEvents() {
        document.querySelectorAll('.edit-budget').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const budgetId = e.currentTarget.dataset.id;
                this.editBudget(budgetId);
            });
        });

        document.querySelectorAll('.delete-budget').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const budgetId = e.currentTarget.dataset.id;
                this.prepareDelete(budgetId);
            });
        });
    }

    static editBudget(budgetId) {
        const budget = budgetsData.budgets.find(b => b.id == budgetId);
        if (!budget) return;

        this.currentEditId = budgetId;
        document.getElementById('budget-id').value = budgetId;
        document.getElementById('category').value = budget.category;
        document.getElementById('amount').value = budget.amount;
        document.getElementById('period').value = budget.period;
        
        document.getElementById('form-title').textContent = 'Edit Budget';
        document.getElementById('submit-btn').textContent = 'Update Budget';
        document.getElementById('cancel-btn').style.display = 'block';
        
        document.getElementById('category').focus();
    }

    static setupForm() {
        const form = document.getElementById('budget-form');
        if (!form) return;

        document.getElementById('cancel-btn').addEventListener('click', () => {
            this.resetForm();
        });

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            form.submit();
        });
    }

    static resetForm() {
        this.currentEditId = null;
        document.getElementById('budget-form').reset();
        document.getElementById('budget-id').value = '';
        document.getElementById('form-title').textContent = 'Add New Budget';
        document.getElementById('submit-btn').textContent = 'Save Budget';
        document.getElementById('cancel-btn').style.display = 'none';
    }

    static prepareDelete(budgetId) {
        this.currentDeleteId = budgetId;
        const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
        modal.show();
    }

    static setupDeleteModal() {
        document.getElementById('confirm-delete').addEventListener('click', () => {
            if (this.currentDeleteId) {
                window.location.href = `/delete_budget/${this.currentDeleteId}`;
            }
        });
    }
}


document.addEventListener('DOMContentLoaded', () => BudgetManager.init());