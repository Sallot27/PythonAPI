import os
import uuid
import tempfile
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Serve the frontend
@app.route('/')
def index():
    return render_template('index.html')

# Serve uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Image upload endpoint
@app.route('/api/data', methods=['POST'])
def upload_image():
    if 'image_' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image = request.files['image_']
    if image.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    filename = secure_filename(f"{uuid.uuid4().hex}_{image.filename}")
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(path)

    return jsonify({'filename': filename, 'url': f'/uploads/{filename}'})


@app.route('/uploads/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/images')
def list_images():
    files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif'))]
    return jsonify({'images': files})

if __name__ == '__main__':
    app.run(debug=True)
