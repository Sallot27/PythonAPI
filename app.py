from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os
import tempfile
import atexit

app = Flask(__name__)

# Temporary in-memory storage (resets on server restart)
temp_storage = []
temp_dir = tempfile.mkdtemp()

# Cleanup function
def cleanup():
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("Cleaned up temporary files")

atexit.register(cleanup)

@app.route('/')
def index():
    # Only show images currently in temp storage
    return render_template('index.html', images=temp_storage)

@app.route('/api/data', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file:
        filename = secure_filename(file.filename)
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        # Store in temporary list
        temp_storage.append(filename)
        
        return jsonify({
            "message": "File temporarily uploaded",
            "filename": filename,
            "warning": "Files will disappear after refresh"
        }), 201

@app.route('/temp/<filename>')
def serve_temp(filename):
    return send_from_directory(temp_dir, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)