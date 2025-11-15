from flask import Flask, render_template, request, jsonify
import os
from app.utils import extract_text_from_file, validate_file_size, clean_text

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

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

def get_mock_response(classification):
    """Generate mock response based on classification"""
    responses = {
        'produtivo': 'Recebemos sua solicitação e nossa equipe está analisando. Retornaremos em breve com uma solução.',
        'improdutivo': 'Muito obrigado pela mensagem! Ficamos felizes em receber seu contato.'
    }
    return responses.get(classification, 'Obrigado por entrar em contato conosco.')

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
    """Classify email text"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = clean_text(data['text'])
        
        if len(text) < 10:
            return jsonify({'error': 'Text too short, minimum 10 characters'}), 400
        
        # TODO: Implement actual classification
        # For now, return mock response based on keywords
        classification = 'produtivo' if any(word in text.lower() for word in 
                                          ['suporte', 'problema', 'erro', 'ajuda', 'solicitação', 
                                           'dúvida', 'urgente', 'prazo', 'status', 'reunião']) else 'improdutivo'
        
        result = {
            'classification': classification,
            'confidence': 0.95,
            'suggested_response': get_mock_response(classification)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/classify/file', methods=['POST'])
def classify_file():
    """Classify uploaded file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Use .txt or .pdf'}), 400
        
        # Validate file size
        if not validate_file_size(file):
            return jsonify({'error': 'File too large. Maximum size: 16MB'}), 400
        
        # Extract text from file
        try:
            text = extract_text_from_file(file, file.filename)
            text = clean_text(text)
            
            if len(text) < 10:
                return jsonify({'error': 'File content too short, minimum 10 characters'}), 400
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
        
        # TODO: Implement actual classification
        # For now, return mock response based on text content
        classification = 'produtivo' if any(word in text.lower() for word in 
                                          ['suporte', 'problema', 'erro', 'ajuda', 'solicitação']) else 'improdutivo'
        
        result = {
            'classification': classification,
            'confidence': 0.88,
            'suggested_response': get_mock_response(classification)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)