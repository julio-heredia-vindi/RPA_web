FROM python:3.9-slim

# Instala dependências do sistema necessárias para o Chrome
RUN apt-get update && apt-get install -y wget unzip gnupg2 \
    && wget -q -O google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome.deb || apt-get -f install -y \
    && rm google-chrome.deb

# Instala o ChromeDriver
RUN CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -q "https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip" && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    rm chromedriver_linux64.zip

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Render passa a porta via variável de ambiente, por isso configure dessa forma:
EXPOSE $PORT

CMD ["python", "app.py"]
