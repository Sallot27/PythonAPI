import ollama
from PIL import Image
import base64
import io
import sys
import os

def encode_image(image_path):
    with Image.open(image_path) as img:
        buffered = io.BytesIO()
        img.save(buffered, format="png")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

def detect_car(image_path):
    image_base64 = encode_image(image_path)
    response = ollama.chat(
        model='llava:3.2',
        messages=[
            {
                'role': 'user',
                'content': 'Does this image contain a car or part of a car? Answer only "yes" or "no".',
                'images': [image_base64],
            }
        ]
    )
    answer = response['message']['content'].strip().lower()
    return answer == 'yes'

def process_image(image_path, output_dir="cars"):
    try:
        if detect_car(image_path):
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Save the image
            filename = os.path.basename(image_path)
            output_path = os.path.join(output_dir, filename)
            
            # Handle duplicate filenames
            counter = 1
            while os.path.exists(output_path):
                name, ext = os.path.splitext(filename)
                output_path = os.path.join(output_dir, f"{name}_{counter}{ext}")
                counter += 1
            
            with Image.open(image_path) as img:
                img.save(output_path)
            print(f"✅ Car detected. Image saved to: {output_path}")
            return True
        else:
            # Delete the image if no car is detected
            os.remove(image_path)
            print("❌ No car detected. Image disposed.")
            return False
    except Exception as e:
        print(f"⚠️ Error processing image: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python detect_car.py path_to_image")
        sys.exit(1)

    image_path = sys.argv[1]
    process_image(image_path)
