from flask import Flask, request
import json
import os

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    return 'Hello, World!', 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json



    # Nome temporário para o arquivo
    temp_filename = 'temp.json'

    # Salva os dados em um arquivo JSON temporário
    with open(temp_filename, 'w') as f:
        json.dump(data, f, indent=4)

    # Ler o arquivo temporário para obter o "accountNumber"
    with open(temp_filename, 'r') as f:
        content = json.load(f)
        account_number = content.get('response', {}).get('accountNumber', 'unknown')  # Pega o accountNumber ou 'unknown' se não existir

    # Definir o nome do novo arquivo com base no accountNumber
    new_filename = f'{account_number}.json'

    # Renomear o arquivo temporário com o accountNumber
    os.rename(temp_filename, new_filename)

    return 'OK', 200

if __name__ == '__main__':
    app.run(port=5000)