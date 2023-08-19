document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const body = document.body;

    // Check if dark mode preference is stored in local storage
    const darkModeEnabled = localStorage.getItem('darkModeEnabled') === 'true';

    // Apply dark mode based on stored preference
    if (darkModeEnabled) {
        body.classList.add('dark-mode');
        darkModeToggle.checked = true;
    }

    darkModeToggle.addEventListener('change', function() {
        if (darkModeToggle.checked) {
            body.classList.add('dark-mode');
            localStorage.setItem('darkModeEnabled', 'true');
        } else {
            body.classList.remove('dark-mode');
            localStorage.setItem('darkModeEnabled', 'false');
        }
    });
});
