import ollama
from PIL import Image
import base64
import io
import sys

def encode_image(image_path):
    with Image.open(image_path) as img:
        buffered = io.BytesIO()
        img.save(buffered, format="png")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

def detect_car(image_path):
    image_base64 = encode_image(image_path)
    response = ollama.chat(
    model='llava:3.2',  # Use Ollama Vision 3.2
    messages=[
        {
            'role': 'user',
            'content': 'Does this image contain a car? Answer only "yes" or "no".',
            'images': [image_base64],
        }
    ]
)
    answer = response['message']['content'].strip().lower()
    return answer == 'yes'

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python detect_car.py path_to_image")
        sys.exit(1)

    image_path = sys.argv[1]
    if detect_car(image_path):
        print("✅ The image contains a car.")
    else:
        print("❌ The image does not contain a car.")
