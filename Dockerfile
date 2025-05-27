FROM python:3.10-slim

WORKDIR /app

# Copiar apenas o requirements.txt do diretório app/ para aproveitar o cache de camadas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código da aplicação do diretório app/
COPY app/ .

# Criar um usuário não-root para rodar a aplicação
RUN useradd -m myuser
USER myuser

# Expor a porta que o Flask vai usar
EXPOSE 8080

# Comando para iniciar a aplicação
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]