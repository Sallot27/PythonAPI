<<<<<<< HEAD
from flask import Flask , request , jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
Upload_Folder = 'uploads'
Allowed_Extentions = {'png' ,'jpg','jpeg' }

app.config['Upload_Folder'] = Upload_Folder
os.makedirs(Upload_Folder , exist_ok=True)
data_store=[]


def allowed_file(filename):
        return '.' in filename and \
                filename.rsplit('.')[1].lower() in Allowed_Extentions


@app.route('/api/data', methods= ['POST'])
def add_data():
    id_value= request.form.get('ID')

    image.files=[]
    for file_key in request.files:
        file = request.files[file_key]
        if file and allowed_file(file.filename):
            image_files.append(file)
    if not id_value:
        return jsonify({"error": "ID is required."}), 400

    saved_paths= [] 
    for img in image_files:
        try:
            filename = secure_filename(img.filename)
            saved_path = os.path.join(app.config['Upload_Folder'], filename)
            img.save(saved_path)
            saved_paths.append(filename)
        except Exception as e:
            return jsonify({"error": f"fialed to save image :  {str(e)}"}), 500

    new_entry= {
        "ID": id_value,
        "images": saved_paths
    }
    data_store.append(new_entry)

    return jsonify({
        "message": "Data Successfully saved.",
        "data" : new_entry}), 201

@app.route("/api/data" , methods=['GET'])
def get_data():
    return jsonify({
        "message": "ALL Data Retrived Successfully",
        "data" : data_store
    })


if __name__ == "__main__":
    app.run(host = '0.0.0.0' , port= 5000 , debug=True)
=======
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from werkzeug.utils import secure_filename
import os
 
 app = Flask(__name__)
 
 # Configuration
 UPLOAD_FOLDER = 'uploads'
 ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
 
 app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 os.makedirs(UPLOAD_FOLDER, exist_ok=True)
 data_store = []
 
 def allowed_file(filename):
     """Check if the uploaded file is allowed."""
     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
 @app.route('/')
 def index():
     return render_template_string(HTML_PAGE, data=data_store)
     """Render the index page."""
     return render_template('index.html', data=data_store)
 
 @app.route('/uploads/<filename>')
 def uploaded_file(filename):
     """Serve the uploaded files."""
     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
 
 @app.route('/api/data', methods=['POST'])
 def add_data():
     """Handle image uploads and data submission."""
     id_value = request.form.get('ID')
     ref_value = request.form.get('Ref')
 
     image_files = [file for file in request.files.values() if allowed_file(file.filename)]
    
 
     if not id_value or not ref_value:
         return jsonify({"error": "ID and Ref are required."}), 40
 
     # Get all uploaded files
     image_files = []
     for file_key in request.files:
         file = request.files[file_key]
         if file and allowed_file(file.filename):
             image_files.append(file)
 
     saved_paths = []
     for img in image_files:
 def add_data():
         except Exception as e:
             return jsonify({"error": f"Failed to save image: {str(e)}"}), 500
 
     new_entry = {
         "ID": id_value,
         "Ref": ref_value,
         "images": saved_paths
     }
     data_store.append(new_entry)
     return jsonify({"message": "Data successfully saved.", "data": new_entry}), 201
 
 @app.route('/uploads/<filename>')
 def uploaded_file(filename):
     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
     return jsonify({
         "message": "Data successfully saved.",
         "data": new_entry
     }), 201
 
 @app.route('/api/data', methods=['GET'])
 def get_data():
     """Retrieve all uploaded data."""
     return jsonify({
         "message": "All data retrieved successfully",
         "data": data_store
     })
 
 port = int(os.environ.get("PORT", 5000))
 app.run(host='0.0.0.0', port=port)
 
>>>>>>> f68458da565b5379ddb9a778fd2e5be97362b4e3
