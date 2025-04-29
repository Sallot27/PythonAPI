from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Enable CORS (important for Flutter)
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST')
    return response

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['POST'])
def add_data():
    # Check if the request contains files
    if not request.files:
        return jsonify({"error": "No files provided"}), 400

    # Get form data
    id_value = request.form.get('ID')
    ref_value = request.form.get('Ref')
    
    if not id_value or not ref_value:
        return jsonify({"error": "Both ID and Ref are required"}), 400

    saved_files = []
    errors = []

    # Process each file
    for file_key in request.files:
        file = request.files[file_key]
        
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                saved_files.append(filename)
            except Exception as e:
                errors.append(f"Failed to save {file.filename}: {str(e)}")
        else:
            errors.append(f"Invalid file type: {file.filename}")

    if errors:
        return jsonify({
            "message": "Some files failed to upload",
            "saved_files": saved_files,
            "errors": errors
        }), 207  # Multi-status

    return jsonify({
        "message": "All files uploaded successfully",
        "saved_files": saved_files,
        "ID": id_value,
        "Ref": ref_value
    }), 201

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)