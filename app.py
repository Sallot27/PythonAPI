from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

Allowed_Extentions = {'png', 'jpg', 'jpeg'}
app.config['Upload_Folder'] = Upload_Folder
data_store = []

@app.route('/')
def index():
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.')[1].lower() in Allowed_Extentions


@app.route('/api/data', methods=['POST'])
def add_data():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    uploaded_file = request.files['image']

    # Example usage:
    filename = uploaded_file.filename
    uploaded_file.save(f'uploads/{filename}')  # Save file to disk or process as needed

    return jsonify({'message': 'File uploaded successfully'}), 200

    new_entry = {
        "ID": id_value,
        "images": saved_paths
    }
    data_store.append(new_entry)

    return jsonify({
        "message": "Data Successfully saved.",
        "data": new_entry}), 201

@app.route("/api/data", methods=['GET'])
def get_data():
    return jsonify({
        "message": "ALL Data Retrived Successfully",
        "data": data_store
    })

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

