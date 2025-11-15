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
- **IA/NLP:** Transformers (Hugging Face), NLTK
- **Frontend:** HTML5, CSS3, JavaScript
- **Deploy:** Heroku/Render
- **Processamento:** PyPDF2 para PDFs

## 📦 Instalação e Execução Local

### Pré-requisitos
- Python 3.8+
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
Crie um arquivo `.env` na raiz do projeto:
```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

6. **Execute a aplicação:**
```bash
python app.py
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
│   ├── models.py
│   ├── routes.py
│   └── utils.py
├── uploads/
├── tests/
├── app.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## 🧠 Como Funciona a IA

1. **Pré-processamento:** O texto é limpo e normalizado usando NLTK
2. **Classificação:** Utilizamos modelos de NLP para categorizar emails
3. **Geração de Resposta:** IA gera respostas contextuais baseadas na classificação

### Categorias de Classificação

- **Produtivo:** Emails que requerem ação específica (suporte, atualizações, dúvidas)
- **Improdutivo:** Emails informativos (felicitações, agradecimentos)

## 🌐 Deploy na Nuvem

A aplicação está hospedada em: [Link será adicionado após deploy]

## 🎥 Demonstração

[Link do vídeo demonstrativo será adicionado]

## 🧪 Testes

Execute os testes com:
```bash
python -m pytest tests/
```

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