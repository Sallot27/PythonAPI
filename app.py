from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from detect_car import process_image  # Using the modified version from previous code
import os
from PIL import Image

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
CAR_IMAGES_FOLDER = 'car_images'  # Folder to store images with cars
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CAR_IMAGES_FOLDER'] = CAR_IMAGES_FOLDER

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CAR_IMAGES_FOLDER, exist_ok=True)

data_store = []

def allowed_file(filename):
    """Check if the uploaded file is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the index page."""
    return render_template('index.html', data=data_store)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve the uploaded files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/car_images/<filename>')
def car_image_file(filename):
    """Serve the car images."""
    return send_from_directory(app.config['CAR_IMAGES_FOLDER'], filename)

@app.route('/api/data', methods=['POST'])
def add_data():
    """Handle image uploads and data submission."""
    id_value = request.form.get('ID')
    ref_value = request.form.get('Ref')

    if not id_value:
        return jsonify({"error": "ID is required."}), 400

    if not ref_value:
        return jsonify({"error": "Ref is required."}), 400

    # Get all uploaded files
    image_files = []
    for file_key in request.files:
        file = request.files[file_key]
        if file and allowed_file(file.filename):
            image_files.append(file)

    saved_paths = []
    rejected_images = []
    for img in image_files:
        try:
            # First save to temp location for processing
            filename = secure_filename(img.filename)
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            img.save(temp_path)
            
            # Process the image (will be moved to car_images if contains car)
            process_image(temp_path, output_dir=app.config['CAR_IMAGES_FOLDER'])
            
            # Check if image was kept (has car)
            final_path = os.path.join(app.config['CAR_IMAGES_FOLDER'], filename)
            if os.path.exists(final_path):
                saved_paths.append(os.path.join('car_images', filename))
            else:
                rejected_images.append(filename)
                
        except Exception as e:
            # Clean up if something went wrong
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({
                "error": f"Failed to process image {filename}: {str(e)}",
                "rejected_images": rejected_images,
                "saved_images": saved_paths
            }), 500

    new_entry = {
        "ID": id_value,
        "Ref": ref_value,
        "images": saved_paths,
        "rejected_images": rejected_images
    }
    data_store.append(new_entry)

    return jsonify({
        "message": "Data successfully processed.",
        "data": new_entry,
        "stats": {
            "total_uploaded": len(image_files),
            "accepted": len(saved_paths),
            "rejected": len(rejected_images)
        }
    }), 201

@app.route('/api/data', methods=['GET'])
def get_data():
    """Retrieve all uploaded data."""
    return jsonify({
        "message": "All data retrieved successfully",
        "data": data_store,
        "stats": {
            "total_entries": len(data_store),
            "total_images": sum(len(entry['images']) for entry in data_store)
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)