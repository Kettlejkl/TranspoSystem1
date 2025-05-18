// wallet.js

// Get the current balance
let currentBalance = 0;

// Function to format currency
function formatCurrency(amount) {
    return parseFloat(amount).toFixed(2);
}

// Initialize wallet functionality
document.addEventListener('DOMContentLoaded', function() {
    // Get the initial balance from the Django backend
    const balanceElement = document.getElementById('balance');
    if (balanceElement) {
        // Get the initial balance from the data attribute set by Django
        currentBalance = parseFloat(balanceElement.getAttribute('data-initial-balance') || 0);
        balanceElement.textContent = formatCurrency(currentBalance);
    }
    
    // Listen for form submissions
    const walletForm = document.getElementById('wallet-form');
    if (walletForm) {
        walletForm.addEventListener('submit', function(e) {
            e.preventDefault();
        });
    }
});

// Function to deposit money
function deposit() {
    const amountElement = document.getElementById('amount');
    const senderNumberElement = document.getElementById('senderNumber');
    const amount = parseFloat(amountElement.value);
    const senderNumber = senderNumberElement.value.trim();
    
    if (isNaN(amount) || amount <= 0) {
        alert('Please enter a valid amount');
        return;
    }
    
    if (!senderNumber) {
        alert('Please enter a sender number');
        return;
    }
    
    // API call to update balance
    updateBalance('deposit', amount, senderNumber);
}

// Function to withdraw money
function withdraw() {
    const amountElement = document.getElementById('amount');
    const senderNumberElement = document.getElementById('senderNumber');
    const amount = parseFloat(amountElement.value);
    const senderNumber = senderNumberElement.value.trim();
    
    if (isNaN(amount) || amount <= 0) {
        alert('Please enter a valid amount');
        return;
    }
    
    if (!senderNumber) {
        alert('Please enter a sender number');
        return;
    }
    
    if (amount > currentBalance) {
        alert('Insufficient funds');
        return;
    }
    
    // API call to update balance
    updateBalance('withdraw', amount, senderNumber);
}

// Function to update balance via API
function updateBalance(action, amount, senderNumber) {
    // Show loading indicator
    document.body.classList.add('loading');
    
    // Send request to the server
    fetch('/api/wallet/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            action: action,
            amount: amount,
            sender_number: senderNumber
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Hide loading indicator
        document.body.classList.remove('loading');
        
        if (data.success) {
            // Update the displayed balance
            currentBalance = data.balance;
            document.getElementById('balance').textContent = formatCurrency(currentBalance);
            document.getElementById('amount').value = ''; // Clear the amount field
            
            // Show success message
            alert(`Successfully ${action}ed $${formatCurrency(amount)}`);
            
            // Update the data attribute with the new balance
            document.getElementById('balance').setAttribute('data-initial-balance', currentBalance);
        } else {
            // Show error message
            alert(data.message || 'An error occurred');
        }
    })
    .catch(error => {
        // Hide loading indicator
        document.body.classList.remove('loading');
        
        console.error('Error:', error);
        alert('An error occurred. Please try again later.');
    });
}

// Function to show alerts for submit and send buttons
function showAlert(action) {
    // Get form data
    const senderNumber = document.getElementById('senderNumber').value;
    
    // Simple validation
    if (!senderNumber) {
        alert('Please enter a sender number');
        return;
    }
    
    // For submission, we'll use a real API call
    if (action === 'Submit') {
        // Send data to server for processing
        fetch('/api/wallet/submit/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                sender_number: senderNumber
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Information submitted successfully!');
            } else {
                alert(data.message || 'An error occurred during submission');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during submission. Please try again later.');
        });
    } else {
        // Just show an alert for demonstration purposes
        alert(`${action} action initiated for sender number: ${senderNumber}`);
    }
}

// Function to go back
function goBack() {
    window.history.back();
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}