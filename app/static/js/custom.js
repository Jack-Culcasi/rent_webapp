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

$(document).ready(function() {
    var searchNameInput = $('#search_name');
    var searchResultsContainer = $('#searchResults');  // Corrected ID

    searchNameInput.on('input', function() {
        var searchQuery = searchNameInput.val().trim();

        // Clear previous results
        searchResultsContainer.html('');

        if (searchQuery.length > 0) {
            // Make an asynchronous request to the server
            $.ajax({
                type: 'POST',
                url: '/search_contacts',
                data: { search_name: searchQuery },
                success: function(response) {
                    // Populate the dropdown with results
                    searchResultsContainer.html(response);

                    // Show the dropdown
                    searchResultsContainer.show();
                }
            });
        } else {
            // Hide the dropdown if the input is empty
            searchResultsContainer.hide();
        }
    });

    // Hide the dropdown when clicking outside the input and results container
    $(document).on('click', function(event) {
        if (!$(event.target).is(searchNameInput) && !$(event.target).is('.result-item')) {
            searchResultsContainer.hide();
        }
    });

    // Handle click event on a result item
    searchResultsContainer.on('click', '.result-item', function() {
        searchNameInput.val($(this).text());
        searchResultsContainer.hide(); // Clear and hide the dropdown
    });
});