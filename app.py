from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os

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
    id_value = request.form.get('ID')

    if not id_value:
        return jsonify({'error': 'ID is required'}), 400

    if uploaded_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(uploaded_file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    filename = secure_filename(uploaded_file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    uploaded_file.save(save_path)

    new_entry = {
        "ID": id_value,
        "images": [filename]
    }
    data_store.append(new_entry)

    return jsonify({
        "message": "Data Successfully saved.",
        "data": new_entry
    }), 201

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

