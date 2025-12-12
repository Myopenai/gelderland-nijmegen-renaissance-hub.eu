// Forum JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize forum functionality
    initForum();
});

function initForum() {
    // New Topic Modal
    const newTopicBtn = document.getElementById('new-topic-btn');
    const newTopicModal = document.getElementById('new-topic-modal');
    const closeModal = document.querySelector('.close-modal');
    const cancelBtn = document.querySelector('.cancel-btn');
    const newTopicForm = document.getElementById('new-topic-form');
    
    // Show modal when New Topic button is clicked
    if (newTopicBtn && newTopicModal) {
        newTopicBtn.addEventListener('click', function() {
            newTopicModal.style.display = 'flex';
            document.body.style.overflow = 'hidden'; // Prevent scrolling when modal is open
        });
    }
    
    // Close modal when X is clicked
    if (closeModal && newTopicModal) {
        closeModal.addEventListener('click', function() {
            newTopicModal.style.display = 'none';
            document.body.style.overflow = 'auto';
        });
    }
    
    // Close modal when Cancel button is clicked
    if (cancelBtn && newTopicModal) {
        cancelBtn.addEventListener('click', function(e) {
            e.preventDefault();
            newTopicModal.style.display = 'none';
            document.body.style.overflow = 'auto';
        });
    }
    
    // Close modal when clicking outside the modal content
    if (newTopicModal) {
        newTopicModal.addEventListener('click', function(e) {
            if (e.target === newTopicModal) {
                newTopicModal.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        });
    }
    
    // Handle form submission
    if (newTopicForm) {
        newTopicForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form values
            const title = document.getElementById('topic-title').value.trim();
            const category = document.getElementById('topic-category').value;
            const content = document.getElementById('topic-content').innerHTML;
            
            // Basic validation
            if (!title || !category || !content) {
                showNotification('Please fill in all required fields', 'error');
                return;
            }
            
            // Here you would typically send the data to a server
            // For now, we'll just show a success message
            showNotification('Topic created successfully!', 'success');
            
            // Reset form
            newTopicForm.reset();
            document.getElementById('topic-content').innerHTML = '';
            
            // Close modal
            newTopicModal.style.display = 'none';
            document.body.style.overflow = 'auto';
            
            // In a real app, you would update the UI with the new topic
            // and possibly redirect to the new topic page
        });
    }
    
    // Initialize rich text editor functionality
    initRichTextEditor();
}

// Initialize rich text editor functionality
function initRichTextEditor() {
    const editor = document.getElementById('topic-content');
    const toolbarButtons = document.querySelectorAll('.toolbar-btn');
    
    if (!editor) return;
    
    // Add event listeners to toolbar buttons
    toolbarButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const command = this.getAttribute('data-command');
            
            // Handle different commands
            if (command === 'createLink' || command === 'insertImage') {
                const url = prompt('Enter the ' + (command === 'createLink' ? 'URL' : 'image URL') + ':');
                if (url) {
                    document.execCommand(command, false, url);
                }
            } else {
                document.execCommand(command, false, null);
            }
            
            // Focus back on the editor
            editor.focus();
        });
    });
}

// Show notification function
function showNotification(message, type = 'info') {
    // Create notification element if it doesn't exist
    let notification = document.querySelector('.notification');
    
    if (!notification) {
        notification = document.createElement('div');
        notification.className = 'notification';
        document.body.appendChild(notification);
    }
    
    // Set notification content and style based on type
    notification.textContent = message;
    notification.className = `notification ${type}`;
    
    // Show notification
    notification.style.display = 'block';
    notification.style.opacity = '1';
    
    // Hide notification after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.style.display = 'none';
        }, 300);
    }, 3000);
}

// Add some basic styling for notifications
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 24px;
        border-radius: 4px;
        color: white;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        opacity: 0;
        transition: opacity 0.3s ease-in-out;
        display: none;
    }
    
    .notification.success {
        background-color: #28a745;
    }
    
    .notification.error {
        background-color: #dc3545;
    }
    
    .notification.info {
        background-color: #17a2b8;
    }
    
    .notification.warning {
        background-color: #ffc107;
        color: #212529;
    }
`;

document.head.appendChild(notificationStyles);

// Handle back to top button
const backToTopBtn = document.getElementById('back-to-top');
if (backToTopBtn) {
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopBtn.style.display = 'block';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });
    
    backToTopBtn.addEventListener('click', function(e) {
        e.preventDefault();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Mobile menu toggle
const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
const mainNav = document.querySelector('.main-nav');

if (mobileMenuToggle && mainNav) {
    mobileMenuToggle.addEventListener('click', function() {
        this.classList.toggle('active');
        mainNav.classList.toggle('active');
    });
}

// Add active class to current navigation item
const currentLocation = location.href;
const menuItems = document.querySelectorAll('.main-nav a');
const menuLength = menuItems.length;

for (let i = 0; i < menuLength; i++) {
    if (menuItems[i].href === currentLocation) {
        menuItems[i].classList.add('active');
    }
}
