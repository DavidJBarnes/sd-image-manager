import os
import gradio as gr
from modules import script_callbacks
from pathlib import Path


class ImageManagerExtension:
    def __init__(self):
        self.base_path = os.path.expanduser("~/StabilityMatrix-linux-x64/Data/Images/Text2Img")

    def get_folders(self):
        """Get all folders sorted by name (newest first)"""
        if not os.path.exists(self.base_path):
            return []

        folders = []
        for item in os.listdir(self.base_path):
            item_path = os.path.join(self.base_path, item)
            if os.path.isdir(item_path):
                folders.append(item)

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
        return [img[2] for img in images]  # Return just the full paths


def create_image_manager_interface():
    manager = ImageManagerExtension()

    with gr.Blocks(css="""
        .thumbnail-gallery {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            overflow-y: hidden !important;
            gap: 10px;
            padding: 10px;
            max-height: 220px;
        }
        .thumbnail-gallery img {
            width: 200px !important;
            height: 200px !important;
            object-fit: cover !important;
            border-radius: 8px;
            cursor: pointer;
            flex-shrink: 0 !important;
        }
    """) as image_manager_interface:

        gr.HTML("<h2>Image Manager</h2>")

        # State variables
        current_folder = gr.State(value=None)
        current_images = gr.State(value=[])
        current_index = gr.State(value=0)

        with gr.Row():
            with gr.Column(scale=4):
                folder_dropdown = gr.Dropdown(
                    label="Select Folder",
                    choices=manager.get_folders(),
                    value=manager.get_folders()[0] if manager.get_folders() else None,
                    interactive=True
                )
            with gr.Column(scale=1, min_width=100):
                refresh_btn = gr.Button("🔄 Refresh", variant="secondary", size="sm")

        with gr.Row():
            with gr.Column():
                # Main image display
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
            # Simple thumbnail gallery
            thumbnail_gallery = gr.Gallery(
                label="Thumbnails",
                show_label=True,
                elem_id="thumbnail_gallery",
                columns=10,
                rows=1,
                height=220,
                object_fit="cover",
                allow_preview=False,
                elem_classes=["thumbnail-gallery"]
            )

        # Status message for delete operations
        with gr.Row():
            status_message = gr.HTML(value="", elem_id="status_message")

        # Hidden button for delete functionality (triggered by JavaScript)
        delete_btn = gr.Button("Delete", visible=False, elem_id="hidden_delete_btn")

        def refresh_folders():
            """Refresh the folder list and return updated dropdown"""
            print("Refreshing folder list...")

            # Get fresh folder list
            updated_folders = manager.get_folders()
            print(f"Found {len(updated_folders)} folders: {updated_folders}")

            # Return the updated choices and select the first one
            selected_folder = updated_folders[0] if updated_folders else None

            return gr.Dropdown(choices=updated_folders, value=selected_folder), selected_folder

        def update_folder(folder_name):
            """Update when folder changes"""
            if not folder_name:
                return None, [], 0, folder_name, []

            images = manager.get_images_in_folder(folder_name)
            if not images:
                return None, [], 0, folder_name, []

            # Load first image
            first_image = images[0] if images else None

            return first_image, images, 0, folder_name, images

        def navigate_image(direction, folder_name, images, current_idx):
            """Navigate through images"""
            if not images or not folder_name:
                return None, current_idx

            # Ensure index is valid
            current_idx = max(0, min(current_idx, len(images) - 1))

            if direction == "prev" and current_idx > 0:
                current_idx -= 1
            elif direction == "next" and current_idx < len(images) - 1:
                current_idx += 1

            selected_image = images[current_idx] if current_idx < len(images) else None
            return selected_image, current_idx

        def on_thumbnail_select(evt: gr.SelectData):
            """Handle thumbnail selection"""
            return evt.index

        def handle_delete():
            """Handle delete button click from JavaScript"""
            return "Processing delete..."

        def delete_current_image(folder_name, images, current_idx):
            """Delete the currently selected image"""
            if not images or not folder_name or current_idx >= len(images):
                return None, [], 0, "No image to delete"

            try:
                # Get the image to delete
                image_to_delete = images[current_idx]

                # Delete the file
                if os.path.exists(image_to_delete):
                    os.remove(image_to_delete)
                    print(f"Deleted image: {os.path.basename(image_to_delete)}")

                # Refresh the image list
                updated_images = manager.get_images_in_folder(folder_name)

                if not updated_images:
                    return None, [], 0, "No more images in folder"

                # Adjust index if necessary
                new_index = min(current_idx, len(updated_images) - 1)
                new_image = updated_images[new_index] if new_index < len(updated_images) else None

                return new_image, updated_images, new_index, f"Deleted {os.path.basename(image_to_delete)}"

            except Exception as e:
                print(f"Error deleting image: {e}")
                return None, images, current_idx, f"Error: {str(e)}"

        # Event handlers

        # Refresh button - updates dropdown and loads first folder
        refresh_btn.click(
            fn=refresh_folders,
            outputs=[folder_dropdown, current_folder]
        ).then(
            fn=update_folder,
            inputs=[current_folder],
            outputs=[main_image, thumbnail_gallery, current_index, current_folder, current_images]
        )

        folder_dropdown.change(
            fn=update_folder,
            inputs=[folder_dropdown],
            outputs=[main_image, thumbnail_gallery, current_index, current_folder, current_images]
        )

        thumbnail_gallery.select(
            fn=on_thumbnail_select,
            outputs=[current_index]
        ).then(
            fn=lambda images, idx: images[idx] if images and idx < len(images) else None,
            inputs=[current_images, current_index],
            outputs=[main_image]
        )

        prev_btn.click(
            fn=lambda folder, images, idx: navigate_image("prev", folder, images, idx),
            inputs=[current_folder, current_images, current_index],
            outputs=[main_image, current_index]
        )

        next_btn.click(
            fn=lambda folder, images, idx: navigate_image("next", folder, images, idx),
            inputs=[current_folder, current_images, current_index],
            outputs=[main_image, current_index]
        )

        # Delete button handler
        delete_btn.click(
            fn=handle_delete,
            outputs=[status_message]
        ).then(
            fn=lambda folder, images, idx: delete_current_image(folder, images, idx),
            inputs=[current_folder, current_images, current_index],
            outputs=[main_image, thumbnail_gallery, current_index, status_message]
        ).then(
            fn=lambda folder: manager.get_images_in_folder(folder),
            inputs=[current_folder],
            outputs=[current_images]
        )

        # Initialize
        def initialize():
            folders = manager.get_folders()
            if folders:
                return update_folder(folders[0])
            return None, [], 0, None, []

        image_manager_interface.load(
            fn=initialize,
            outputs=[main_image, thumbnail_gallery, current_index, current_folder, current_images]
        )

    return image_manager_interface


def on_ui_tabs():
    """Create the Image Manager tab"""
    return [(create_image_manager_interface(), "Image Manager", "image_manager")]


# Register the extension
script_callbacks.on_ui_tabs(on_ui_tabs)