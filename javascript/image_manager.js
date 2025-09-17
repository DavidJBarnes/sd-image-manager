// Image Manager Extension JavaScript
// Place this file in: extensions/image-manager/javascript/image_manager.js

(function() {
    'use strict';

    let imageManagerInitialized = false;

    function initializeImageManager() {
        if (imageManagerInitialized) return;

        // Wait for the Image Manager tab to be available
        const checkTab = setInterval(() => {
            const imageManagerTab = document.querySelector('[data-tab="image_manager"]') ||
                                   document.querySelector('button[id*="image_manager"]') ||
                                   document.querySelector('.tab-nav button:contains("Image Manager")');

            if (imageManagerTab) {
                clearInterval(checkTab);
                setupImageManagerFeatures();
                imageManagerInitialized = true;
            }
        }, 500);
    }

    function setupImageManagerFeatures() {
        console.log("Setting up Image Manager features...");

        // Enhanced keyboard navigation
        setupKeyboardNavigation();

        // Thumbnail hover effects
        setupThumbnailEffects();

        // Image loading optimization
        setupImageOptimization();
    }

    function setupKeyboardNavigation() {
        // Remove any existing keyboard listeners to avoid duplicates
        document.removeEventListener('keydown', handleKeyboardNavigation);
        document.addEventListener('keydown', handleKeyboardNavigation);

        console.log("Keyboard navigation setup complete");
    }

    function handleKeyboardNavigation(event) {
        // Only handle keyboard events when Image Manager tab is active
        const activeTab = document.querySelector('.tab-nav button[aria-selected="true"]') ||
                         document.querySelector('.tab-nav .selected') ||
                         document.querySelector('#tab_image_manager[style*="block"]');

        if (!activeTab || (!activeTab.textContent.includes('Image Manager') && !activeTab.id.includes('image_manager'))) {
            return;
        }

        // Don't handle keyboard events when user is typing in inputs
        if (event.target.tagName.toLowerCase() === 'input' ||
            event.target.tagName.toLowerCase() === 'textarea' ||
            event.target.contentEditable === 'true') {
            return;
        }

        switch (event.key) {
            case 'ArrowLeft':
                event.preventDefault();
                // Find the Previous button more reliably
                const prevBtns = document.querySelectorAll('button');
                const prevBtn = Array.from(prevBtns).find(btn =>
                    btn.textContent.includes('Previous') ||
                    btn.textContent.includes('←')
                );
                if (prevBtn) prevBtn.click();
                break;

            case 'ArrowRight':
                event.preventDefault();
                // Find the Next button more reliably
                const nextBtns = document.querySelectorAll('button');
                const nextBtn = Array.from(nextBtns).find(btn =>
                    btn.textContent.includes('Next') ||
                    btn.textContent.includes('→')
                );
                if (nextBtn) nextBtn.click();
                break;

            case 'Home':
                event.preventDefault();
                // Jump to first image
                const firstThumbnail = document.querySelector('#thumbnail_gallery img:first-child');
                if (firstThumbnail) firstThumbnail.click();
                break;

            case 'End':
                event.preventDefault();
                // Jump to last image
                const lastThumbnail = document.querySelector('#thumbnail_gallery img:last-child');
                if (lastThumbnail) lastThumbnail.click();
                break;
        }
    }

    function setupThumbnailEffects() {
        // Add CSS for better thumbnail interactions and horizontal scrolling
        const style = document.createElement('style');
        style.textContent = `
            #image_manager .gallery {
                overflow-x: auto !important;
                overflow-y: hidden !important;
                white-space: nowrap;
                padding-bottom: 10px;
            }
            
            #image_manager .gallery > div {
                display: inline-flex !important;
                flex-direction: row !important;
                gap: 8px;
                align-items: flex-start;
            }
            
            #image_manager .gallery img {
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                cursor: pointer;
                border-radius: 4px;
                flex-shrink: 0;
                width: 100px !important;
                height: 100px !important;
                object-fit: cover;
            }
            
            #image_manager .gallery img:hover {
                transform: scale(1.05);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                z-index: 10;
                position: relative;
            }
            
            #image_manager .gallery img.selected {
                border: 3px solid #2563eb;
                box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.3);
            }
            
            #image_manager .main-image {
                max-height: 600px;
                object-fit: contain;
                background: #f8f9fa;
                border-radius: 8px;
            }
            
            #image_manager .navigation-buttons {
                margin: 10px 0;
            }
            
            #image_manager .keyboard-hint {
                font-size: 0.875rem;
                color: #6b7280;
                text-align: center;
                margin-top: 10px;
            }
            
            /* Ensure horizontal scrolling works */
            #thumbnail_gallery {
                overflow-x: auto !important;
                overflow-y: hidden !important;
            }
            
            #thumbnail_gallery .grid {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                gap: 8px;
                padding: 10px;
            }
            
            #thumbnail_gallery .grid > div {
                flex-shrink: 0;
            }
        `;

        if (!document.querySelector('#image-manager-styles')) {
            style.id = 'image-manager-styles';
            document.head.appendChild(style);
        }
    }

    function setupImageOptimization() {
        // Preload adjacent images for smoother navigation
        function preloadAdjacentImages() {
            const currentImage = document.querySelector('#image_manager .main-image img');
            if (!currentImage) return;

            const thumbnails = document.querySelectorAll('#image_manager .gallery img');
            const currentSrc = currentImage.src;
            let currentIndex = -1;

            // Find current image index
            thumbnails.forEach((thumb, index) => {
                if (thumb.src === currentSrc) {
                    currentIndex = index;
                }
            });

            if (currentIndex === -1) return;

            // Preload previous and next images
            const preloadImages = [];
            if (currentIndex > 0) preloadImages.push(thumbnails[currentIndex - 1].src);
            if (currentIndex < thumbnails.length - 1) preloadImages.push(thumbnails[currentIndex + 1].src);

            preloadImages.forEach(src => {
                const img = new Image();
                img.src = src;
            });
        }

        // Set up mutation observer to detect image changes
        const observer = new MutationObserver(() => {
            setTimeout(preloadAdjacentImages, 100);
        });

        const imageManager = document.querySelector('#image_manager');
        if (imageManager) {
            observer.observe(imageManager, { childList: true, subtree: true });
        }
    }

    function addKeyboardHints() {
        const imageManager = document.querySelector('#image_manager');
        if (!imageManager || imageManager.querySelector('.keyboard-hint')) return;

        const hint = document.createElement('div');
        hint.className = 'keyboard-hint';
        hint.textContent = 'Use ← → arrow keys to navigate, Home/End to jump to first/last image';

        const navigationArea = imageManager.querySelector('.navigation-buttons') ||
                              imageManager.querySelector('.gradio-button-group');
        if (navigationArea) {
            navigationArea.parentNode.insertBefore(hint, navigationArea.nextSibling);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeImageManager);
    } else {
        initializeImageManager();
    }

    // Also initialize when the page changes (for single-page app behavior)
    window.addEventListener('load', initializeImageManager);

    // Re-initialize if the interface is dynamically loaded
    const observer = new MutationObserver(() => {
        if (!imageManagerInitialized && document.querySelector('[data-tab="image_manager"]')) {
            initializeImageManager();
        }
    });

    observer.observe(document.body, { childList: true, subtree: true });

})();