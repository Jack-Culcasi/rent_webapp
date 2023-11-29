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