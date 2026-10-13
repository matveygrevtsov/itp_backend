from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import tempfile
import io
from PIL import Image
import img2pdf

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure upload settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return jsonify({
        'message': 'Hello from Flask backend!',
        'status': 'success',
        'timestamp': '2026-10-13 12:01:00'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Flask Backend',
        'port': 3000
    })

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    return jsonify({
        'data': 'This is a test endpoint',
        'items': [1, 2, 3, 4, 5]
    })

@app.route('/api/echo/<message>', methods=['GET'])
def echo_message(message):
    return jsonify({
        'received': message,
        'echo': f'You said: {message}'
    })

@app.route('/api/images-to-pdf', methods=['POST'])
def images_to_pdf():
    """
    Convert multiple images to a single PDF file.
    Accepts multiple image files in request.
    Returns PDF file as response.
    """
    try:
        # Check if files are present in the request
        if 'files' not in request.files:
            return jsonify({
                'error': 'No files provided',
                'message': 'Please provide image files in the "files" field'
            }), 400
        
        files = request.files.getlist('files')
        
        # Check if at least one file was provided
        if len(files) == 0 or (len(files) == 1 and files[0].filename == ''):
            return jsonify({
                'error': 'No files selected',
                'message': 'Please select at least one image file'
            }), 400
        
        valid_files = []
        invalid_files = []
        
        # Validate each file
        for file in files:
            if file and allowed_file(file.filename):
                valid_files.append(file)
            else:
                invalid_files.append(file.filename)
        
        if not valid_files:
            return jsonify({
                'error': 'No valid image files',
                'message': 'No valid image files provided. Supported formats: PNG, JPG, JPEG',
                'invalid_files': invalid_files
            }), 400
        
        # Create a temporary directory to store images
        with tempfile.TemporaryDirectory() as temp_dir:
            image_paths = []
            
            # Save uploaded images to temporary directory
            for i, file in enumerate(valid_files):
                # Generate a unique filename
                file_ext = file.filename.rsplit('.', 1)[1].lower()
                temp_filename = f"image_{i+1}.{file_ext}"
                temp_path = os.path.join(temp_dir, temp_filename)
                
                # Save the file
                file.save(temp_path)
                
                # Open and validate image with Pillow
                try:
                    with Image.open(temp_path) as img:
                        # Convert to RGB if necessary (for PNG with transparency)
                        if img.mode in ('RGBA', 'LA', 'P'):
                            rgb_img = img.convert('RGB')
                            rgb_path = os.path.join(temp_dir, f"rgb_{i+1}.jpg")
                            rgb_img.save(rgb_path, 'JPEG', quality=95)
                            image_paths.append(rgb_path)
                        else:
                            image_paths.append(temp_path)
                except Exception as e:
                    # If image is invalid, remove it from the list
                    invalid_files.append(file.filename)
                    continue
            
            if not image_paths:
                return jsonify({
                    'error': 'No valid images to process',
                    'message': 'All provided images were invalid or corrupted'
                }), 400
            
            # Convert images to PDF
            pdf_bytes = img2pdf.convert(image_paths)
            
            # Create a BytesIO object for the PDF
            pdf_stream = io.BytesIO(pdf_bytes)
            pdf_stream.seek(0)
            
            # Return PDF as response
            return send_file(
                pdf_stream,
                mimetype='application/pdf',
                as_attachment=True,
                download_name='merged_images.pdf'
            )
            
    except img2pdf.AlphaChannelError as e:
        return jsonify({
            'error': 'Image processing error',
            'message': 'Some images have transparency (alpha channel) and cannot be converted to PDF directly',
            'details': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

# Additional endpoint to check if service is working with images
@app.route('/api/pdf-info', methods=['GET'])
def pdf_info():
    """Return information about the PDF conversion service."""
    return jsonify({
        'service': 'Image to PDF Converter',
        'status': 'active',
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size': '16MB',
        'max_files': 'No limit (within reasonable memory constraints)',
        'endpoint': '/api/images-to-pdf (POST)',
        'usage_notes': 'Send multiple files with field name "files"'
    })

if __name__ == '__main__':
    print("Starting Flask server on port 3000...")
    print("Image to PDF endpoint available at: http://localhost:3000/api/images-to-pdf")
    app.run(host='0.0.0.0', port=3000, debug=True, use_reloader=False)