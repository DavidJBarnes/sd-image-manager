# Image Manager Extension for Automatic1111 WebUI

A powerful extension that adds an Image Manager tab to your A1111 WebUI for browsing and managing generated images.

## Features

- **Folder Navigation**: Browse through your Text2Img output folders
- **Thumbnail Gallery**: View thumbnails of all images in the selected folder
- **Full-Size Preview**: Click thumbnails to view images at full size
- **Keyboard Navigation**: Use arrow keys to navigate through images
- **Auto-Selection**: Automatically selects the most recent folder on load
- **Responsive Design**: Clean, modern interface with hover effects

## Installation

### Method 1: Manual Installation

1. Navigate to your A1111 WebUI extensions directory:
   ```bash
   cd /path/to/automatic1111-webui/extensions/
   ```

2. Create the extension directory:
   ```bash
   mkdir image-manager
   cd image-manager
   ```

3. Create the required files and directory structure:
   ```
   extensions/image-manager/
   ├── __init__.py
   ├── scripts/
   │   └── image_manager.py
   └── javascript/
       └── image_manager.js
   ```

4. Copy the provided code into the respective files:
   - Copy the main Python code into `scripts/image_manager.py`
   - Copy the JavaScript code into `javascript/image_manager.js` 
   - Create an empty `__init__.py` file

5. Restart your A1111 WebUI

### Method 2: Git Clone (if you have the code in a repository)

```bash
cd /path/to/automatic1111-webui/extensions/
git clone <repository-url> image-manager
```

## Configuration

The extension is configured to work with the default StabilityMatrix directory structure:
- Base path: `~/StabilityMatrix-linux-x64/Data/Images/Text2Img`

If your images are stored elsewhere, modify the `base_path` in the `ImageManagerExtension.__init__()` method:

```python
self.base_path = "/your/custom/path/to/images"
```

## Usage

1. **Access the Extension**: After installation, you'll see an "Image Manager" tab in your A1111 WebUI interface.

2. **Select a Folder**: Use the dropdown menu to select which folder of images you want to view. The most recent folder is selected by default.

3. **Browse Images**: 
   - Thumbnails appear at the bottom of the interface
   - Click any thumbnail to view the full-size image above
   - Use the Previous/Next buttons or arrow keys to navigate

4. **Keyboard Shortcuts**:
   - `←` (Left Arrow): Previous image
   - `→` (Right Arrow): Next image  
   - `Home`: Jump to first image
   - `End`: Jump to last image

## Supported File Formats

- PNG
- JPG/JPEG
- WebP
- BMP
- TIFF

## Folder Structure Expected

The extension expects your images to be organized like this:
```
~/StabilityMatrix-linux-x64/Data/Images/Text2Img/
├── 2024-01-15_10-30-45/
│   ├── image_001.png
│   ├── image_002.png
│   └── ...
├── 2024-01-15_11-15-20/
│   ├── image_001.png
│   └── ...
└── ...
```

## Troubleshooting

### Extension doesn't appear in tabs
- Ensure all files are in the correct locations
- Check the A1111 WebUI console for any Python errors
- Restart the WebUI completely

### Images not loading
- Verify the `base_path` points to your actual images directory
- Check file permissions on the images directory
- Ensure image files have supported extensions

### Keyboard navigation not working
- Make sure you're not focused on an input field
- Try clicking somewhere in the Image Manager tab area first
- Check browser console for JavaScript errors

## Customization

### Changing the thumbnail size
Modify the `thumbnail_gallery` configuration in the Python code:
```python
thumbnail_gallery = gr.Gallery(
    columns=8,  # Change number of columns
    rows=2,     # Change number of rows  
    height="200px"  # Adjust height
)
```

### Adding more keyboard shortcuts
Extend the `handleKeyboardNavigation()` function in the JavaScript file to add more key bindings.

## Development

To extend this extension:

1. The main logic is in `scripts/image_manager.py`
2. UI enhancements can be added via `javascript/image_manager.js`
3. The extension uses Gradio components for the interface
4. State management is handled through Gradio State components

## License

[Specify your license here]

## Contributing

[Add contribution guidelines here]