import os
import gradio as gr
from modules import script_callbacks, shared, images
from pathlib import Path
import json
from datetime import datetime


class ImageManagerExtension:
    def __init__(self):
        self.base_path = os.path.expanduser("~/StabilityMatrix-linux-x64/Data/Images/Text2Img")
        self.current_folder = None
        self.current_images = []
        self.current_index = 0

    def get_folders(self):
        """Get all folders in the base directory, sorted by modification time (newest first)"""
        if not os.path.exists(self.base_path):
            return []

        folders = []
        for item in os.listdir(self.base_path):
            item_path = os.path.join(self.base_path, item)
            if os.path.isdir(item_path):
                folders.append((item, os.path.getmtime(item_path)))

        # Sort by modification time, newest first
        folders.sort(key=lambda x: x[1], reverse=True)
        return [folder[0] for folder in folders]

    def get_images_in_folder(self, folder_name):
        """Get all image files in the specified folder"""
        if not folder_name:
            return []

        folder_path = os.path.join(self.base_path, folder_name)
        if not os.path.exists(folder_path):
            return []

        image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff'}
        images = []

        for file in os.listdir(folder_path):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                full_path = os.path.join(folder_path, file)
                images.append((file, os.path.getmtime(full_path), full_path))

        # Sort by modification time, newest first
        images.sort(key=lambda x: x[1], reverse=True)
        return [(img[0], img[2]) for img in images]  # Return (filename, full_path)

    def load_image(self, image_path):
        """Load image for display"""
        if os.path.exists(image_path):
            return image_path
        return None

    def navigate_image(self, direction, current_folder, current_index):
        """Navigate through images using keyboard or button input"""
        if not current_folder:
            return None, current_index, []

        images = self.get_images_in_folder(current_folder)
        if not images:
            return None, 0, []

        if direction == "left" and current_index > 0:
            current_index -= 1
        elif direction == "right" and current_index < len(images) - 1:
            current_index += 1

        current_image = self.load_image(images[current_index][1])
        return current_image, current_index, images


def create_image_manager_interface():
    manager = ImageManagerExtension()

    with gr.Blocks() as image_manager_interface:
        gr.HTML("<h2>Image Manager</h2>")

        # State variables
        current_folder_state = gr.State(value=None)
        current_index_state = gr.State(value=0)
        current_images_state = gr.State(value=[])

        with gr.Row():
            with gr.Column():
                # Folder dropdown
                folder_dropdown = gr.Dropdown(
                    label="Select Folder",
                    choices=manager.get_folders(),
                    value=manager.get_folders()[0] if manager.get_folders() else None,
                    interactive=True
                )

        with gr.Row():
            # Main image display area
            with gr.Column(scale=3):
                main_image = gr.Image(
                    label="Selected Image",
                    type="filepath",
                    height=600,
                    interactive=False
                )

                # Navigation buttons
                with gr.Row():
                    prev_btn = gr.Button("← Previous", variant="secondary")
                    next_btn = gr.Button("Next →", variant="secondary")

        with gr.Row():
            # Thumbnail gallery
            thumbnail_gallery = gr.Gallery(
                label="Thumbnails",
                show_label=True,
                elem_id="thumbnail_gallery",
                columns=8,
                rows=2,
                height="200px",
                object_fit="cover",
                allow_preview=False
            )

        # JavaScript for keyboard navigation
        keyboard_js = """
        function setupKeyboardNavigation() {
            document.addEventListener('keydown', function(event) {
                if (event.target.tagName.toLowerCase() === 'input' || 
                    event.target.tagName.toLowerCase() === 'textarea') {
                    return;
                }

                if (event.key === 'ArrowLeft') {
                    event.preventDefault();
                    document.querySelector('#prev_btn button').click();
                } else if (event.key === 'ArrowRight') {
                    event.preventDefault();
                    document.querySelector('#next_btn button').click();
                }
            });
        }

        // Setup keyboard navigation when the page loads
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', setupKeyboardNavigation);
        } else {
            setupKeyboardNavigation();
        }
        """

        # Add keyboard navigation JavaScript
        gr.HTML(f"<script>{keyboard_js}</script>")

        def update_folder_content(folder_name):
            """Update content when folder selection changes"""
            if not folder_name:
                return None, [], 0, folder_name, []

            images = manager.get_images_in_folder(folder_name)
            if not images:
                return None, [], 0, folder_name, images

            # Load first image
            first_image = manager.load_image(images[0][1])

            # Prepare thumbnail data for gallery
            thumbnail_data = [(img[1], img[0]) for img in images]  # (path, caption)

            return first_image, thumbnail_data, 0, folder_name, images

        def on_thumbnail_select(evt: gr.SelectData):
            """Handle thumbnail selection"""
            if not evt.index and evt.index != 0:
                return None, 0

            folder_name = folder_dropdown.value
            if not folder_name:
                return None, 0

            images = manager.get_images_in_folder(folder_name)
            if evt.index < len(images):
                selected_image = manager.load_image(images[evt.index][1])
                return selected_image, evt.index

            return None, 0

        def navigate_images(direction):
            """Handle image navigation"""
            folder_name = folder_dropdown.value
            current_index = current_index_state.value if current_index_state.value is not None else 0

            if not folder_name:
                return None, current_index

            images = manager.get_images_in_folder(folder_name)
            if not images:
                return None, 0

            if direction == "prev" and current_index > 0:
                current_index -= 1
            elif direction == "next" and current_index < len(images) - 1:
                current_index += 1

            selected_image = manager.load_image(images[current_index][1])
            return selected_image, current_index

        # Event handlers
        folder_dropdown.change(
            fn=update_folder_content,
            inputs=[folder_dropdown],
            outputs=[main_image, thumbnail_gallery, current_index_state, current_folder_state, current_images_state]
        )

        thumbnail_gallery.select(
            fn=on_thumbnail_select,
            outputs=[main_image, current_index_state]
        )

        prev_btn.click(
            fn=lambda: navigate_images("prev"),
            outputs=[main_image, current_index_state]
        )

        next_btn.click(
            fn=lambda: navigate_images("next"),
            outputs=[main_image, current_index_state]
        )

        # Initialize with first folder if available
        def initialize_interface():
            folders = manager.get_folders()
            if folders:
                return update_folder_content(folders[0])
            return None, [], 0, None, []

        # Load initial content
        image_manager_interface.load(
            fn=initialize_interface,
            outputs=[main_image, thumbnail_gallery, current_index_state, current_folder_state, current_images_state]
        )

    return image_manager_interface


def on_ui_tabs():
    """Create the Image Manager tab"""
    return [(create_image_manager_interface(), "Image Manager", "image_manager")]


# Register the extension
script_callbacks.on_ui_tabs(on_ui_tabs)