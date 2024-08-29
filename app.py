from flask import Flask, request, jsonify
import subprocess
import os
import sys
from flask_cors import CORS
from flask import send_from_directory

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)



@app.route('/generate_lipsync', methods=['POST'])
def generate_lipsync():
    try:
        # Get the input parameters from the request
        audio_file = request.json.get('audio_file')
        image_file = request.json.get('image_file')
        enhancer = request.json.get('enhancer', 'gfpgan')
        
        # Ensure that the files exist
        # if not os.path.exists(audio_file) or not os.path.exists(image_file):
        #     return jsonify({'error': 'Audio or image file not found'}), 400
        
          # Get the path to the Python interpreter in the virtual environment
        python_executable = sys.executable
        
        # Construct the command to run the script
        command = [
            python_executable, 'inference.py',
            '--driven_audio', audio_file,
            '--source_image', image_file,
            '--enhancer', enhancer
        ]
        
        # Run the command
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({'error': 'Failed to generate video', 'details': result.stderr}), 500
        
        # Assuming the output is stored in the result directory
        output_path = os.path.join('results', 'result_voice.mp4')
        
        if not os.path.exists(output_path):
            return jsonify({'error': 'Output video not found'}), 500
        
        return jsonify({'message': 'Lip-sync video generated successfully', 'output_path': output_path})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_all_videos(directory='results'):
    files = os.listdir(directory)
    video_files = [f for f in files if f.endswith('.mp4')]
    return video_files

@app.route('/get_videos', methods=['GET'])
def get_videos():
    try:
        videos = get_all_videos()
        return jsonify({'videos': videos})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results/<filename>')
def serve_video(filename):
    return send_from_directory('results', filename) 


# Folders to save uploaded files
BASE_UPLOAD_FOLDER = 'Upload'
IMAGE_UPLOAD_FOLDER = os.path.join(BASE_UPLOAD_FOLDER, 'Image')
AUDIO_UPLOAD_FOLDER = os.path.join(BASE_UPLOAD_FOLDER, 'Audio')
app.config['IMAGE_UPLOAD_FOLDER'] = IMAGE_UPLOAD_FOLDER
app.config['AUDIO_UPLOAD_FOLDER'] = AUDIO_UPLOAD_FOLDER

# Ensure the upload folders exist
os.makedirs(IMAGE_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files or 'audio' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    image = request.files['image']
    audio = request.files['audio']

    if image.filename == '' or audio.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the image to the specified folder
    image_path = os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], image.filename)
    image.save(image_path)

    # Save the audio to the specified folder
    audio_path = os.path.join(app.config['AUDIO_UPLOAD_FOLDER'], audio.filename)
    audio.save(audio_path)

    return jsonify({
        'message': 'Files successfully uploaded',
        'image_path': image_path,
        'audio_path': audio_path
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
