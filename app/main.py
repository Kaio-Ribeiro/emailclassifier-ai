from flask import Flask, render_template, request, jsonify
import os
from .utils import extract_text_from_file, validate_file_size, clean_text
from .ai_classifier import get_classifier

app = Flask(__name__, template_folder='templates', static_folder='static')

# Basic configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Email Classifier AI is running'})

@app.route('/api/classify/text', methods=['POST'])
def classify_text():
    """Classify email text using AI"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        classifier = get_classifier()
        result = classifier.classify_email(text)
        response = classifier.generate_response(result['classification'], text, result['confidence'])
        return jsonify({
            'classification': result['classification'],
            'confidence': result['confidence'],
            'reasoning': result['reasoning'],
            'response': response
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classify/file', methods=['POST'])
def classify_file():
    """Classify uploaded email file using AI"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        if not validate_file_size(file):
            return jsonify({'error': 'File too large'}), 400
        text = extract_text_from_file(file, file.filename)
        text = clean_text(text)
        classifier = get_classifier()
        result = classifier.classify_email(text)
        response = classifier.generate_response(result['classification'], text, result['confidence'])
        return jsonify({
            'classification': result['classification'],
            'confidence': result['confidence'],
            'reasoning': result['reasoning'],
            'response': response
        })
    else:
        return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
