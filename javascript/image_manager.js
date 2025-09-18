// Simple keyboard navigation for Image Manager
(function() {
    'use strict';

    let keyboardHandler = null;

    function setupKeyboard() {
        // Remove existing handler to prevent duplicates
        if (keyboardHandler) {
            document.removeEventListener('keydown', keyboardHandler);
        }

        keyboardHandler = function(event) {
            // Check if Image Manager tab is active
            const activeTab = document.querySelector('.tab-nav button[aria-selected="true"]') ||
                             document.querySelector('.gradio-tab.selected button') ||
                             document.querySelector('button.selected');

            if (!activeTab || !activeTab.textContent.includes('Image Manager')) {
                return;
            }

            // Don't handle if typing in input fields
            if (event.target.tagName.toLowerCase() === 'input' ||
                event.target.tagName.toLowerCase() === 'textarea' ||
                event.target.isContentEditable) {
                return;
            }

            let targetButton = null;

            if (event.key === 'ArrowLeft') {
                event.preventDefault();
                // Find Previous button more aggressively
                targetButton = Array.from(document.querySelectorAll('button')).find(btn =>
                    btn.textContent.trim().includes('Previous') ||
                    btn.textContent.trim().includes('←') ||
                    btn.textContent.trim() === '← Previous'
                );

            } else if (event.key === 'ArrowRight') {
                event.preventDefault();
                // Find Next button more aggressively
                targetButton = Array.from(document.querySelectorAll('button')).find(btn =>
                    btn.textContent.trim().includes('Next') ||
                    btn.textContent.trim().includes('→') ||
                    btn.textContent.trim() === 'Next →'
                );
            }

            if (targetButton) {
                console.log('Keyboard navigation: clicking button -', targetButton.textContent);
                targetButton.click();
            } else {
                console.log('Keyboard navigation: button not found for key -', event.key);
                console.log('Available buttons:', Array.from(document.querySelectorAll('button')).map(b => b.textContent));
            }
        };

        document.addEventListener('keydown', keyboardHandler);
        console.log('Image Manager keyboard navigation setup complete');
    }

    // Setup with multiple triggers to ensure it works
    function initialize() {
        setupKeyboard();

        // Re-setup when tabs are clicked
        document.addEventListener('click', function(e) {
            if (e.target.closest('.tab-nav') || e.target.textContent?.includes('Image Manager')) {
                setTimeout(setupKeyboard, 100);
            }
        });

        // Re-setup periodically to catch dynamic changes
        setTimeout(setupKeyboard, 1000);
        setTimeout(setupKeyboard, 3000);
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }

    // Also setup when page loads
    window.addEventListener('load', initialize);

})();