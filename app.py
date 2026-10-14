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

# Максимальный уровень DEFLATE-сжатия для PNG (диапазон 0-9).
# Сжатие PNG полностью lossless: пиксели остаются бит-в-бит неизменными,
# меняется только размер упакованного потока.
PNG_COMPRESS_LEVEL = 9

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _preserved_metadata(img):
    """Собирает метаданные, которые нужно перенести в сжатый файл.

    EXIF хранит поворот камеры, ICC-профиль отвечает за передачу цвета, а DPI
    влияет на размер страницы в PDF. Без них картинка в PDF может оказаться
    повёрнутой, с изменёнными цветами или в неправильном масштабе.
    """
    metadata = {}

    exif = img.info.get('exif')
    if exif:
        metadata['exif'] = exif

    icc_profile = img.info.get('icc_profile')
    if icc_profile:
        metadata['icc_profile'] = icc_profile

    dpi = img.info.get('dpi')
    if dpi:
        metadata['dpi'] = dpi

    return metadata

def compress_image_lossless(source_path, output_dir, index):
    """Сжимает картинку без потери качества и возвращает путь к результату.

    * PNG пересохраняется lossless: optimize=True подбирает оптимальные
      PNG-фильтры, а compress_level=9 включает максимальное DEFLATE-сжатие.
      Пиксели (включая альфа-канал) остаются бит-в-бит неизменными, а img2pdf
      встраивает этот же поток в PDF как есть — итоговый PDF становится меньше.
    * JPEG (JPG) не перекодируется: img2pdf встраивает исходные байты JPEG в
      PDF без пересжатия (фильтр DCTDecode), а любое повторное сжатие JPEG в
      Pillow (даже c quality="keep") меняет пиксели. Поэтому исходный файл
      возвращается как есть — так качество гарантированно не теряется.
    * Если сжатая версия получилась не меньше исходной либо режим картинки не
      поддерживается PNG-энкодером, возвращается исходный файл.

    :param source_path: путь к загруженному файлу во временной директории
    :param output_dir: директория, куда сохраняется сжатая копия
    :param index: порядковый номер картинки (для уникального имени файла)
    :return: путь к файлу, который нужно передать в img2pdf
    """
    with Image.open(source_path) as original:
        original.load()

        if original.format == 'JPEG':
            # JPEG уже сжат с потерями, поэтому перекодирование только ухудшит
            # картинку. Отдаём исходный файл: img2pdf встроит его без потерь.
            return source_path

        compressed_path = os.path.join(output_dir, f'compressed_{index}.png')
        try:
            original.save(
                compressed_path,
                'PNG',
                optimize=True,                      # подбор оптимальных PNG-фильтров
                compress_level=PNG_COMPRESS_LEVEL,  # максимум lossless-сжатия
                **_preserved_metadata(original)
            )
        except Exception:
            # Экзотические режимы (например, CMYK), которые Pillow не умеет
            # сохранять в PNG: отдаём исходный файл, img2pdf разберётся сам.
            return source_path

        # Сжатую копию используем только если она действительно меньше исходной.
        if os.path.getsize(compressed_path) >= os.path.getsize(source_path):
            return source_path

        return compressed_path

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
                
                # Validate the image and compress it without quality loss
                try:
                    compressed_path = compress_image_lossless(temp_path, temp_dir, i + 1)
                    image_paths.append(compressed_path)
                except Exception:
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
            'message': 'Some images with transparency could not be converted to PDF',
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
        'usage_notes': 'Send multiple files with field name "files"',
        'compression': 'Lossless: PNG is re-packed with maximum DEFLATE compression, '
                       'JPEG is embedded into the PDF without re-encoding '
                       '(DCTDecode), so image quality is never degraded'
    })

if __name__ == '__main__':
    print("Starting Flask server on port 3000...")
    print("Image to PDF endpoint available at: http://localhost:3000/api/images-to-pdf")
    app.run(host='0.0.0.0', port=3000, debug=True, use_reloader=False)