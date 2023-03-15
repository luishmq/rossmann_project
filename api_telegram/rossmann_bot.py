import requests
import pandas as pd
import json

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
# https://api.telegram.org/bot5967388185:AAHEpPGCYIw_SyQvcR5ZZqHAx8PC2ZGDAIU/setWebhook?url=https://c39d455a18fe19.lhr.life


def send_message(chat_id, text):

  url = 'https://api.telegram.org/bot{}/'.format(token)
  url = url + 'sendMessage?chat_id={}'.format(chat_id)

  r = requests.post(url, json={'text': text})
  print('Status Code: {}'.format(r.status_code))

  return None


def load_dataset( store_id ):
    # loading test dataset
    df10 = pd.read_csv( '/Users/luishmq/Documents/repos/rossmann_project/datasets/test.csv' )
    df_store_raw = pd.read_csv( '/Users/luishmq/Documents/repos/rossmann_project/datasets store.csv' )

    # merge test dataset + store
    df_test = pd.merge( df10, df_store_raw, how='left', on='Store' )

    # choose store for prediction
    df_test = df_test[df_test['Store'] == 'store_id']

    if not df_test.empty:

       # Limpeza e filtragem dos dados
       df_test = df_test[df_test['Store'] == store_number]
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
    store_number = message['message']['text']

    store_number = store_number.replace('/', '')

    try:
      store_number = int(store_number)
    except ValueError:
      store_number = 'error'

    return chat_id, store_number

# API Initialize
app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def index():
  if request.method == 'POST':
    
    message = request.get_json()
    chat_id, store_number = parse_message(message)

    if store_number != 'error':
      # Carregando os dados
      data = load_dataset(store_number)

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
  app.run(host='0.0.0.0', port=5000)