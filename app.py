from flask import Flask, request, jsonify,send_from_directory
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
data_store = []

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/data', methods=['POST'])
def add_data():
    id_value = request.form.get('ID')
    ref_value = request.form.get('Ref')
    
    # Get all uploaded files regardless of field name
    image_files = []
    for file_key in request.files:
        file = request.files[file_key]
        if file and allowed_file(file.filename):
            image_files.append(file)

    if not id_value:
        return jsonify({"error": "ID is required."}), 400

    if not ref_value:
        return jsonify({"error": "Ref is required."}), 400

    saved_paths = []
    for img in image_files:
        try:
            filename = secure_filename(img.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            img.save(save_path)
            saved_paths.append(filename)
        except Exception as e:
            return jsonify({"error": f"Failed to save image: {str(e)}"}), 500

    new_entry = {
        "ID": id_value,
        "Ref": ref_value,
        "images": saved_paths
    }
    data_store.append(new_entry)

    return jsonify({
        "message": "Data successfully saved.",
        "data": new_entry
    }), 201

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        "message": "All data retrieved successfully",
        "data": data_store
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
