// Enhanced script.js for Smart Expense Tracker
document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initTooltips();
    initAutoClosingAlerts();
    initFormValidation();
    initDataFetching();
    initUIInteractions();
    initThemeToggle();
    initPrintButtons();
});

// Initialize Bootstrap tooltips
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            trigger: 'hover focus'
        });
    });
}

// Auto-close alerts with animation
function initAutoClosingAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
}

// Form validation with better UX
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Add shake animation to invalid fields
                const invalidFields = form.querySelectorAll(':invalid');
                invalidFields.forEach(field => {
                    field.style.animation = 'shake 0.5s';
                    setTimeout(() => {
                        field.style.animation = '';
                    }, 500);
                });
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// Data fetching with loading states
function initDataFetching() {
    // Update expense data with loading indicator
    updateExpenseData();
    
    // Set up periodic data refresh (every 2 minutes)
    setInterval(() => {
        updateExpenseData();
        updateCategoryData();
    }, 120000);
}

// Enhanced expense data fetching
async function updateExpenseData() {
    try {
        showLoading('#expenseTable');
        const response = await fetch('/api/expenses');
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        renderExpenseData(data);
    } catch (error) {
        console.error('Error fetching expense data:', error);
        showErrorToast('Failed to load expense data');
    } finally {
        hideLoading('#expenseTable');
    }
}

// Enhanced category data fetching
async function updateCategoryData() {
    try {
        showLoading('#categoryChartContainer');
        const response = await fetch('/api/expenses_by_category');
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        updateCategoryChart(data);
    } catch (error) {
        console.error('Error fetching category data:', error);
        showErrorToast('Failed to load category data');
    } finally {
        hideLoading('#categoryChartContainer');
    }
}

// Render expense data with animations
function renderExpenseData(data) {
    const tableBody = document.querySelector('#expenseTable tbody');
    if (!tableBody) return;
    
    // Clear existing rows with fade out
    const rows = tableBody.querySelectorAll('tr');
    rows.forEach(row => {
        row.style.transition = 'opacity 0.3s ease';
        row.style.opacity = '0';
        setTimeout(() => row.remove(), 300);
    });
    
    // Add new rows with fade in
    setTimeout(() => {
        data.forEach((expense, index) => {
            const row = document.createElement('tr');
            row.style.opacity = '0';
            row.style.transition = `opacity 0.3s ease ${index * 0.05}s`;
            
            row.innerHTML = `
                <td>${new Date(expense.date).toLocaleDateString()}</td>
                <td>${expense.category}</td>
                <td>${expense.description || '-'}</td>
                <td>${expense.payment_method}</td>
                <td>$${expense.amount.toFixed(2)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary edit-expense" data-id="${expense.id}">
                        <i class="bi bi-pencil"></i>
                    </button>
                </td>
            `;
            
            tableBody.appendChild(row);
            setTimeout(() => row.style.opacity = '1', 10);
        });
    }, 300);
}

// Update category chart with animation
function updateCategoryChart(data) {
    const ctx = document.getElementById('categoryChart')?.getContext('2d');
    if (!ctx) return;
    
    // Destroy existing chart if it exists
    if (window.categoryChart) {
        window.categoryChart.destroy();
    }
    
    // Create new chart with animation
    window.categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: [
                    '#4361ee', '#4895ef', '#4cc9f0', '#f72585', 
                    '#7209b7', '#3a0ca3', '#f8961e', '#ef233c'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            cutout: '70%',
            animation: {
                animateScale: true,
                animateRotate: true
            },
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 20,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: $${value.toFixed(2)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Initialize UI interactions
function initUIInteractions() {
    // Smooth scroll to top
    document.querySelector('.scroll-to-top')?.addEventListener('click', function(e) {
        e.preventDefault();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // Floating action button
    const fab = document.querySelector('.fab');
    if (fab) {
        fab.addEventListener('click', function() {
            window.location.href = '/add_expense';
        });
        
        // Show/hide FAB on scroll
        let lastScrollTop = 0;
        window.addEventListener('scroll', function() {
            const st = window.pageYOffset || document.documentElement.scrollTop;
            if (st > lastScrollTop) {
                // Scrolling down
                fab.style.transform = 'translateY(100px)';
            } else {
                // Scrolling up
                fab.style.transform = 'translateY(0)';
            }
            lastScrollTop = st <= 0 ? 0 : st;
        }, false);
    }
    
    // Edit expense buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('.edit-expense')) {
            const expenseId = e.target.closest('.edit-expense').dataset.id;
            openEditExpenseModal(expenseId);
        }
    });
}

// Theme toggle functionality
function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        // Check for saved theme preference
        const currentTheme = localStorage.getItem('theme') || 'light';
        document.body.classList.toggle('dark-theme', currentTheme === 'dark');
        themeToggle.checked = currentTheme === 'dark';
        
        themeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('dark-theme');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.remove('dark-theme');
                localStorage.setItem('theme', 'light');
            }
        });
    }
}

// Print functionality
function initPrintButtons() {
    document.querySelectorAll('.print-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            window.print();
        });
    });
}

// Show loading indicator
function showLoading(selector) {
    const element = document.querySelector(selector);
    if (element) {
        const loader = document.createElement('div');
        loader.className = 'loading-spinner';
        loader.id = 'loadingSpinner';
        element.appendChild(loader);
    }
}

// Hide loading indicator
function hideLoading(selector) {
    const loader = document.querySelector(`${selector} #loadingSpinner`);
    if (loader) {
        loader.remove();
    }
}

// Show error toast notification
function showErrorToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast show align-items-center text-white bg-danger border-0';
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '1100';
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.style.transition = 'opacity 0.5s ease';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 5000);
    
    // Manual close
    toast.querySelector('.btn-close').addEventListener('click', () => {
        toast.style.transition = 'opacity 0.5s ease';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    });
}

// Open edit expense modal (placeholder - would be implemented with actual API calls)
function openEditExpenseModal(expenseId) {
    // In a real implementation, we would fetch the expense data here
    console.log('Editing expense with ID:', expenseId);
    
    // Show a toast as placeholder
    showErrorToast('Edit functionality would be implemented here');
}

// Add shake animation to CSS if not already present
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        20%, 60% { transform: translateX(-5px); }
        40%, 80% { transform: translateX(5px); }
    }
    
    .loading-spinner {
        display: inline-block;
        width: 40px;
        height: 40px;
        border: 4px solid rgba(67, 97, 238, 0.2);
        border-radius: 50%;
        border-top-color: #4361ee;
        animation: spin 1s ease-in-out infinite;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    
    @keyframes spin {
        to { transform: translate(-50%, -50%) rotate(360deg); }
    }
    
    .dark-theme {
        background-color: #1a1a2e;
        color: #e6e6e6;
    }
    
    .dark-theme .card {
        background-color: #16213e;
        color: #e6e6e6;
    }
    
    .dark-theme .table {
        color: #e6e6e6;
    }
    
    .dark-theme .table th {
        color: #b8b8b8;
    }
    
    .dark-theme .form-control, 
    .dark-theme .form-select {
        background-color: #1a1a2e;
        color: #e6e6e6;
        border-color: #2d3748;
    }
`;
document.head.appendChild(style);