FROM python:latest

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       postgresql-client \
       build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências do Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia todo o projeto
COPY . .

# Copia o script de entrypoint e dá permissão de execução
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Define o entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]