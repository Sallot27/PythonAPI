from flask import Flask, render_template_string, request, redirect, url_for, flash, session, send_from_directory
import os
import time
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

def cleanup_uploads(folder, max_age=3600):
    now = time.time()
    for f in os.listdir(folder):
        f_path = os.path.join(folder, f)
        if os.path.isfile(f_path) and now - os.path.getmtime(f_path) > max_age:
            os.remove(f_path)

def ollama_check(image_path, label):
    prompt = (
        f"You are an insurance assistant. "
        f"This is an image labeled '{label}'. "
        f"Does this photo clearly and authentically show the {label.lower()} of a car for insurance? "
        f"Reply in the following format:\n"
        f"yes - if correct\n"
        f"no: [short reason] - if incorrect\n"
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
    retry_part = request.args.get('retry')
    if retry_part:
        part_label = next((lbl for p, lbl in IMAGE_PARTS if p == retry_part), None)
        return render_template_string(TEMPLATE_UPLOAD, parts=[(retry_part, part_label)])

    if request.method == 'POST':
        cleanup_uploads(app.config['UPLOAD_FOLDER'])
        results = []
        for part, label in IMAGE_PARTS:
            file = request.files.get(part)
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{part}_{int(time.time())}_{file.filename}")
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

@app.route('/summary')
def summary():
    results = session.get('results', [])
    all_yes = all(r['answer'] == 'yes' for r in results)
    success_count = sum(1 for r in results if r['answer'] == 'yes')
    failure_count = sum(1 for r in results if r['answer'] == 'no')
    error_count = sum(1 for r in results if r['answer'] not in ('yes', 'no'))
    return render_template_string(TEMPLATE_SUMMARY, results=results, all_yes=all_yes,
                                  success_count=success_count, failure_count=failure_count, error_count=error_count)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# TEMPLATE_UPLOAD and TEMPLATE_SUMMARY follow as before or can be improved further with JS loading, progress, etc.

if __name__ == '__main__':
    app.run(debug=True)
