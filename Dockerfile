# Usar uma imagem base com Python
FROM python:3.9-slim

# Instalar dependências do sistema necessárias para os navegadores do Playwright
RUN apt-get update && apt-get install -y \
  libnss3 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libcups2 \
  libdrm2 \
  libxkbcommon0 \
  libgbm1 \
  libasound2 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxrandr2 \
  libpango-1.0-0 \
  libcairo2 \
  fonts-liberation \
  libfontconfig1

# Definir o diretório de trabalho no container
WORKDIR /app

# Copiar o arquivo requirements.txt e instalar as dependências do Python
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Instalar os navegadores do Playwright
RUN playwright install

# Copiar todos os arquivos da pasta atual para o diretório de trabalho no container
COPY . .

# Instalar o python-dotenv
RUN pip install python-dotenv

# Rodar o script principal ao iniciar o container
CMD ["python", "posicao/main.py"]
