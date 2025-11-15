"""
AI-powered email classifier using Hugging Face transformers
"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import logging
import os
from typing import Dict, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailClassifier:
    """
    Email classifier using pre-trained Portuguese language models
    """
    
    def __init__(self):
        self.model_name = "neuralmind/bert-base-portuguese-cased"
        self.sentiment_model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize the classification models"""
        try:
            logger.info(f"Loading models on device: {self.device}")
            
            # Load sentiment analysis pipeline for Portuguese
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=0 if self.device == "cuda" else -1
            )
            
            logger.info("Models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            # Fallback to simpler approach
            self.sentiment_model = None
    
    def classify_email(self, text: str) -> Dict[str, any]:
        """
        Classify email as productive or unproductive
        
        Args:
            text: Email content
            
        Returns:
            Dict with classification, confidence, and reasoning
        """
        try:
            # Clean and prepare text
            cleaned_text = self._preprocess_text(text)
            
            if len(cleaned_text.strip()) < 10:
                return {
                    'classification': 'improdutivo',
                    'confidence': 0.5,
                    'reasoning': 'Texto muito curto para análise'
                }
            
            # Use sentiment analysis if available
            if self.sentiment_model:
                result = self._classify_with_sentiment(cleaned_text)
            else:
                result = self._classify_with_keywords(cleaned_text)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in classification: {e}")
            return self._fallback_classification(text)
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        cleaned = ' '.join(text.split())
        
        # Limit text length for processing
        max_length = 512
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
        
        return cleaned
    
    def _classify_with_sentiment(self, text: str) -> Dict[str, any]:
        """Classify using sentiment analysis model"""
        try:
            # Get sentiment
            sentiment_result = self.sentiment_model(text)[0]
            sentiment = sentiment_result['label']
            confidence = sentiment_result['score']
            
            # Check for productive keywords
            productive_keywords = [
                'suporte', 'problema', 'erro', 'bug', 'falha', 'ajuda', 'dúvida',
                'solicitação', 'pedido', 'urgente', 'prazo', 'atualização', 'status',
                'pendente', 'bloqueado', 'reunião', 'projeto', 'revisão', 'análise',
                'aprovação', 'confirmar', 'verificar', 'resolver', 'corrigir'
            ]
            
            unproductive_keywords = [
                'parabéns', 'felicitações', 'obrigado', 'agradecimento', 'natal',
                'aniversário', 'feriado', 'férias', 'convite', 'social'
            ]
            
            text_lower = text.lower()
            productive_count = sum(1 for keyword in productive_keywords if keyword in text_lower)
            unproductive_count = sum(1 for keyword in unproductive_keywords if keyword in text_lower)
            
            # Determine classification
            if productive_count > unproductive_count and productive_count > 0:
                classification = 'produtivo'
                final_confidence = min(0.95, confidence * 0.8 + (productive_count * 0.1))
                reasoning = f"Contém {productive_count} palavras-chave produtivas"
            elif unproductive_count > 0:
                classification = 'improdutivo'
                final_confidence = min(0.90, confidence * 0.7 + (unproductive_count * 0.1))
                reasoning = f"Contém {unproductive_count} palavras-chave improdutivas"
            elif sentiment == 'NEGATIVE':
                classification = 'produtivo'
                final_confidence = confidence * 0.8
                reasoning = "Sentimento negativo indica possível problema"
            else:
                classification = 'improdutivo'
                final_confidence = confidence * 0.6
                reasoning = "Sem indicadores claros de produtividade"
            
            return {
                'classification': classification,
                'confidence': final_confidence,
                'reasoning': reasoning,
                'sentiment': sentiment,
                'sentiment_confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment classification: {e}")
            return self._classify_with_keywords(text)
    
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
        Generate appropriate response based on classification
        
        Args:
            classification: 'produtivo' or 'improdutivo'
            text: Original email text for context
            confidence: Classification confidence
            
        Returns:
            Generated response string
        """
        try:
            if classification == 'produtivo':
                return self._generate_productive_response(text, confidence)
            else:
                return self._generate_unproductive_response(text, confidence)
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Obrigado pelo seu contato. Retornaremos em breve."
    
    def _generate_productive_response(self, text: str, confidence: float) -> str:
        """Generate response for productive emails"""
        text_lower = text.lower() if text else ""
        
        # Specific responses based on content
        if any(word in text_lower for word in ['urgente', 'crítico', 'emergência']):
            return ("Recebemos sua solicitação urgente e nossa equipe técnica está "
                   "priorizando sua demanda. Você receberá uma atualização em no máximo 2 horas.")
        
        elif any(word in text_lower for word in ['erro', 'problema', 'falha', 'bug']):
            return ("Obrigado por reportar este problema. Nossa equipe técnica está "
                   "investigando e trabalharemos para resolver o mais rápido possível. "
                   "Você receberá atualizações sobre o progresso da correção.")
        
        elif any(word in text_lower for word in ['suporte', 'ajuda', 'dúvida']):
            return ("Recebemos sua solicitação de suporte. Nossa equipe especializada "
                   "analisará sua questão e retornará com uma solução detalhada em até 24 horas.")
        
        elif any(word in text_lower for word in ['status', 'atualização', 'andamento']):
            return ("Obrigado por solicitar uma atualização. Verificaremos o status atual "
                   "de sua demanda e enviaremos um relatório detalhado em breve.")
        
        elif any(word in text_lower for word in ['reunião', 'meeting', 'encontro']):
            return ("Recebemos sua solicitação de reunião. Verificaremos a disponibilidade "
                   "da equipe e retornaremos com propostas de horários adequados.")
        
        else:
            # Generic productive response
            responses = [
                ("Recebemos sua mensagem e nossa equipe está analisando. "
                 "Retornaremos com uma resposta detalhada em breve."),
                ("Obrigado por entrar em contato. Sua demanda foi direcionada para "
                 "o setor responsável e você receberá um retorno em até 24 horas."),
                ("Confirmamos o recebimento de sua solicitação. Nossa equipe está "
                 "trabalhando na análise e entrará em contato assim que possível.")
            ]
            
            # Choose response based on confidence
            if confidence > 0.8:
                return responses[0]
            elif confidence > 0.6:
                return responses[1]
            else:
                return responses[2]
    
    def _generate_unproductive_response(self, text: str, confidence: float) -> str:
        """Generate response for unproductive emails"""
        text_lower = text.lower() if text else ""
        
        # Specific responses
        if any(word in text_lower for word in ['parabéns', 'felicitações']):
            return ("Muito obrigado pelas felicitações! Ficamos muito felizes "
                   "em receber sua mensagem e agradecemos o reconhecimento.")
        
        elif any(word in text_lower for word in ['obrigado', 'agradecimento']):
            return ("Ficamos muito gratos pelo seu agradecimento! É sempre um prazer "
                   "poder ajudar e contribuir para o seu sucesso.")
        
        elif any(word in text_lower for word in ['natal', 'ano novo', 'feriado']):
            return ("Muito obrigado pelas felicitações! Desejamos a você e sua família "
                   "momentos especiais e muita alegria. Feliz feriado!")
        
        elif any(word in text_lower for word in ['aniversário', 'nascimento']):
            return ("Obrigado pelas felicitações de aniversário! Ficamos muito felizes "
                   "em receber sua mensagem carinhosa.")
        
        else:
            # Generic unproductive responses
            responses = [
                ("Muito obrigado pela mensagem! Ficamos felizes em receber seu contato "
                 "e agradecemos por pensar em nós."),
                ("Agradecemos sua mensagem. É sempre um prazer ouvir de você! "
                 "Tenha um excelente dia."),
                ("Obrigado pelo contato! Sua mensagem é muito importante para nós "
                 "e ficamos gratos pela atenção.")
            ]
            
            # Choose response based on confidence
            if confidence > 0.8:
                return responses[0]
            elif confidence > 0.6:
                return responses[1]
            else:
                return responses[2]


# Global classifier instance
classifier = None

def get_classifier() -> EmailClassifier:
    """Get or create classifier instance"""
    global classifier
    if classifier is None:
        classifier = EmailClassifier()
    return classifier