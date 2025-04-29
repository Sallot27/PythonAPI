from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from PIL import Image
import ollama
import base64
import io

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
REQUIRED_ANGLES = ['front', 'rear', 'right_side', 'left_side', 'chassis', 'engine']

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_image(image_path):
    with Image.open(image_path) as img:
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

def validate_image_quality(image_path):
    try:
        with Image.open(image_path) as img:
            # Check image resolution
            if img.width < 800 or img.height < 600:
                return False, "Image resolution too low (minimum 800x600)"
            
            # Check if image is blurry (simple variance of Laplacian)
            # You might need to install opencv-python for more advanced checks
            return True, "Image quality OK"
    except Exception as e:
        return False, f"Invalid image: {str(e)}"

def detect_car_part(image_path, expected_part):
    image_base64 = encode_image(image_path)
    
    prompts = {
        'front': "Is this a clear image of the FRONT view of a car? Answer only 'yes' or 'no'.",
        'rear': "Is this a clear image of the REAR view of a car? Answer only 'yes' or 'no'.",
        'right_side': "Is this a clear image of the RIGHT SIDE view of a car? Answer only 'yes' or 'no'.",
        'left_side': "Is this a clear image of the LEFT SIDE view of a car? Answer only 'yes' or 'no'.",
        'chassis': "Is this a clear image of a car's CHASSIS NUMBER? Answer only 'yes' or 'no'.",
        'engine': "Is this a clear image of a car's ENGINE? Answer only 'yes' or 'no'."
    }
    
    response = ollama.chat(
        model='llava:3.2',
        messages=[
            {
                'role': 'user',
                'content': prompts[expected_part],
                'images': [image_base64],
            }
        ]
    )
    answer = response['message']['content'].strip().lower()
    return answer == 'yes'

@app.route('/api/data', methods=['POST'])
def upload_documentation():
    # Validate required fields
    if not request.form.get('ID'):
        return jsonify({"error": "Policy ID is required"}), 400
    if not request.form.get('Ref'):
        return jsonify({"error": "Reference number is required"}), 400
    
    # Validate all required angles are provided
    received_angles = set(request.form.getlist('angles[]'))
    missing_angles = set(REQUIRED_ANGLES) - received_angles
    if missing_angles:
        return jsonify({
            "error": f"Missing required angles: {', '.join(missing_angles)}",
            "required_angles": REQUIRED_ANGLES
        }), 400
    
    # Process each image
    results = {}
    validation_passed = True
    validation_errors = []
    
    for angle in REQUIRED_ANGLES:
        file_key = f"image_{angle}"
        if file_key not in request.files:
            validation_passed = False
            validation_errors.append(f"Missing image for {angle}")
            continue
            
        file = request.files[file_key]
        if not file or file.filename == '':
            validation_passed = False
            validation_errors.append(f"Empty file for {angle}")
            continue
            
        if not allowed_file(file.filename):
            validation_passed = False
            validation_errors.append(f"Invalid file type for {angle}")
            continue
            
        # Save temporarily for processing
        filename = secure_filename(f"{request.form['ID']}_{angle}_{file.filename}")
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        # Validate image quality
        quality_ok, quality_msg = validate_image_quality(temp_path)
        if not quality_ok:
            os.remove(temp_path)
            validation_passed = False
            validation_errors.append(f"{angle}: {quality_msg}")
            continue
            
        # Validate car part
        is_valid_part = detect_car_part(temp_path, angle)
        if not is_valid_part:
            os.remove(temp_path)
            validation_passed = False
            validation_errors.append(f"Image doesn't show valid {angle.replace('_', ' ')} view")
            continue
            
        # If all checks passed
        results[angle] = {
            "filename": filename,
            "status": "validated",
            "message": f"Valid {angle.replace('_', ' ')} view"
        }
    
    if not validation_passed:
        return jsonify({
            "status": "rejected",
            "errors": validation_errors,
            "required_angles": REQUIRED_ANGLES
        }), 400
    
    # If all validations passed, save permanently (in a real app, you'd move to permanent storage)
    return jsonify({
        "status": "approved",
        "ID": request.form['ID'],
        "Ref": request.form['Ref'],
        "results": results,
        "message": "All images validated successfully"
    }), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)