from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# HTML Template for viewing images
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Image Gallery</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 40px; }
        img { max-width: 300px; margin: 10px; border: 2px solid #ccc; border-radius: 8px; }
    </style>
</head>
<body>
    <h1>Uploaded Images</h1>
    <div>
        {% for image in images %}
            <img src="{{ url_for('uploaded_file', filename=image) }}" alt="{{ image }}">
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route('/')
def gallery():
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template_string(HTML_TEMPLATE, images=images)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/data', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return jsonify({"message": "Image uploaded", "filename": filename}), 200

if __name__ == '__main__':
    app.run(debug=True)
