import os
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Check allowed file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Gallery</title>
      <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet" />
    </head>
    <body class="bg-gray-50 min-h-screen p-6">
      <h1 class="text-3xl font-bold mb-4">Image Gallery</h1>
      <form action="/api/data" method="post" enctype="multipart/form-data" class="mb-6">
        <input type="file" name="image" accept="image/*" required class="mb-2"/>
        <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded">Upload</button>
      </form>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        {% for filename in files %}
          <div>
            <img src="{{ url_for('uploaded_file', filename=filename) }}" class="rounded shadow"/>
            <p class="text-sm text-gray-600 mt-1">{{ filename }}</p>
          </div>
        {% endfor %}
      </div>
    </body>
    </html>
    ''', files=os.listdir(app.config['UPLOAD_FOLDER']))

@app.route('/api/data', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part in request'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename})

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/images')
def list_images():
    files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if allowed_file(f)]
    return jsonify(files)

if __name__ == '__main__':
    app.run(debug=True)
