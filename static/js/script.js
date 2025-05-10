// Dev Forum JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Dark mode toggle
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            const isDarkMode = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDarkMode);
            
            // Update icon
            const icon = darkModeToggle.querySelector('i');
            if (isDarkMode) {
                icon.classList.remove('bi-moon');
                icon.classList.add('bi-sun');
            } else {
                icon.classList.remove('bi-sun');
                icon.classList.add('bi-moon');
            }
        });

        // Check for saved dark mode preference
        const savedDarkMode = localStorage.getItem('darkMode');
        if (savedDarkMode === 'true') {
            document.body.classList.add('dark-mode');
            const icon = darkModeToggle.querySelector('i');
            icon.classList.remove('bi-moon');
            icon.classList.add('bi-sun');
        }
    }

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea.auto-resize');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        // Initial resize
        textarea.dispatchEvent(new Event('input'));
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.confirm-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Fade in elements with .fade-in class
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach(element => {
        element.classList.add('show');
    });

    // Add active class to current nav item
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });

    // Markdown preview for post content
    const markdownPreviews = document.querySelectorAll('.markdown-preview');
    markdownPreviews.forEach(preview => {
        const textarea = document.getElementById(preview.dataset.for);
        const previewButton = document.getElementById(preview.dataset.button);
        
        if (textarea && previewButton) {
            previewButton.addEventListener('click', function() {
                // Simple markdown to HTML conversion
                let html = textarea.value
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\*(.*?)\*/g, '<em>$1</em>')
                    .replace(/\n/g, '<br>');
                
                preview.innerHTML = html;
                preview.style.display = 'block';
                textarea.style.display = 'none';
                
                this.textContent = 'Edit';
                this.dataset.mode = 'preview';
                
                if (this.dataset.mode === 'preview') {
                    preview.style.display = 'none';
                    textarea.style.display = 'block';
                    this.textContent = 'Preview';
                    this.dataset.mode = 'edit';
                } else {
                    preview.style.display = 'block';
                    textarea.style.display = 'none';
                    this.textContent = 'Edit';
                    this.dataset.mode = 'preview';
                }
            });
        }
    });
});

// Add dark mode toggle to navbar
function addDarkModeToggle() {
    const navbarNav = document.querySelector('.navbar-nav');
    if (navbarNav) {
        const darkModeItem = document.createElement('li');
        darkModeItem.className = 'nav-item';
        darkModeItem.innerHTML = `
            <button id="dark-mode-toggle" class="btn nav-link">
                <i class="bi bi-moon"></i>
            </button>
        `;
        navbarNav.appendChild(darkModeItem);
    }
}

// Call the function after DOM is loaded
document.addEventListener('DOMContentLoaded', addDarkModeToggle);