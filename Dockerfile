# Use uma imagem oficial do Python 3.11 slim
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . /app

# Instala dependências do sistema (para torch, transformers, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential git && \
    rm -rf /var/lib/apt/lists/*

# Instala dependências Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expõe a porta padrão do Flask
EXPOSE 5000

# Variáveis de ambiente para produção
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Comando para rodar com gunicorn (ajuste o nome do app se necessário)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

# Para rodar com Flask (desenvolvimento), troque o CMD por:
# CMD ["flask", "run", "--host=0.0.0.0"]
