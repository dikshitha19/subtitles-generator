from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
from pathlib import Path
from subtitles_generator.core import Model
from subtitles_generator.utils import create_srt, extract_audio
import logging
import warnings
import sys
from hydra import compose, initialize
from pymongo import MongoClient
import bcrypt

client = MongoClient('mongodb://localhost:27017/')
db = client['userDB']

collection = db['users']

app = Flask(__name__)
app.secret_key = 'super_secret_key'  

# Directories
UPLOAD_FOLDER = './uploads'
OUTPUT_FOLDER = './output'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Logger setup
logger = logging.getLogger(__name__)
logging_handler = logging.StreamHandler(sys.stdout)
logging_handler.setLevel(logging.INFO)
logger.addHandler(logging_handler)

warnings.filterwarnings("ignore")

# Dummy user store (Replace this with DB later)
# users = {'admin': 'admin123'}

def process_video_for_subtitles(input_file: Path, output_file: Path, lang: str, model_size: str, cfg):
    logger.info("Starting the subtitle generation process...")

    if input_file.suffix in cfg.supported_media_formats.video:
        logger.info("Extracting audio ...")
        input_file = extract_audio(input_file)
        logger.info(f"Audio extracted: {input_file}")

    model = Model(cfg.model_names[model_size], lang)
    logger.info(f"Using model: {cfg.model_names[model_size]}, Language: {lang}")

    logger.info("Generating subtitles ...")
    predicted_texts = model.transcribe(
        audio_path=input_file,
        sampling_rate=cfg.processing.sampling_rate,
        chunk_size=cfg.processing.chunk_size
    )

    logger.info("Subtitles generated, now writing them to the output file.")
    create_srt(output_file, predicted_texts, cfg.processing.chunk_size)
    logger.info(f"Subtitles saved to: {output_file}")
    return output_file

@app.route('/')
def landing():
    username = session.get('username')
    return render_template('landing.html', username=username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        user = collection.find_one({"username": username})
        if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid Credentials')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        if collection.find_one({"username": username}):
            return render_template('signup.html', error='Username already exists')
        if collection.find_one({"email": email}):
            return render_template('signup.html', error='Email already registered')

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
        collection.insert_one({
            "username": username,
            "email": email,
            "password": hashed_password
        })
        session['username'] = username
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('landing'))

@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('login'))

    logger.info("Upload function triggered")
    if 'file' not in request.files:
        logger.error("No file part")
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        logger.error("No selected file")
        return "No selected file", 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    logger.info(f"File saved at: {filepath}")

    with initialize(version_base=None, config_path="src\\subtitles_generator\\conf"):
        logger.info("Initializing Hydra configuration...")
        cfg = compose(config_name="config")
        logger.info("Hydra configuration loaded.")

    lang = request.form.get('lang', 'english')
    model_size = request.form.get('model_size', 'medium')
    output_filename = Path(file.filename).stem + '.srt'
    output_file = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

    try:
        logger.info("Processing video for subtitles...")
        processed_file = process_video_for_subtitles(Path(filepath), Path(output_file), lang, model_size, cfg)
        logger.info(f"Subtitles generated: {processed_file}")
        return send_from_directory(app.config['OUTPUT_FOLDER'], output_filename, as_attachment=True)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    logger.info("Starting Flask app...")
    app.run(debug=True)