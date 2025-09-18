// Simple keyboard navigation for Image Manager
(function() {
    'use strict';

    let keyboardSetup = false;

    function setupKeyboard() {
        if (keyboardSetup) return;

        document.addEventListener('keydown', function(event) {
            // Check if Image Manager tab is active
            const activeTab = document.querySelector('.tab-nav button[aria-selected="true"]');
            if (!activeTab || !activeTab.textContent.includes('Image Manager')) {
                return;
            }

            // Don't handle if typing in input
            if (event.target.tagName.toLowerCase() === 'input' ||
                event.target.tagName.toLowerCase() === 'textarea') {
                return;
            }

            if (event.key === 'ArrowLeft') {
                event.preventDefault();
                const prevBtn = document.querySelector('button:contains("Previous")') ||
                               Array.from(document.querySelectorAll('button')).find(btn =>
                                   btn.textContent.includes('Previous') || btn.textContent.includes('←'));
                if (prevBtn) prevBtn.click();

            } else if (event.key === 'ArrowRight') {
                event.preventDefault();
                const nextBtn = document.querySelector('button:contains("Next")') ||
                               Array.from(document.querySelectorAll('button')).find(btn =>
                                   btn.textContent.includes('Next') || btn.textContent.includes('→'));
                if (nextBtn) nextBtn.click();
            }
        });

        keyboardSetup = true;
        console.log('Image Manager keyboard navigation setup');
    }

    // Initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupKeyboard);
    } else {
        setupKeyboard();
    }

    // Also setup when page loads
    window.addEventListener('load', setupKeyboard);

})();