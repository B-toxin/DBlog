// script.js
const navToggle = document.getElementById('navToggle');
const sidebar = document.getElementById('sidebar');

navToggle.addEventListener('click', () => {
    // Toggle sidebar visibility by changing the left property
    const isVisible = sidebar.style.left === '0px' || sidebar.style.left === '';
    sidebar.style.left = isVisible ? '-250px' : '0px';
});
