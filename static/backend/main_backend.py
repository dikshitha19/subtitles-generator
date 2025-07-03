import os
from pathlib import Path
from flask import Flask, render_template, request, send_from_directory, jsonify, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging
import json
import time
from subtitles_generator.core import Model
from subtitles_generator.utils import create_srt, extract_audio
from hydra import compose, initialize

app = Flask(__name__, template_folder='templates')
CORS(app)

# Configuration
app.config.update(
    UPLOAD_FOLDER='uploads',
    OUTPUT_FOLDER='output',
    MAX_CONTENT_LENGTH=100 * 1024 * 1024,
    ALLOWED_EXTENSIONS={'mp4', 'avi', 'mov', 'mp3', 'wav', 'mkv'},
    SECRET_KEY='your-secret-key-here'
)

Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path(app.config['OUTPUT_FOLDER']).mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    def generate():
        try:
            if 'file' not in request.files:
                yield json.dumps({"error": "No file part"}) + "\n"
                return

            file = request.files['file']
            if file.filename == '':
                yield json.dumps({"error": "No selected file"}) + "\n"
                return

            if not allowed_file(file.filename):
                yield json.dumps({"error": "Unsupported file format"}) + "\n"
                return

            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            lang = request.form.get('lang', 'english')
            model_size = request.form.get('model_size', 'medium')
            output_filename = Path(filename).stem + '.srt'
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

            # Initialize progress
            yield json.dumps({"progress": 10, "message": "File uploaded"}) + "\n"
            time.sleep(1)

            with initialize(version_base=None, config_path="src/subtitles_generator/conf"):
                cfg = compose(config_name="config")

                if Path(filepath).suffix in cfg.supported_media_formats.video:
                    yield json.dumps({"progress": 30, "message": "Extracting audio..."}) + "\n"
                    filepath = extract_audio(Path(filepath))
                    time.sleep(1)

                yield json.dumps({"progress": 50, "message": "Initializing model..."}) + "\n"
                model = Model(cfg.model_names[model_size], lang)
                time.sleep(1)

                yield json.dumps({"progress": 70, "message": "Transcribing audio..."}) + "\n"
                predicted_texts = model.transcribe(
                    audio_path=filepath,
                    sampling_rate=cfg.processing.sampling_rate,
                    chunk_size=cfg.processing.chunk_size
                )
                time.sleep(2)

                yield json.dumps({"progress": 90, "message": "Generating subtitles..."}) + "\n"
                create_srt(output_path, predicted_texts, cfg.processing.chunk_size)
                time.sleep(1)

                yield json.dumps({
                    "progress": 100,
                    "message": "Complete!",
                    "filename": output_filename
                }) + "\n"

        except Exception as e:
            logger.error(f"Error: {str(e)}")
            yield json.dumps({
                "error": str(e),
                "message": "Processing failed"
            }) + "\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(
        app.config['OUTPUT_FOLDER'],
        filename,
        as_attachment=True,
        mimetype='application/x-subrip'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)