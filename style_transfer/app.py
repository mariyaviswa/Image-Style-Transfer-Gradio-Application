import gradio as gr
from PIL import Image
import os
import time
import style

# ========== Path Configuration ==========
BASE_DIR = "D:/PROJECTS/image_style_transfer/style_transfer"

COLOR_THEME = {
    "primary": "#4B4DED",
    "secondary": "#6C6DEE",
    "accent": "#FF7D45",
    "text": "#2D2E47",
    "background": "#F8F9FA"
}

CUSTOM_CSS = """
footer {visibility: hidden !important}
.section-header {border-bottom: 2px solid #4B4DED; padding-bottom: 8px;}
.dropdown-container {margin-bottom: 1.5rem;}
.upload-button {width: 100% !important;}
"""

# ========== Core Functions ==========
def stylize_image(style_name, source_choice, uploaded_file):
    try:
        # Handle image source
        if source_choice == "custom":
            if not uploaded_file:
                raise ValueError("Please upload an image when selecting 'Custom'")
            
            # Get filename from path
            filename = os.path.basename(uploaded_file)
            input_path = os.path.join(BASE_DIR, "uploaded_images", filename)
            
            # Copy file using proper path handling
            with open(uploaded_file, "rb") as src_file:
                with open(input_path, "wb") as dest_file:
                    dest_file.write(src_file.read())
        else:
            input_path = os.path.join(BASE_DIR, "images/content-images", source_choice)

        # Create output path
        output_dir = os.path.join(BASE_DIR, "images/output-images")
        os.makedirs(output_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        output_path = os.path.join(output_dir, f"result_{timestamp}.jpg")

        # Process image
        model_path = os.path.join(BASE_DIR, "saved_models", f"{style_name}.pth")
        model = style.load_model(model_path)
        style.stylize(model, input_path, output_path)

        return Image.open(output_path), output_path

    except Exception as e:
        raise gr.Error(f"Error processing image: {str(e)}")

# ========== UI Components ==========
def create_header():
    return gr.Markdown(f"""
    <div style="text-align: center; padding: 2rem; background: {COLOR_THEME['primary']}; border-radius: 12px;">
        <h1 style="color: white; margin: 0;">Image Style Transfer</h1>
        <p style="color: rgba(255,255,255,0.9);">Transform your images using style transfer</p>
    </div>
    """)

def create_controls():
    with gr.Group():
        gr.Markdown("### 🎨 Style Configuration", elem_classes="section-header")
        
        style_dd = gr.Dropdown(
            label="Style Model",
            choices=[
                ("Candy Style", "candy"),
                ("Mosaic Art", "mosaic"),
                ("Rain Princess", "rain_princess"),
                ("Udnie Abstract", "udnie")
            ],
            value="candy",
            elem_classes="dropdown-container"
        )
        
        source_dd = gr.Dropdown(
            label="Content Image",
            choices=[
                ("Amber", "amber.jpg"),
                ("Cat", "cat.png"),
                ("Room", "room.jpg"),
                ("Buildings", "buildings.jpg"),
                ("Custom Upload", "custom")
            ],
            value="amber.jpg",
            elem_classes="dropdown-container"
        )
        
        upload_btn = gr.UploadButton(
            "📁 Upload Custom Image",
            file_types=["image"],
            file_count="single",
            visible=False
        )
        
    return style_dd, source_dd, upload_btn

def create_previews():
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Original Image", elem_classes="section-header")
            input_img = gr.Image(interactive=False)
        with gr.Column():
            gr.Markdown("### Style Reference", elem_classes="section-header")
            style_img = gr.Image(interactive=False)
    
    return input_img, style_img

# ========== Main UI ==========
with gr.Blocks(
    title="Image Style Transfer",
    theme=gr.themes.Soft(
        primary_hue="purple",
        secondary_hue="blue"
    ),
    css=CUSTOM_CSS
) as app:
    
    create_header()
    
    with gr.Row():
        # Controls Column
        with gr.Column(scale=1):
            style_ctrl, source_ctrl, upload_ctrl = create_controls()
            process_btn = gr.Button("✨ Generate Style Transfer", variant="primary")
        
        # Previews Column
        with gr.Column(scale=2):
            input_preview, style_preview = create_previews()
            gr.Markdown("### 🎉 Result", elem_classes="section-header")
            output_img = gr.Image(interactive=False)
            download_btn = gr.File(label="Download Result")

    # ========== Event Handlers ==========
    source_ctrl.change(
        lambda x: gr.UploadButton(visible=(x == "custom")),
        inputs=source_ctrl,
        outputs=upload_ctrl
    )
    
    style_ctrl.change(
        lambda x: Image.open(os.path.join(BASE_DIR, "images/style-images", f"{x}.jpg")),
        inputs=style_ctrl,
        outputs=style_preview
    )
    
    source_ctrl.change(
        lambda x: Image.open(os.path.join(BASE_DIR, "images/content-images", x)) if x != "custom" else None,
        inputs=source_ctrl,
        outputs=input_preview
    )
    
    upload_ctrl.upload(
        lambda file: Image.open(file),  # Fixed this line
        inputs=upload_ctrl,
        outputs=input_preview
    )
    
    process_btn.click(
        stylize_image,
        inputs=[style_ctrl, source_ctrl, upload_ctrl],
        outputs=[output_img, download_btn]
    )

# launch the app
app.launch()

