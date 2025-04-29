from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from detect_car import detect_car
import os

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
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

@app.route('/api/data', methods=['POST'])
def add_data():
    """Handle image uploads and data submission."""
    id_value = request.form.get('ID')
    ref_value = request.form.get('Ref')

    if not id_value or not ref_value:
        return jsonify({"error": "ID and Ref are required."}), 400

    image_files = []
    for file_key in request.files:
        file = request.files[file_key]
        if file and allowed_file(file.filename):
            image_files.append(file)

    saved_paths = []
    for img in image_files:
        filename = secure_filename(img.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img.save(save_path)

        try:
            if detect_car(save_path):
                saved_paths.append(filename)
            else:
                os.remove(save_path)  # delete image without car
        except Exception as e:
            if os.path.exists(save_path):
                os.remove(save_path)
            print(f"Error checking image: {e}")

    if not saved_paths:
        return jsonify({"error": "No valid car images were uploaded."}), 400

    new_entry = {
        "ID": id_value,
        "Ref": ref_value,
        "images": saved_paths,
        "statuses": image_statuses,  # include AI results for rendering
        "date": datetime.now().strftime("%Y-%m-%d")
                }
    data_store.append(new_entry)

    return jsonify({
        "message": "Data saved (only car images kept).",
        "data": new_entry
    }), 201


@app.route('/api/data', methods=['GET'])
def get_data():
    """Retrieve all uploaded data."""
    return jsonify({
        "message": "All data retrieved successfully",
        "data": data_store
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)