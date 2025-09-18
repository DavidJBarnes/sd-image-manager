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
        """Get all folders in the base directory, sorted by folder name (newest first)"""
        if not os.path.exists(self.base_path):
            return []

        folders = []
        for item in os.listdir(self.base_path):
            item_path = os.path.join(self.base_path, item)
            if os.path.isdir(item_path):
                folders.append(item)

        # Sort by folder name descending (assuming date format YYYY-MM-DD)
        folders.sort(reverse=True)
        return folders

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


def create_thumbnail_html(images, selected_index=0):
    """Create custom HTML for horizontal thumbnail gallery"""
    if not images:
        return "<div id='custom-thumbnail-gallery' style='width: 100%; height: 220px; overflow-x: auto; overflow-y: hidden; display: flex; gap: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 8px; background: #f8f9fa;'>No images found</div>"

    html_parts = [
        "<div id='custom-thumbnail-gallery' style='width: 100%; height: 220px; overflow-x: auto; overflow-y: hidden; display: flex; gap: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 8px; background: #f8f9fa;'>"]

    for i, (filename, filepath) in enumerate(images):
        selected_class = "selected" if i == selected_index else ""
        html_parts.append(f"""
            <img src="file/{filepath}" 
                 data-index="{i}" 
                 data-filepath="{filepath}"
                 class="thumbnail-img {selected_class}" 
                 onclick="selectThumbnail({i}, '{filepath}')"
                 style="width: 200px; height: 200px; object-fit: cover; border-radius: 8px; cursor: pointer; flex-shrink: 0; transition: transform 0.2s ease, box-shadow 0.2s ease; {('border: 3px solid #2563eb; box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.3);' if i == selected_index else '')}"
                 onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 4px 12px rgba(0, 0, 0, 0.3)'; this.style.zIndex='10';"
                 onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='{('0 0 0 2px rgba(37, 99, 235, 0.3)' if i == selected_index else 'none')}'; this.style.zIndex='1';"
                 title="{filename}">
        """)

    html_parts.append("</div>")
    return "".join(html_parts)


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
            # Custom horizontal thumbnail gallery using HTML
            with gr.Column():
                thumbnail_html = gr.HTML(
                    value="<div id='custom-thumbnail-gallery' style='width: 100%; height: 220px; overflow-x: auto; overflow-y: hidden; display: flex; gap: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 8px; background: #f8f9fa;'></div>",
                    elem_id="thumbnail_container"
                )

        def update_folder_content(folder_name):
            """Update content when folder selection changes"""
            if not folder_name:
                return None, "", 0, folder_name, []

            images = manager.get_images_in_folder(folder_name)
            if not images:
                return None, "", 0, folder_name, images

            # Load first image
            first_image = manager.load_image(images[0][1])

            # Create custom thumbnail HTML
            thumbnail_html_content = create_thumbnail_html(images, 0)

            return first_image, thumbnail_html_content, 0, folder_name, images

        def navigate_images(direction):
            """Handle image navigation - called by buttons and returns updated state"""
            folder_name = current_folder_state.value
            current_index = current_index_state.value if current_index_state.value is not None else 0

            if not folder_name:
                return None, "", current_index

            images = manager.get_images_in_folder(folder_name)
            if not images:
                return None, "", 0

            # Ensure current_index is within bounds
            current_index = max(0, min(current_index, len(images) - 1))

            if direction == "prev" and current_index > 0:
                current_index -= 1
            elif direction == "next" and current_index < len(images) - 1:
                current_index += 1

            selected_image = manager.load_image(images[current_index][1])
            updated_html = create_thumbnail_html(images, current_index)

            return selected_image, updated_html, current_index

        # Custom JavaScript handler for thumbnail clicks
        def handle_thumbnail_click(index_str):
            """Handle thumbnail selection from JavaScript"""
            try:
                index = int(index_str) if index_str else 0
                folder_name = current_folder_state.value

                if not folder_name:
                    return None, "", index

                images = manager.get_images_in_folder(folder_name)
                if index < len(images):
                    selected_image = manager.load_image(images[index][1])
                    updated_html = create_thumbnail_html(images, index)
                    return selected_image, updated_html, index
            except:
                pass

            return None, "", 0

        # Hidden textbox to receive JavaScript events
        js_event_box = gr.Textbox(visible=False, elem_id="js_event_box")

        # Event handlers
        folder_dropdown.change(
            fn=update_folder_content,
            inputs=[folder_dropdown],
            outputs=[main_image, thumbnail_html, current_index_state, current_folder_state, current_images_state]
        )

        # Handle JavaScript events
        js_event_box.change(
            fn=handle_thumbnail_click,
            inputs=[js_event_box],
            outputs=[main_image, thumbnail_html, current_index_state]
        )

        prev_btn.click(
            fn=lambda: navigate_images("prev"),
            outputs=[main_image, thumbnail_html, current_index_state]
        )

        next_btn.click(
            fn=lambda: navigate_images("next"),
            outputs=[main_image, thumbnail_html, current_index_state]
        )

        # Initialize with first folder if available
        def initialize_interface():
            folders = manager.get_folders()
            if folders:
                return update_folder_content(folders[0])
            return None, "", 0, None, []

        # Load initial content
        image_manager_interface.load(
            fn=initialize_interface,
            outputs=[main_image, thumbnail_html, current_index_state, current_folder_state, current_images_state]
        )

    return image_manager_interface


def on_ui_tabs():
    """Create the Image Manager tab"""
    return [(create_image_manager_interface(), "Image Manager", "image_manager")]


# Register the extension
script_callbacks.on_ui_tabs(on_ui_tabs)