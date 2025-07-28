from flask import Flask, render_template_string, request, redirect, url_for, flash, session
import os
import ollama
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key_here'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
IMAGE_PARTS = [
    ('front', 'Front View'),
    ('back', 'Back View'),
    ('right', 'Right Side'),
    ('left', 'Left Side'),
    ('engine', 'Engine'),
    ('chassis_code', 'Chassis Code')
]

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ollama_check(image_path, label):
    prompt = (
        f"You are an insurance assistant. "
        f"This is an image labeled '{label}'. "
        f"Does this photo clearly and authentically show the {label.lower()} of a car for insurance? "
        f"Reply in the following format:\n"
        f"yes - if correct\n"
        f"no: [short reason] - if incorrect (e.g., 'no: blurry image', 'no: not the left side', etc.)\n"
        f"Use only one short sentence if no."
    )
    response = ollama.chat(
        model='qwen2.5vl:3b',
        messages=[{
            'role': 'user',
            'content': prompt,
            'images': [image_path]
        }]
    )
    content = response['message']['content'].strip().lower()
    if content.startswith("yes"):
        return 'yes', ''
    elif content.startswith("no"):
        parts = content.split(":", 1)
        return 'no', parts[1].strip() if len(parts) == 2 else ''
    return 'no', content

@app.route('/', methods=['GET', 'POST'])
def upload_all():
    if request.method == 'POST':
        results = []
        for part, label in IMAGE_PARTS:
            file = request.files.get(part)
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{part}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                try:
                    answer, reason = ollama_check(filepath, label)
                except Exception as e:
                    answer, reason = 'error', str(e)
                results.append({
                    'part': part,
                    'label': label,
                    'filename': filename,
                    'answer': answer,
                    'reason': reason
                })
            else:
                results.append({
                    'part': part,
                    'label': label,
                    'filename': '',
                    'answer': 'no',
                    'reason': 'Missing or invalid file'
                })
        session['results'] = results
        return redirect(url_for('summary'))
    return render_template_string(TEMPLATE_UPLOAD, parts=IMAGE_PARTS)

TEMPLATE_UPLOAD = '''
<!doctype html>
<html lang="en">
<head>
  <title>Car Image Upload</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background: #eef3fc; }
    .container { max-width: 960px; margin-top: 40px; }
    .upload-box { border: 1px dashed #999; padding: 16px; border-radius: 10px; background: #fff; }
    .img-preview { width: 100%; max-height: 180px; object-fit: cover; margin-top: 8px; border-radius: 6px; }

    /* Loading overlay */
    #loading-overlay {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(255,255,255,0.8);
      z-index: 9999;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      display: none;
    }
  </style>
</head>
<body>
  <div class="container">
    <h2 class="text-center mb-4">Upload All Required Car Photos</h2>
    <form method="post" enctype="multipart/form-data" onsubmit="showLoading()">
      <div class="row g-3">
        {% for part, label in parts %}
        <div class="col-md-4">
          <label class="form-label">{{ label }}</label>
          <div class="upload-box">
            <input type="file" class="form-control" name="{{ part }}" accept="image/*" onchange="previewImage(this, '{{ part }}')">
            <img id="preview-{{ part }}" class="img-preview" style="display:none;">
          </div>
        </div>
        {% endfor %}
      </div>
      <div class="text-center mt-4">
        <button class="btn btn-primary px-4" type="submit">Submit All</button>
      </div>
    </form>
  </div>

  <!-- Loading Overlay -->
  <div id="loading-overlay">
    <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;"></div>
    <div class="mt-3 fs-5 text-primary">Processing images, please wait...</div>
  </div>

  <script>
  function previewImage(input, id) {
    const preview = document.getElementById('preview-' + id);
    if (input.files && input.files[0]) {
      const reader = new FileReader();
      reader.onload = function(e) {
        preview.src = e.target.result;
        preview.style.display = 'block';
      }
      reader.readAsDataURL(input.files[0]);
    }
  }

  function showLoading() {
    sessionStorage.setItem('startTime', Date.now());
    document.getElementById('loading-overlay').style.display = 'flex';
  }
</script>

</body>
</html>
'''

TEMPLATE_SUMMARY = '''
<!doctype html>
<html lang="en">
<head>
  <title>Upload Summary</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background: #f8fafc; }
    .container { max-width: 960px; margin-top: 40px; }
    .img-preview { width: 100%; max-height: 200px; object-fit: cover; border-radius: 6px; }
  </style>
</head>
<body>
  <div class="container">
    <h2 class="text-center mb-4">Upload Summary</h2>
    <div class="row g-4">
      {% for r in results %}
      <div class="col-md-4 text-center">
        <h6>{{ r.label }}</h6>
        {% if r.filename %}
          <img src="{{ url_for('uploaded_file', filename=r.filename) }}" class="img-preview mb-2" alt="{{ r.label }}">
        {% else %}
          <div class="text-danger mb-2">No image uploaded</div>
        {% endif %}
        {% if r.answer == 'yes' %}
          <span class="badge bg-success">✔ Valid</span>
        {% elif r.answer == 'no' %}
          <span class="badge bg-danger">✖ Invalid</span>
        {% else %}
          <span class="badge bg-secondary">Error</span>
        {% endif %}
        {% if r.reason %}
          <div class="text-warning mt-1"><small>{{ r.reason }}</small></div>
        {% endif %}
      </div>
      {% endfor %}
    </div>
    <hr>
    <div class="text-center mt-4">
      {% if all_yes %}
        <div class="alert alert-success">✅ All images are valid for insurance purposes.</div>
      {% else %}
        <div class="alert alert-danger">⚠ Some images did not meet the requirements.</div>
      {% endif %}
      <a class="btn btn-outline-primary" href="{{ url_for('upload_all') }}">Try Again</a>
    </div>
  </div>
</body>
</html>
'''

@app.route('/summary')
def summary():
    results = session.get('results', [])
    all_yes = all(r['answer'] == 'yes' for r in results)
    return render_template_string(TEMPLATE_SUMMARY, results=results, all_yes=all_yes)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return app.send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)

