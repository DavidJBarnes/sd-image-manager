// Image Manager Extension JavaScript
// This file handles all client-side functionality

(function() {
    'use strict';

    let imageManagerInitialized = false;
    let keyboardHandler = null;

    // Global variables for state management
    window.currentImageIndex = 0;
    window.currentImages = [];

    function initializeImageManager() {
        if (imageManagerInitialized) return;

        console.log("Initializing Image Manager...");

        // Setup all functionality
        setupThumbnailHandling();
        setupKeyboardNavigation();
        setupStyles();

        imageManagerInitialized = true;
    }

    function setupThumbnailHandling() {
        // Global function for thumbnail selection (called from inline HTML)
        window.selectThumbnail = function(index, filepath) {
            window.currentImageIndex = index;

            // Update thumbnail selection visually
            document.querySelectorAll('.thumbnail-img').forEach((img, i) => {
                if (i === index) {
                    img.classList.add('selected');
                    img.style.border = '3px solid #2563eb';
                    img.style.boxShadow = '0 0 0 2px rgba(37, 99, 235, 0.3)';
                } else {
                    img.classList.remove('selected');
                    img.style.border = 'none';
                    img.style.boxShadow = 'none';
                }
            });

            // Trigger the Python handler through hidden textbox
            const eventBox = document.querySelector('#js_event_box textarea') ||
                            document.querySelector('#js_event_box input');
            if (eventBox) {
                eventBox.value = index.toString();
                eventBox.dispatchEvent(new Event('input', { bubbles: true }));
            }
        };

        // Navigation function called by keyboard and buttons
        window.navigateImage = function(direction) {
            if (!window.currentImages || window.currentImages.length === 0) return;

            let newIndex = window.currentImageIndex;
            if (direction === 'prev' && newIndex > 0) {
                newIndex--;
            } else if (direction === 'next' && newIndex < window.currentImages.length - 1) {
                newIndex++;
            }

            if (newIndex !== window.currentImageIndex) {
                selectThumbnail(newIndex, window.currentImages[newIndex].filepath);
            }
        };
    }

    function setupKeyboardNavigation() {
        // Remove existing handler
        if (keyboardHandler) {
            document.removeEventListener('keydown', keyboardHandler);
        }

        keyboardHandler = function(event) {
            // Check if Image Manager tab is active
            const activeTab = document.querySelector('.tab-nav button[aria-selected="true"]') ||
                             document.querySelector('.tab-nav .selected');

            if (!activeTab || !activeTab.textContent.includes('Image Manager')) {
                return;
            }

            // Don't handle if user is typing
            if (event.target.tagName.toLowerCase() === 'input' ||
                event.target.tagName.toLowerCase() === 'textarea' ||
                event.target.contentEditable === 'true') {
                return;
            }

            switch (event.key) {
                case 'ArrowLeft':
                    event.preventDefault();
                    // Find and click Previous button
                    const prevBtn = Array.from(document.querySelectorAll('button')).find(btn =>
                        btn.textContent.includes('Previous') || btn.textContent.includes('←')
                    );
                    if (prevBtn) {
                        console.log('Clicking Previous button via keyboard');
                        prevBtn.click();
                    }
                    break;

                case 'ArrowRight':
                    event.preventDefault();
                    // Find and click Next button
                    const nextBtn = Array.from(document.querySelectorAll('button')).find(btn =>
                        btn.textContent.includes('Next') || btn.textContent.includes('→')
                    );
                    if (nextBtn) {
                        console.log('Clicking Next button via keyboard');
                        nextBtn.click();
                    }
                    break;

                case 'Home':
                    event.preventDefault();
                    if (window.currentImages && window.currentImages.length > 0) {
                        selectThumbnail(0, window.currentImages[0].filepath);
                    }
                    break;

                case 'End':
                    event.preventDefault();
                    if (window.currentImages && window.currentImages.length > 0) {
                        const lastIndex = window.currentImages.length - 1;
                        selectThumbnail(lastIndex, window.currentImages[lastIndex].filepath);
                    }
                    break;
            }
        };

        document.addEventListener('keydown', keyboardHandler);
        console.log('Keyboard navigation setup complete');
    }

    function setupStyles() {
        // Add CSS for thumbnail gallery and interactions
        const style = document.createElement('style');
        style.id = 'image-manager-styles';
        style.textContent = `
            /* Custom thumbnail gallery styles */
            #custom-thumbnail-gallery {
                scrollbar-width: thin;
                scrollbar-color: #888 #f1f1f1;
            }
            
            #custom-thumbnail-gallery::-webkit-scrollbar {
                height: 8px;
            }
            
            #custom-thumbnail-gallery::-webkit-scrollbar-track {
                background: #f1f1f1;
                border-radius: 4px;
            }
            
            #custom-thumbnail-gallery::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 4px;
            }
            
            #custom-thumbnail-gallery::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
            
            /* Ensure thumbnails maintain proper sizing */
            .thumbnail-img {
                min-width: 200px !important;
                max-width: 200px !important;
                min-height: 200px !important;
                max-height: 200px !important;
            }
            
            /* Main image container */
            #image_manager .main-image {
                background: #f8f9fa;
                border-radius: 8px;
            }
            
            /* Button styling */
            #image_manager button {
                transition: all 0.2s ease;
            }
            
            #image_manager button:hover {
                transform: translateY(-1px);
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            
            /* Hidden textbox */
            #js_event_box {
                display: none !important;
            }
        `;

        if (!document.querySelector('#image-manager-styles')) {
            document.head.appendChild(style);
        }
    }

    function observeForChanges() {
        // Watch for thumbnail gallery updates
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === 1 && node.id === 'custom-thumbnail-gallery') {
                            console.log('Thumbnail gallery updated');
                            // Update current images from the DOM
                            updateCurrentImagesFromDOM();
                        }
                    });
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    function updateCurrentImagesFromDOM() {
        // Extract current images from thumbnail gallery
        const thumbnails = document.querySelectorAll('.thumbnail-img');
        window.currentImages = Array.from(thumbnails).map((img, index) => ({
            filename: img.title || `Image ${index + 1}`,
            filepath: img.dataset.filepath || img.src
        }));

        // Update current index from selected thumbnail
        const selectedThumbnail = document.querySelector('.thumbnail-img.selected');
        if (selectedThumbnail) {
            window.currentImageIndex = parseInt(selectedThumbnail.dataset.index) || 0;
        }
    }

    // Initialize when DOM is ready
    function waitForDOM() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initializeImageManager);
        } else {
            initializeImageManager();
        }
    }

    // Initialize
    waitForDOM();

    // Re-initialize when needed
    window.addEventListener('load', initializeImageManager);

    // Watch for tab changes
    document.addEventListener('click', function(e) {
        if (e.target.closest('.tab-nav') || e.target.textContent.includes('Image Manager')) {
            setTimeout(initializeImageManager, 100);
        }
    });

    // Setup observers
    observeForChanges();

    console.log('Image Manager JavaScript loaded');

})();