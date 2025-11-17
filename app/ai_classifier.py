# Adiciona geração de resposta de e-mail usando Gemma-2-2B-IT via huggingface_hub
from huggingface_hub import InferenceClient
import os
import logging
import os
from typing import Dict
import joblib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailResponseGenerator:
    def __init__(self, hf_token):
        self.hf_client = InferenceClient(token=hf_token)
        self.model_name = "google/gemma-2-2b-it"
    
    def generate_response(self, email_texto, categoria):
        """Gera resposta usando chat_completion"""
        
        if categoria == "Produtivo":
            system_msg = "Você é um assistente profissional de email de uma empresa financeira."
            user_msg = f"""Email recebido: {email_texto}\n\nGere uma resposta profissional, cordial e coerente com a mensagem recebida, em formato de e-mail, em português."""
        else:  # Improdutivo
            system_msg = "Você é um assistente profissional de email de uma empresa financeira."
            user_msg = f"""Email recebido: {email_texto}\n\nGere uma resposta breve, cordial e coerente com a mensagem recebida, em formato de e-mail, em português."""
        
        try:
            messages = [
                {"role": "user", "content": user_msg}
            ]
            
            response = self.hf_client.chat_completion(
                messages=messages,
                model=self.model_name,
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Erro ao gerar resposta com Gemma: {e}")
            # Fallback
            if categoria == "Produtivo":
                return "Prezado(a), agradecemos seu contato. Sua solicitação foi recebida e será analisada por nossa equipe. Retornaremos em até 48 horas úteis. Atenciosamente, Equipe de Atendimento."
            else:
                return "Agradecemos sua mensagem. Atenciosamente, Equipe de Atendimento."

class EmailClassifier:
    """
    Email classifier using local scikit-learn model (.pkl)
    """
    def __init__(self):
        # Caminho do pipeline completo
        modelo_path = os.path.join(os.path.dirname(__file__), 'models', 'modelo_classificador_email.pkl')
        # Carrega pipeline completo (vectorizer + classificador)
        self.pipeline = joblib.load(modelo_path)

    def classify_email(self, text: str) -> Dict[str, any]:
        """
        Classifica o e-mail como produtivo ou improdutivo usando pipeline local
        """
        try:
            cleaned_text = self._preprocess_text(text)
            if len(cleaned_text.strip()) < 10:
                return {
                    'classification': 'improdutivo',
                    'confidence': 0.5,
                    'reasoning': 'Texto muito curto para análise'
                }
            pred = self.pipeline.predict([cleaned_text])[0]
            if hasattr(self.pipeline, 'predict_proba'):
                proba = self.pipeline.predict_proba([cleaned_text])[0]
                confidence = max(proba)
            else:
                confidence = 1.0
            # Ajusta nomes para compatibilidade
            if pred in ['produtivo', 'Produtivo', 1]:
                classification = 'produtivo'
            else:
                classification = 'improdutivo'
            return {
                'classification': classification,
                'confidence': float(confidence),
                'reasoning': 'Classificação via pipeline local scikit-learn'
            }
        except Exception as e:
            logger.error(f"Erro na classificação local: {e}")
            return self._fallback_classification(text)
    
    def _preprocess_text(self, text: str) -> str:
        """Limpa e pré-processa o texto"""
        if not text:
            return ""
        cleaned = ' '.join(text.split())
        max_length = 512
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
        return cleaned
    
    
    def _classify_with_keywords(self, text: str) -> Dict[str, any]:
        """Fallback classification using keywords only"""
        productive_keywords = [
            'suporte', 'problema', 'erro', 'bug', 'falha', 'ajuda', 'dúvida',
            'solicitação', 'pedido', 'urgente', 'prazo', 'atualização', 'status',
            'pendente', 'bloqueado', 'reunião', 'projeto', 'revisão', 'análise'
        ]
        
        unproductive_keywords = [
            'parabéns', 'felicitações', 'obrigado', 'agradecimento', 'natal',
            'aniversário', 'feriado', 'férias', 'convite'
        ]
        
        text_lower = text.lower()
        productive_count = sum(1 for keyword in productive_keywords if keyword in text_lower)
        unproductive_count = sum(1 for keyword in unproductive_keywords if keyword in text_lower)
        
        if productive_count > unproductive_count:
            classification = 'produtivo'
            confidence = min(0.85, 0.6 + (productive_count * 0.1))
            reasoning = f"Contém {productive_count} palavras-chave produtivas"
        elif unproductive_count > 0:
            classification = 'improdutivo'
            confidence = min(0.80, 0.6 + (unproductive_count * 0.1))
            reasoning = f"Contém {unproductive_count} palavras-chave improdutivas"
        else:
            # Default to productive for business emails
            classification = 'produtivo'
            confidence = 0.6
            reasoning = "Classificação padrão para emails empresariais"
        
        return {
            'classification': classification,
            'confidence': confidence,
            'reasoning': reasoning
        }
    
    def _fallback_classification(self, text: str) -> Dict[str, any]:
        """Ultimate fallback classification"""
        return {
            'classification': 'produtivo',
            'confidence': 0.5,
            'reasoning': 'Classificação de fallback devido a erro'
        }
    
    def generate_response(self, classification: str, text: str = "", confidence: float = 0.0) -> str:
        """
        Gera resposta de e-mail usando Gemma-2-2B-IT via huggingface_hub
        Args:
            classification: 'produtivo' ou 'improdutivo'
            text: Texto do e-mail
            confidence: Confiança da classificação (não usado)
        Returns:
            Resposta gerada
        """
        try:
            hf_token = os.environ.get('HF_TOKEN')
            if not hf_token:
                raise ValueError('Token HF_TOKEN não encontrado nas variáveis de ambiente.')
            generator = EmailResponseGenerator(hf_token)
            categoria = 'Produtivo' if classification.lower() == 'produtivo' else 'Improdutivo'
            return generator.generate_response(text, categoria)
        except Exception as e:
            logger.error(f"Erro ao gerar resposta com Gemma: {e}")
            # Fallback
            if classification.lower() == 'produtivo':
                return "Prezado(a), agradecemos seu contato. Sua solicitação foi recebida e será analisada por nossa equipe. Retornaremos em até 48 horas úteis. Atenciosamente, Equipe de Atendimento."
            else:
                return "Agradecemos sua mensagem. Atenciosamente, Equipe de Atendimento."

# Global classifier instance
classifier = None

def get_classifier() -> EmailClassifier:
    """Get or create classifier instance"""
    global classifier
    if classifier is None:
        classifier = EmailClassifier()
    return classifier