#!/bin/bash
set -e

# Atualiza pacotes e instala dependências necessárias
apt-get update
apt-get install -y wget unzip

# Instala o Google Chrome
wget -q -O google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i google-chrome.deb || apt-get -f install -y
rm google-chrome.deb

# Instala o ChromeDriver
CHROME_DRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`
wget -q "https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
mv chromedriver /usr/bin/chromedriver
chmod +x /usr/bin/chromedriver
rm chromedriver_linux64.zip
