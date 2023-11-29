// character_counter.js

function updateCharacterCount(textarea) {
    var maxLength = parseInt(textarea.getAttribute('maxlength'));
    var currentLength = textarea.value.length;
    var charactersLeft = maxLength - currentLength;

    // Display the character count in the format "current/maximum"
    document.getElementById('character-count').textContent = currentLength + '/' + maxLength;
}

// Function to show confirmation dialog for Amend
function confirmAmend() {
    var isConfirmed = window.confirm('Are you sure you want to amend this booking?');
    if (isConfirmed) {
        // Set the action field before submitting the form
        document.getElementById('action').value = 'amend';
        document.getElementById('manageForm').submit();
    }
    return false; // Prevent default behavior
}

// Function to show confirmation dialog for Delete
function confirmDelete() {
    var isConfirmed = window.confirm('Are you sure you want to delete this car? All the bookings related to this car will be deleted too.');
    if (isConfirmed) {
        // Set the action field before submitting the form
        document.getElementById('action').value = 'delete';
        document.getElementById('manageForm').submit();
    }
    return false; // Prevent default behavior
}