from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
import os
 
 app = Flask(__name__)
 
 # Configuration
 UPLOAD_FOLDER = 'uploads'
 ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
 
 app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 os.makedirs(UPLOAD_FOLDER, exist_ok=True)
 data_store = []
 
 HTML_PAGE = """
 <!doctype html>
 <html lang="en">
   <head>
     <meta charset="utf-8">
     <title>Image Upload and Gallery</title>
     <style>
       body { font-family: Arial, sans-serif; padding: 20px; }
       .gallery img { max-width: 200px; margin: 10px; border: 1px solid #ccc; border-radius: 10px; }
     </style>
   </head>
   <body>
     <h1>Upload Image</h1>
     <form method="POST" action="/api/data" enctype="multipart/form-data">
       ID: <input type="text" name="ID" required><br>
       Ref: <input type="text" name="Ref" required><br>
       Image: <input type="file" name="image" accept="image/*" multiple required><br><br>
       <input type="submit" value="Upload">
     </form>
     <h2>Uploaded Images</h2>
     <div class="gallery">
       {% for entry in data %}
         {% for img in entry.images %}
           <div>
             <p><strong>{{ entry.ID }}</strong> - {{ entry.Ref }}</p>
             <img src="/uploads/{{ img }}" alt="{{ img }}">
           </div>
         {% endfor %}
       {% endfor %}
     </div>
   </body>
 </html>
 """
 
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
     if not id_value:
         return jsonify({"error": "ID is required."}), 400
 
     if not id_value or not ref_value:
         return jsonify({"error": "ID and Ref are required."}), 400
     if not ref_value:
         return jsonify({"error": "Ref is required."}), 400
 
     # Get all uploaded files
     image_files = []
     for file_key in request.files:
         file = request.files[file_key]
         if file and allowed_file(file.filename):
             image_files.append(file)
 
     saved_paths = []
     for img in image_files:
 @@ -71,13 +55,25 @@ def add_data():
         except Exception as e:
             return jsonify({"error": f"Failed to save image: {str(e)}"}), 500
 
     new_entry = {"ID": id_value, "Ref": ref_value, "images": saved_paths}
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
 if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5000, debug=True)
