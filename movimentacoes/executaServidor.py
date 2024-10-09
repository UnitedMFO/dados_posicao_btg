from flask import Flask, request
import os
import requests
from zipfile import ZipFile
from threading import Event

app = Flask(__name__)

def run_server():
    app.run(port=5000)

# Criando um evento de threading para sinalizar quando o webhook terminar
webhook_completed_event = Event()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    print("Encerrando o servidor...")
    os._exit(0)  # Encerra o processo do Python

@app.route('/hello', methods=['GET'])
def hello():
    return 'Hello, world!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    account_number = data.get('response', {}).get('accountNumber', 'unknown')
    file_url = data.get('response', {}).get('url')

    if file_url:
        zip_filename = f'{account_number}.zip'

        response = requests.get(file_url)
        if response.status_code == 200:
            with open(zip_filename, 'wb') as zip_file:
                zip_file.write(response.content)

            with ZipFile(zip_filename, 'r') as zip_ref:
                zip_ref.extractall()

            extracted_files = zip_ref.namelist()
            if extracted_files:
                original_name = extracted_files[0]
                new_name = f'{account_number}{os.path.splitext(original_name)[1]}'
                os.rename(original_name, new_name)

            os.remove(zip_filename)

    webhook_completed_event.set()
    print("Requisição recebida com sucesso.")
    return 'OK', 200


