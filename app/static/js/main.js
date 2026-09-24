// Main JavaScript for LoanMaster

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.transition = 'opacity 0.5s ease';
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 500);
        }, 5000);
    });

    // Phone number formatting for M-PESA
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            // Remove any non-numeric characters
            this.value = this.value.replace(/\D/g, '');
            
            // Limit to 12 digits
            if (this.value.length > 12) {
                this.value = this.value.slice(0, 12);
            }
        });
    });

    // Loan amount validation
    const amountInputs = document.querySelectorAll('input[name="amount"]');
    amountInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            const value = parseFloat(this.value);
            if (value < 0) {
                this.value = 0;
            }
            if (value > 1000000) {
                this.value = 1000000;
                showAlert('Maximum loan amount is KSh 1,000,000', 'warning');
            }
        });
    });

    // Confirm dangerous actions
    const confirmButtons = document.querySelectorAll('.confirm-action');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to perform this action?')) {
                e.preventDefault();
            }
        });
    });

    // Update loan status badges dynamically
    const statusBadges = document.querySelectorAll('.badge');
    statusBadges.forEach(badge => {
        const status = badge.textContent.trim();
        if (status === 'ACTIVE') {
            badge.classList.add('bg-success');
        } else if (status === 'PENDING') {
            badge.classList.add('bg-warning');
        } else if (status === 'APPROVED') {
            badge.classList.add('bg-info');
        } else if (status === 'REJECTED') {
            badge.classList.add('bg-danger');
        } else if (status === 'COMPLETED') {
            badge.classList.add('bg-secondary');
        }
    });

    // Calculate loan interest
    const loanAmountInput = document.querySelector('input[name="loan_amount"]');
    const loanPeriodInput = document.querySelector('input[name="loan_period"]');
    const interestDisplay = document.getElementById('interestDisplay');
    const totalDisplay = document.getElementById('totalDisplay');
    const monthlyDisplay = document.getElementById('monthlyDisplay');

    if (loanAmountInput && loanPeriodInput) {
        const updateLoanCalculations = function() {
            const amount = parseFloat(loanAmountInput.value) || 0;
            const period = parseInt(loanPeriodInput.value) || 1;
            const interestRate = 10; // 10% annual interest
            const total = amount * (1 + (interestRate / 100) * (period / 12));
            const monthly = total / period;
            
            if (interestDisplay) {
                interestDisplay.textContent = `KSh ${(total - amount).toFixed(2)}`;
            }
            if (totalDisplay) {
                totalDisplay.textContent = `KSh ${total.toFixed(2)}`;
            }
            if (monthlyDisplay) {
                monthlyDisplay.textContent = `KSh ${monthly.toFixed(2)}`;
            }
        };

        loanAmountInput.addEventListener('input', updateLoanCalculations);
        loanPeriodInput.addEventListener('input', updateLoanCalculations);
        
        // Initial calculation
        updateLoanCalculations();
    }
});

// Utility function to show alerts
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Function to handle M-PESA STK Push
function initiateSTKPush(phoneNumber, amount, callback) {
    // In production, this would call the Daraja API
    // For demo, we'll simulate the process
    console.log(`Initiating STK Push to ${phoneNumber} for KSh ${amount}`);
    
    // Show loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'alert alert-info mt-3';
    loadingDiv.innerHTML = `
        <i class="fas fa-spinner fa-spin me-2"></i>
        Sending M-PESA request to ${phoneNumber}...
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.appendChild(loadingDiv);
    }
    
    // Simulate API call
    setTimeout(() => {
        loadingDiv.remove();
        
        // Simulate success
        if (Math.random() > 0.1) { // 90% success rate for demo
            showAlert(`Payment request sent to ${phoneNumber}. Please check your phone and enter PIN.`, 'success');
            if (callback) callback(true);
        } else {
            showAlert('Payment failed. Please try again.', 'danger');
            if (callback) callback(false);
        }
    }, 2000);
}

// Function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-KE', {
        style: 'currency',
        currency: 'KES'
    }).format(amount);
}