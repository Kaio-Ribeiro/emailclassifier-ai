"""
AI-powered email classifier using Hugging Face transformers
"""
import torch
from transformers import pipeline
from deep_translator import GoogleTranslator
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
        self.model_name = "MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33"
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.translator = GoogleTranslator(source='auto', target='en')
        self.zero_shot_classifier = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize the classification models"""
        try:
            logger.info(f"Loading zero-shot model on device: {self.device}")
            self.zero_shot_classifier = pipeline(
                "zero-shot-classification",
                model=self.model_name,
                device=0 if self.device == "cuda" else -1
            )
            logger.info("Zero-shot model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading zero-shot model: {e}")
            self.zero_shot_classifier = None
    
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

            # Traduzir para inglês antes da classificação
            try:
                translated_text = self.translator.translate(cleaned_text)
            except Exception as e:
                logger.warning(f"Erro ao traduzir texto, usando original: {e}")
                translated_text = cleaned_text


            # Classificação zero-shot
            if self.zero_shot_classifier:
                # Labels detalhadas com exemplos e palavras-chave
                candidate_labels = [
                    (
                        "productive: Emails that require action, response, or have direct operational/financial impact. "
                        "Examples: 'I need an update on my loan request', 'The system is showing an error', "
                        "'When will my card be unlocked?', 'I want to dispute a charge on my bill'. "
                        "Keywords: status, update, request, urgent, problem, error, payment, invoice, account, "
                        "transaction, support, how, when, protocol, case, deadline, unlock, resolve, fix, question, "
                        "help, information, document, contract, change, urgent information, operational change, financial'."
                    ),
                    (
                        "unproductive: Emails with no immediate action required, social/courtesy nature, generic thanks, "
                        "greetings, or irrelevant to business. Examples: 'Merry Christmas to you and your family', "
                        "'Thank you for your great service', 'Just letting you know I received the previous email', "
                        "'Promotion: 50% off product X'. Keywords: happy, congratulations, thank you, merry christmas, "
                        "happy new year, best wishes, just informing, for your information, fyi, no action needed, holiday, "
                        "birthday, automatic confirmation, spam, irrelevant, outside scope, generic question, social, "
                        "courtesy, acknowledgment, only for your knowledge'."
                    )
                ]
                hypothesis_template = "This email is about: {}"
                zero_shot_result = self.zero_shot_classifier(
                    translated_text,
                    candidate_labels,
                    hypothesis_template=hypothesis_template
                )
                # Score para cada label
                scores = dict(zip(zero_shot_result['labels'], zero_shot_result['scores']))
                prod_score = scores.get(candidate_labels[0], 0)
                unprod_score = scores.get(candidate_labels[1], 0)
                # Thresholds
                if prod_score > 0.70 and prod_score > unprod_score:
                    classification = 'produtivo'
                    confidence = prod_score
                    reasoning = f"Zero-shot: score produtivo {prod_score:.2f}"
                elif unprod_score > 0.70:
                    classification = 'improdutivo'
                    confidence = unprod_score
                    reasoning = f"Zero-shot: score improdutivo {unprod_score:.2f}"
                elif 0.50 < max(prod_score, unprod_score) <= 0.70:
                    # Ambíguo: fallback para keywords
                    keyword_result = self._classify_with_keywords(cleaned_text)
                    classification = keyword_result['classification']
                    confidence = max(prod_score, unprod_score)
                    reasoning = f"Ambíguo (zero-shot), fallback keywords: {keyword_result['reasoning']}"
                else:
                    classification = 'produtivo'
                    confidence = max(prod_score, unprod_score)
                    reasoning = "Score baixo, default produtivo"
                return {
                    'classification': classification,
                    'confidence': confidence,
                    'reasoning': reasoning,
                    'translated_text': translated_text,
                    'zero_shot_scores': scores
                }
            else:
                # Fallback para keywords
                result = self._classify_with_keywords(cleaned_text)
                result['translated_text'] = translated_text
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