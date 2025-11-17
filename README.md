

## ℹ️ Sobre a Classificação e Geração de Resposta

Inicialmente, a classificação dos e-mails utilizava o modelo zero-shot MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-3 da Hugging Face. No entanto, devido a problemas na implementação, optou-se por criar um arquivo CSV com exemplos reais de e-mails produtivos e improdutivos e treinar um modelo próprio (scikit-learn + TF-IDF + LogisticRegression) usando o Google Colab.

O pipeline treinado foi salvo em `app/models/modelo_classificador_email.pkl` e é carregado localmente para a classificação dos e-mails.

**Importante:** A geração automática de respostas para os e-mails classificados ainda utiliza um modelo da Hugging Face (Gemma-2-2B-IT) via API, garantindo respostas contextuais e naturais.



# Email Classifier AI

Uma aplicação web inteligente que utiliza IA para classificar emails automaticamente e sugerir respostas adequadas.

## 🎯 Objetivo

Automatizar a leitura e classificação de emails empresariais, categorizando-os como **Produtivo** ou **Improdutivo** e gerando respostas automáticas apropriadas.

## 🚀 Funcionalidades

- ✅ Upload de arquivos de email (.txt, .pdf)
- ✅ Inserção direta de texto de emails
- ✅ Classificação automática com IA
- ✅ Geração de respostas automáticas
- ✅ Interface web moderna e intuitiva
- ✅ Deploy na nuvem

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python, Flask
- **IA/NLP:** scikit-learn (pipeline salvo em .pkl), Transformers (Hugging Face, modelo google/gemma-2-2b-it para geração de resposta)
- **Serialização:** joblib
- **Frontend:** HTML5, CSS3, JavaScript
- **Deploy:** Render
- **Processamento:** PyPDF2 para PDFs

## 📦 Instalação e Execução Local

### Pré-requisitos
- Python 3.12
- pip

### Passos

1. **Clone o repositório:**
```bash
git clone https://github.com/Kaio-Ribeiro/emailclassifier-ai.git
cd emailclassifier-ai
```

2. **Crie um ambiente virtual:**
```bash
python -m venv venv
```

3. **Ative o ambiente virtual:**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```


4. **Instale as dependências:**
```bash
pip install -r requirements.txt
```


5. **Configure as variáveis de ambiente:**

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
HF_TOKEN=your-huggingface-token-here

Para que a geração automática de respostas funcione, é necessário possuir uma conta gratuita no [Hugging Face](https://huggingface.co/). Após criar sua conta, gere um token de acesso (API Key) em: [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) e preencha o campo `HF_TOKEN` acima.
```

**Descrição das variáveis:**
- `FLASK_ENV`: Ambiente do Flask (`development` ou `production`).
- `SECRET_KEY`: Chave secreta para a aplicação Flask.
- `UPLOAD_FOLDER`: Pasta para uploads temporários (padrão: `uploads`).
- `MAX_CONTENT_LENGTH`: Tamanho máximo permitido para uploads (em bytes, padrão: 16777216 = 16MB).
- `HF_TOKEN`: Token de acesso à API do Hugging Face.


6. **Execute a aplicação:**
```bash
python app.py
```

Ou, para rodar via Docker:
```bash
docker build -t emailclassifier-ai .
docker run -p 5000:5000 --env-file .env emailclassifier-ai
```

A aplicação estará disponível em: `http://localhost:5000`

## 🔧 Estrutura do Projeto

```
emailclassifier-ai/
├── app/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   ├── __init__.py
│   ├── ai_classifier.py
│   ├── main.py
│   ├── utils.py
│   └── models/
│       └── modelo_classificador_email.pkl
├── data/
│   └── email_dataset.csv
├── notebooks/
│   └── email-classfier.ipynb
├── uploads/
├── requirements.txt
├── Dockerfile
├── .env
├── .gitignore
└── README.md
```


## 🧠 Como Funciona a IA

1. **Pré-processamento:** O texto é limpo e normalizado (remoção de espaços, truncamento, etc.)
2. **Classificação:** Utilizamos um pipeline scikit-learn (TF-IDF + LogisticRegression) treinado e salvo em `.pkl` para categorizar emails como produtivo ou improdutivo.
3. **Geração de Resposta:** Utilizamos o modelo "google/gemma-2-2b-it" da Hugging Face para gerar respostas contextuais baseadas na classificação. Em caso de erro, uma resposta padrão é utilizada como fallback.


### Categorias de Classificação

- **Produtivo:** Emails que requerem ação específica (suporte, atualizações, dúvidas)
- **Improdutivo:** Emails informativos (felicitações, agradecimentos)


## 🌐 Deploy na Nuvem

A aplicação está hospedada em: [https://emailclassifier-ai.onrender.com](https://emailclassifier-ai.onrender.com)

## 🎥 Demonstração

[Link do vídeo demonstrativo será adicionado]


## 📚 Reprodutibilidade e Treinamento

Para facilitar a reprodutibilidade e evolução do projeto, incluímos:

- Um arquivo de exemplo de dados de treinamento: `data/email_dataset.csv`
- Um notebook (markdown) com o passo a passo do treinamento do modelo: `notebooks/email-classfier.ipynb`

Você pode usar e adaptar esses arquivos para re-treinar o modelo localmente, criar novos conjuntos de dados ou auditar o processo de classificação.


## 📝 Observações

- O pipeline scikit-learn é carregado automaticamente do arquivo `.pkl`.
- É fundamental manter a mesma versão do scikit-learn do treinamento (1.6.1) para evitar incompatibilidades.
- O joblib é utilizado para serialização/deserialização do pipeline.

## 📝 Exemplos de Uso

### Email Produtivo
```
Assunto: Solicitação de Suporte - Sistema Fora do Ar
Prezada equipe,
Estou enfrentando problemas para acessar o sistema desde esta manhã...
```
**Classificação:** Produtivo
**Resposta Sugerida:** "Recebemos sua solicitação de suporte e nossa equipe técnica..."

### Email Improdutivo
```
Assunto: Parabéns pela promoção!
Olá João,
Queria parabenizá-lo pela sua promoção...
```
**Classificação:** Improdutivo
**Resposta Sugerida:** "Muito obrigado pela mensagem! Fico feliz em receber..."

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**Kaio Ribeiro**
- GitHub: [@Kaio-Ribeiro](https://github.com/Kaio-Ribeiro)

---

**Desenvolvido como parte do desafio técnico de classificação automática de emails com IA.**