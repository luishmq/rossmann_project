import requests
import pandas as pd
import json
import os

from flask import Flask, request, Response

#constants
TOKEN = '5832194842:AAFB4ju1RhkaXjqnOad3l13ZUiKqGiSwffE'


# Info Bot
# https://api.telegram.org/bot5832194842:AAFB4ju1RhkaXjqnOad3l13ZUiKqGiSwffE/getMe

# Get Updates
# https://api.telegram.org/bot5832194842:AAFB4ju1RhkaXjqnOad3l13ZUiKqGiSwffE/getUpdates

# Send Message
# https://api.telegram.org/bot5832194842:AAFB4ju1RhkaXjqnOad3l13ZUiKqGiSwffE/sendMessage chat_id=5619238150&text=Hi Luis!

# Webhook Render
# https://api.telegram.org/bot5832194842:AAFB4ju1RhkaXjqnOad3l13ZUiKqGiSwffE/setWebhook?url=https://test-api-telegram-rossmann.onrender.com


def send_message(chat_id, text):

  url = 'https://api.telegram.org/bot{}/'.format(TOKEN)
  url = url + 'sendMessage?chat_id={}'.format(chat_id)

  r = requests.post(url, json={'text': text})
  print('Status Code: {}'.format(r.status_code))

  return None


def load_dataset( store_id ):
    # loading test dataset
    df10 = pd.read_csv( 'test.csv' )
    df_store_raw = pd.read_csv( 'store.csv' )

    # merge test dataset + store
    df_test = pd.merge( df10, df_store_raw, how='left', on='Store' )

    # choose store for prediction
    df_test = df_test[df_test['Store'] == store_id]

    if not df_test.empty:

       # Limpeza e filtragem dos dados
       df_test = df_test[df_test['Open'] != 0]
       df_test = df_test[~df_test['Open'].isnull()]
       df_test = df_test.drop('Id', axis=1)

       # Convertendo para .json
       data = json.dumps(df_test.to_dict(orient='records'))

    else: 
       data = 'error'
	
    return data

def predict( data ):
    # API Call
    url = 'https://test-web-api.onrender.com/rossmann/predict'
    header = {'Content-type': 'application/json' } 
    data = data

    r = requests.post( url, data=data, headers=header )
    print( 'Status Code {}'.format( r.status_code ) )

    d1 = pd.DataFrame( r.json(), columns=r.json()[0].keys() )

    return d1

def parse_message(message):
    chat_id = message['message']['chat']['id']
    store_id = message['message']['text']

    store_id = store_id.replace('/', '')

    try:
      store_id = int(store_id)
    except ValueError:
      store_id = 'error'

    return chat_id, store_id

# API Initialize
app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':

        message = request.get_json()
        chat_id, store_id = parse_message(message)

        if store_id != 'error':
            # Carregando os dados
            data = load_dataset(store_id)

            if data != 'error':
                # Fazendo a previsão
                d1 = predict(data)

                # Somando os resultados por loja
                d2 = d1[['store', 'prediction']].groupby('store').sum().reset_index()

                # Enviando a resposta
                msg = 'A loja número {} vai vender €{:,.2f} nas próximas 6 semanas.'.format(d2['store'].values[0], d2['prediction'].values[0])

                send_message(chat_id, msg)
                return Response('OK', status=200)
            else:
                send_message(chat_id, 'Previsão de Vendas indisponível para essa loja.')
                return Response('OK', status=200)

        else:
            send_message(chat_id, 'Número da Loja Inválido.')
            return Response('OK', status=200)

    else:
        return '<h1> Bot no Telegram para Previsão de Vendas da Rossmann </h1>'

if __name__ == '__main__':
  port = os.environ.get('PORT', 5000)
  app.run(host='0.0.0.0', port=port)