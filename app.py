from detect_car import detect_car

from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__, template_folder='templates')


# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory data store (replace with database in production)
data_store = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/data', methods=['POST'])
def init_submission():
    """Initialize a new submission with ID and Ref"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        id_value = data.get('ID')
        ref_value = data.get('Ref')
        
        if not id_value or not ref_value:
            return jsonify({"error": "Both ID and Ref are required"}), 400
        
        # Create a new submission entry
        submission_id = f"{id_value}_{ref_value}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        data_store[submission_id] = {
            "ID": id_value,
            "Ref": ref_value,
            "images": [],
            "status": "in_progress",
            "created_at": datetime.now().isoformat()
        }
        
        return jsonify({
            "message": "Submission initialized",
            "submission_id": submission_id
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data', methods=['POST'])
def upload_data():
    """Handle image uploads from Flutter app with multiple images and fields"""
    try:
        # Extract ID and Ref from form fields
        id_value = request.form.get('ID')
        ref_value = request.form.get('Ref')
        
        if not id_value or not ref_value:
            return jsonify({"error": "Both ID and Ref are required"}), 400
        
        # Create or find submission_id
        submission_id = None
        for sid, data in data_store.items():
            if data['ID'] == id_value and data['Ref'] == ref_value and data['status'] == 'in_progress':
                submission_id = sid
                break
        if not submission_id:
            submission_id = f"{id_value}_{ref_value}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            data_store[submission_id] = {
                "ID": id_value,
                "Ref": ref_value,
                "images": [],
                "status": "in_progress",
                "created_at": datetime.now().isoformat()
            }
        
        # Process image files named image_0, image_1, etc.
        image_files = []
        for key in request.files:
            if key.startswith('image_'):
                image_files.append((int(key.split('_')[1]), request.files[key]))
        
        # Sort by index
        image_files.sort(key=lambda x: x[0])
        
        for index, file in image_files:
            if file and allowed_file(file.filename):
                filename = f"{submission_id}_image{index}_{secure_filename(file.filename)}"
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(save_path)
                
                if len(data_store[submission_id]["images"]) <= index:
                    data_store[submission_id]["images"].append(filename)
                else:
                    data_store[submission_id]["images"][index] = filename
            else:
                return jsonify({"error": f"File type not allowed for image {index}"}), 400
        
        return jsonify({"message": "Images uploaded successfully", "submission_id": submission_id}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload_image/<submission_id>/<int:image_index>', methods=['POST'])
def upload_image(submission_id, image_index):
    """Handle individual image uploads"""
    try:
        if submission_id not in data_store:
            return jsonify({"error": "Invalid submission ID"}), 404
            
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        if file and allowed_file(file.filename):
            # Generate unique filename
            filename = f"{submission_id}_image{image_index}_{secure_filename(file.filename)}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save the file
            file.save(save_path)

            # Run car detection on the saved image
            if not detect_car(save_path):
                # Delete the image if no car detected
                os.remove(save_path)
                return jsonify({"error": "No car detected in the image"}), 400
            
            # Update submission data
            if len(data_store[submission_id]["images"]) <= image_index:
                data_store[submission_id]["images"].append(filename)
            else:
                data_store[submission_id]["images"][image_index] = filename
            
            return jsonify({
                "message": "Image uploaded successfully",
                "filename": filename,
                "image_index": image_index
            }), 200
            
        return jsonify({"error": "File type not allowed"}), 400
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/complete_submission/<submission_id>', methods=['POST'])
def complete_submission(submission_id):
    """Mark submission as complete"""
    try:
        if submission_id not in data_store:
            return jsonify({"error": "Invalid submission ID"}), 404
            
        data_store[submission_id]["status"] = "completed"
        data_store[submission_id]["completed_at"] = datetime.now().isoformat()
        
        return jsonify({
            "message": "Submission completed successfully",
            "submission": data_store[submission_id]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/submission_status/<submission_id>', methods=['GET'])
def submission_status(submission_id):
    """Check submission status"""
    if submission_id not in data_store:
        return jsonify({"error": "Submission not found"}), 404
        
    return jsonify(data_store[submission_id]), 200

@app.route('/', methods=['GET'])
def index():
    """Serve index.html"""
    return send_from_directory(app.template_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


