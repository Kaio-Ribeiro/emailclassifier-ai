# Adiciona geração de resposta de e-mail usando Gemma-2-2B-IT via huggingface_hub
from huggingface_hub import InferenceClient
import os
import torch
from transformers import pipeline
from deep_translator import GoogleTranslator
import logging
import os
from typing import Dict

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
            print(f"Erro: {e}")
            # Fallback
            if categoria == "Produtivo":
                return "Prezado(a), agradecemos seu contato. Sua solicitação foi recebida e será analisada por nossa equipe. Retornaremos em até 48 horas úteis. Atenciosamente, Equipe de Atendimento."
            else:
                return "Agradecemos sua mensagem. Atenciosamente, Equipe de Atendimento."

class EmailClassifier:
    """
    Email classifier using pre-trained Portuguese language models
    """
    
    def __init__(self):
        self.model_name = "MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33"
        self.translator = GoogleTranslator(source='auto', target='en')
        self.hf_token = os.environ.get('HF_TOKEN')
        if not self.hf_token:
            raise ValueError('Token HF_TOKEN não encontrado nas variáveis de ambiente.')
        self.hf_client = InferenceClient(token=self.hf_token)
    
    # _initialize_models não é mais necessário com InferenceClient
    # def _initialize_models(self):
    #     pass
    
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


            # Zero-shot classification via Hugging Face Hub API
            candidate_labels = [
                "productive: Emails that require action, response, or have direct operational/financial impact. "
                "Examples: 'I need an update on my loan request', 'The system is showing an error', "
                "'When will my card be unlocked?', 'I want to dispute a charge on my bill'. "
                "Keywords: status, update, request, urgent, problem, error, payment, invoice, account, "
                "transaction, support, how, when, protocol, case, deadline, unlock, resolve, fix, question, "
                "help, information, document, contract, change, urgent information, operational change, financial'.",
                "unproductive: Emails with no immediate action required, social/courtesy nature, generic thanks, "
                "greetings, or irrelevant to business. Examples: 'Merry Christmas to you and your family', "
                "'Thank you for your great service', 'Just letting you know I received the previous email', "
                "'Promotion: 50% off product X'. Keywords: happy, congratulations, thank you, merry christmas, "
                "happy new year, best wishes, just informing, for your information, fyi, no action needed, holiday, "
                "birthday, automatic confirmation, spam, irrelevant, outside scope, generic question, social, "
                "courtesy, acknowledgment, only for your knowledge'."
            ]
            hypothesis_template = "This email is about: {}"
            try:
                zero_shot_result = self.hf_client.zero_shot_classification(
                    text=translated_text,
                    candidate_labels=candidate_labels,
                    hypothesis_template=hypothesis_template,
                    model=self.model_name
                )
                # Se o resultado for uma lista, pegar o primeiro elemento
                # O retorno pode ser uma lista ou dict, tratar ambos
                result = zero_shot_result
                if isinstance(zero_shot_result, list):
                    if len(zero_shot_result) > 0 and isinstance(zero_shot_result[0], dict):
                        result = zero_shot_result[0]
                    else:
                        logger.error(f"Unexpected zero_shot_result list format: {zero_shot_result}")
                        raise ValueError("Unexpected zero_shot_result format from HF Hub")
                if not (isinstance(result, dict) and 'labels' in result and 'scores' in result):
                    logger.error(f"zero_shot_result missing 'labels' or 'scores': {result}")
                    raise ValueError("zero_shot_result missing 'labels' or 'scores'")
                scores = dict(zip(result['labels'], result['scores']))
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
            except Exception as e:
                logger.error(f"Error in zero-shot classification via HF Hub: {e}")
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
            print(f"Erro ao gerar resposta com Gemma: {e}")
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