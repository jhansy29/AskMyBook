from flask import Flask, request, redirect, flash, render_template, send_from_directory
import os
from datetime import datetime
import google.generativeai as genai  
from werkzeug.utils import secure_filename
from gtts import gTTS

app = Flask(__name__)
app.secret_key = "super_secret_key"
app.config['UPLOAD_FOLDER'] = 'Uploads'
app.config['TTS_FOLDER'] = 'tts'

# Create folders if they don’t exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TTS_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'wav', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_latest_file(extension):
    files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith(extension)]
    files.sort(reverse=True)
    return os.path.join(app.config['UPLOAD_FOLDER'], files[0]) if files else None

def get_files():
    return sorted([f for f in os.listdir(app.config['UPLOAD_FOLDER']) if allowed_file(f)], reverse=True)

@app.route('/', methods=['GET'])
def index():
    uploaded_files = get_files()
    tts_files = sorted(os.listdir(app.config['TTS_FOLDER']), reverse=True)
    return render_template('index.html', uploaded_files=uploaded_files, tts_files=tts_files)

@app.route('/upload', methods=['POST'])
def upload_file():
    print("POST request received at /upload")
    if 'file' not in request.files:
        print("No file part in request")
        flash('No file part')
        return redirect('/')
    file = request.files['file']
    if file.filename == '':
        print("No selected file")
        flash('No selected file')
        return redirect('/')
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        timestamp = datetime.now().strftime("%Y%m%d-%I%M%S%p")
        filename = f"{timestamp}.{ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Saving file to {file_path}")
        try:
            file.save(file_path)
            if os.path.exists(file_path):
                print("File saved successfully")
                flash(f"{ext.upper()} file uploaded successfully!")
            else:
                print("File save failed")
                flash("Failed to save file - check folder permissions")
        except Exception as e:
            print(f"Error saving file: {e}")
            flash(f"Error saving file: {e}")
    else:
        print("Unsupported file type")
        flash("Unsupported file type - only WAV and PDF allowed")
    return redirect('/')

@app.route('/process', methods=['POST'])
def process_files():
    print("POST request received at /process")
    latest_pdf = get_latest_file(".pdf")
    latest_wav = get_latest_file(".wav")
    if not latest_pdf or not latest_wav:
        print("Missing files: PDF or WAV not found")
        flash("Both PDF and WAV files are required to process.")
        return redirect('/')

    print(f"Processing PDF: {latest_pdf}")
    print(f"Processing WAV: {latest_wav}")

    # Configure Gemini API
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')  

        # Upload files
        files = [
            genai.upload_file(path=latest_wav, display_name="prompt.wav", mime_type="audio/wav"),
            genai.upload_file(path=latest_pdf, display_name="test.pdf", mime_type="application/pdf"),
        ]

        
        contents = [
            {
                "role": "user",
                "parts": [
                    {"file_data": {"file_uri": files[0].uri, "mime_type": files[0].mime_type}},
                    {"file_data": {"file_uri": files[1].uri, "mime_type": files[1].mime_type}},
                    {"text": """Please respond to the user's question from the audio file using the content of the uploaded book (PDF).\n\nYour response should include:\n1. Transcript of the audio\n2. Answer based on the book content\n"""}
                ]
            }
        ]

        generate_content_config = genai.GenerationConfig(
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            response_mime_type="text/plain",
        )

        # Stream response
        response_output = ""
        response = model.generate_content(
            contents,
            generation_config=generate_content_config,
            stream=True
        )
        for chunk in response:
            response_output += chunk.text

        # Clean up uploaded files
        for file in files:
            try:
                genai.delete_file(file.name)
            except Exception as e:
                print(f"Error deleting file {file.name}: {e}")

    except Exception as e:
        print(f"Error processing with Gemini: {e}")
        flash(f"Error processing files: {e}")
        return redirect('/')

    # Save response to tts folder
    timestamp = datetime.now().strftime("%Y%m%d-%I%M%S%p")
    result_path = os.path.join(app.config['TTS_FOLDER'], f"{timestamp}_response.txt")
    try:
        with open(result_path, 'w') as f:
            f.write(response_output)
        print(f"Response saved to {result_path}")
        flash("Gemini response generated!")
        tts = gTTS(text=response_output, lang='en')
        result_path = os.path.join(app.config['TTS_FOLDER'], f"{timestamp}_response.wav")
        tts.save(result_path)
        print(f"TTS saved to {result_path}")
            
        
    except Exception as e:
        print(f"Error saving response: {e}")
        flash(f"Error saving response: {e}")
    return redirect('/')

@app.route('/Uploads/<filename>', methods=['GET'])
def serve_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/tts/<filename>', methods=['GET'])
def serve_tts_file(filename):
    return send_from_directory(app.config['TTS_FOLDER'], filename)

@app.route('/script.js', methods=['GET'])
def scripts_js():
    return send_from_directory('', 'script.js')

if __name__ == '__main__':
    app.run(port=5002, debug=True)