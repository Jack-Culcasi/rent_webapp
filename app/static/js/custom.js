// character_counter.js

function updateCharacterCount(textarea) {
    var maxLength = parseInt(textarea.getAttribute('maxlength'));
    var currentLength = textarea.value.length;
    var charactersLeft = maxLength - currentLength;

    // Display the character count in the format "current/maximum"
    document.getElementById('character-count').textContent = currentLength + '/' + maxLength;
}

// Function to show confirmation dialog for Amend
function confirmAmend(context) {
    var confirmationMessage = '';

    // Adjust the message based on the context
    if (context === 'car') {
        confirmationMessage = 'Are you sure you want to amend this car?';
    } else if (context === 'booking') {
        confirmationMessage = 'Are you sure you want to amend this booking?';
    } else {
        // Default message if context is not recognized
        confirmationMessage = 'Are you sure you want to proceed?';
    }

    var isConfirmed = window.confirm(confirmationMessage);

    if (isConfirmed) {
        // Set the action field before submitting the form
        document.getElementById('action').value = 'amend';
        document.getElementById('manageForm').submit();
    }

    return false; // Prevent default behavior
}

// Function to show confirmation dialog for Delete
function confirmDelete(context) {
    var confirmationMessage = '';

    // Adjust the message based on the context
    if (context === 'car') {
        confirmationMessage = 'Are you sure you want to delete this car? All the bookings related to this car will be deleted too.';
    } else if (context === 'booking') {
        confirmationMessage = 'Are you sure you want to delete this booking?';
    } else {
        // Default message if context is not recognized
        confirmationMessage = 'Are you sure you want to proceed?';
    }

    var isConfirmed = window.confirm(confirmationMessage);

    if (isConfirmed) {
        // Set the action field before submitting the form
        document.getElementById('action').value = 'delete';
        document.getElementById('manageForm').submit();
    }

    return false; // Prevent default behavior
}

// Function to toggle dark mode
function toggleDarkMode() {
    var body = document.body;

    // Toggle dark mode class on the body
    body.classList.toggle('dark-mode');

    // Update button text based on dark mode state
    var button = document.getElementById('darkModeToggle');
    if (body.classList.contains('dark-mode')) {
        button.textContent = 'Dark Mode On';
        // Store dark mode preference in localStorage
        localStorage.setItem('darkMode', 'on');
    } else {
        button.textContent = 'Dark Mode Off';
        // Remove dark mode preference from localStorage
        localStorage.removeItem('darkMode');
    }
}

// Check for dark mode preference on page load
document.addEventListener('DOMContentLoaded', function() {
    var darkMode = localStorage.getItem('darkMode');
    var body = document.body;

    // Set dark mode based on the stored preference
    if (darkMode === 'on') {
        body.classList.add('dark-mode');
        // Update button text
        document.getElementById('darkModeToggle').textContent = 'Dark Mode On';
    }
});

// Add an event listener to the button
var darkModeButton = document.getElementById('darkModeToggle');
if (darkModeButton) {
    darkModeButton.addEventListener('click', toggleDarkMode);
}