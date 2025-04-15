from flask import Flask, render_template, request, send_file, jsonify, after_this_request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timedelta
import pandas as pd
import os, time
from io import StringIO
import zipfile

app = Flask(__name__)
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def extrair_tabela_por_data(data_str):
    data_formatada = datetime.strptime(data_str, "%Y-%m-%d").strftime("%Y%m%d")
    url = f"https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/derivativos/ajustes-do-pregao/?Data={data_formatada}&download=1"

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)

    try:
        driver.get(url)
        time.sleep(5)

        iframe = driver.find_element(By.TAG_NAME, "iframe")
        driver.switch_to.frame(iframe)

        table = driver.find_element(By.TAG_NAME, "table")
        html = table.get_attribute("outerHTML")

        df = pd.read_html(StringIO(html))[0]
        nome_arquivo = f"{data_formatada}.csv"
        caminho = os.path.join(DOWNLOAD_FOLDER, nome_arquivo)
        df.to_csv(caminho, index=False, encoding='utf-8-sig')
        return True, nome_arquivo
    except Exception as e:
        return False, str(e)
    finally:
        driver.quit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extrair', methods=['POST'])
def extrair():
    data_inicio = datetime.strptime(request.form['data_inicio'], "%Y-%m-%d")
    data_fim = datetime.strptime(request.form['data_fim'], "%Y-%m-%d")

    resultados = []
    data_atual = data_inicio
    while data_atual <= data_fim:
        data_str = data_atual.strftime("%Y-%m-%d")
        sucesso, msg = extrair_tabela_por_data(data_str)
        resultados.append({
            'data': data_str,
            'sucesso': sucesso,
            'mensagem': msg,
            'link_download': f'/download/{msg}' if sucesso else None
        })
        data_atual += timedelta(days=1)

    return jsonify(resultados)

@app.route('/download/<nome_arquivo>')
def download(nome_arquivo):
    caminho = os.path.join(DOWNLOAD_FOLDER, nome_arquivo)
    if os.path.exists(caminho):
        return send_file(caminho, as_attachment=True)
    else:
        return jsonify({'erro': 'Arquivo não encontrado'}), 404

@app.route('/download_zip')
def download_zip():
    zip_path = os.path.join(DOWNLOAD_FOLDER, 'arquivos.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(DOWNLOAD_FOLDER):
            for file in files:
                if file.endswith('.csv'):
                    zipf.write(os.path.join(root, file), arcname=file)

    @after_this_request
    def remove_file(response):
        try:
            os.remove(zip_path)
            # Remove arquivos CSV temporários
            for file in os.listdir(DOWNLOAD_FOLDER):
                if file.endswith('.csv'):
                    os.remove(os.path.join(DOWNLOAD_FOLDER, file))
        except Exception as e:
            app.logger.error(f"Erro ao remover arquivos: {e}")
        return response

    return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
