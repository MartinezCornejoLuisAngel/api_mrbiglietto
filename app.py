from flask import Flask, request, jsonify, render_template, redirect , url_for,flash
from flask_login import LoginManager,login_user, logout_user, login_required
from web3 import Web3, HTTPProvider
from solcx import compile_source
from decouple import config
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
from flask_cors import CORS
import re
import requests
from web3.middleware import construct_sign_and_send_raw_middleware
from config import d_config
from flask_wtf.csrf import CSRFProtect
from models.ModelUser import ModelUser
from models.entities.User import User


# Conexión a la red de Ethereum (en este caso, una red de prueba)
web3 = Web3(Web3.HTTPProvider(config('INFURA_NODE')))

# Dirección del contrato inteligente
contract_address = config('CONTRACT_ADDRESS')
clave_privada = config('SECRET_KEY_METAMASK')
private_key_bytes = bytes.fromhex(clave_privada)
web3.middleware_onion.add(construct_sign_and_send_raw_middleware(private_key_bytes))


# ABI del contrato inteligente
abi = [
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "id",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "name",
				"type": "string"
			}
		],
		"name": "createEvent",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "idEvent",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "clientId",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "ticketId",
				"type": "string"
			}
		],
		"name": "createTicket",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "id",
				"type": "string"
			}
		],
		"name": "ErrorCreatedEvent",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "text",
				"type": "string"
			}
		],
		"name": "ErrorCreatedTicket",
		"type": "error"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "events",
		"outputs": [
			{
				"internalType": "string",
				"name": "id",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "name",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getEvents",
		"outputs": [
			{
				"components": [
					{
						"internalType": "string",
						"name": "id",
						"type": "string"
					},
					{
						"internalType": "string",
						"name": "name",
						"type": "string"
					}
				],
				"internalType": "struct MrBiglietto.Event[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "tickets",
		"outputs": [
			{
				"internalType": "string",
				"name": "ticketId",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "clientId",
				"type": "string"
			},
			{
				"components": [
					{
						"internalType": "string",
						"name": "id",
						"type": "string"
					},
					{
						"internalType": "string",
						"name": "name",
						"type": "string"
					}
				],
				"internalType": "struct MrBiglietto.Event",
				"name": "eventFrom",
				"type": "tuple"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

contract = web3.eth.contract(address=contract_address, abi=abi)

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = config('FLASH_SECRET_KEY')
login_manager_app = LoginManager(app)
csrf = CSRFProtect()

@login_manager_app.user_loader
def load_user(username):
  return ModelUser.get_by_username(username)


@app.route('/check')
def check_conn():
    data = {}
    if  web3.is_connected():
        data['isConnected'] = True
        balance = web3.eth.get_balance(contract_address)
        data['balance'] = web3.from_wei(balance,"ether")
    else:
        data['isConnected'] = False
        return jsonify(data),402
    return jsonify(data),200

@app.route('/create_event', methods=['POST'])
def create_event():
    # Asegúrate de que el cuerpo de la solicitud contenga los parámetros necesarios para el método create_event
    if not request.json or 'id_event' not in request.json or 'name_events' not in request.json:
        return jsonify({'error': 'Missing parameters'}), 400

    id_event = request.json['id_event']
    name_events = request.json['name_events']

    # Llama al método create_event del contrato inteligente con los parámetros proporcionados
    try:
        #QUITAR LA CLAVE 
        tx_hash = contract.functions.createEvent(id_event, name_events).transact({'from': config('FROM_WALLET')})
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        return jsonify({'transaction_hash': tx_hash.hex(), 'status': receipt.status}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/events')
def get_events():
    try:
        # Llamar a la función del contrato para obtener los eventos
        events = contract.functions.getEvents().call()
        # Devolver los eventos como respuesta JSON
        return jsonify({'events': events}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/create_ticket', methods=['POST'])
def create_ticket():
    # Asegúrate de que el cuerpo de la solicitud contenga los parámetros necesarios para el método create_event
    if not request.json or 'id_event' not in request.json or 'id_client' not in request.json or 'id_ticket' not in request.json:
        return jsonify({'error': 'Missing parameters'}), 400

    id_event = request.json['id_event']
    id_client = "-" + request.json['id_client'] + "-"
    id_ticket = request.json['id_ticket']
    # Llama al método create_event del contrato inteligente con los parámetros proporcionados
    try:
        #QUITAR LA CLAVE 
        tx_hash = contract.functions.createTicket(id_event, id_client,id_ticket).transact({'from': config('FROM_WALLET')})
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({'transaction_hash': tx_hash.hex(), 'status': receipt.status}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_ticket_data', methods=['POST'])
def get_ticket_data():
    # Obtener el hash de la transacción del cuerpo de la solicitud
    data = request.get_json()
    hash_transaccion = data.get('hash_transaccion')
    pattern = re.compile(r'[^\x20-\x7E]')
    # Consultar la información de la transacción en la blockchain
    try:
        transaccion = web3.eth.get_transaction(hash_transaccion)
		# Extraer los datos relevantes de la transacción
        transaccion_json = {
            'hash': transaccion.hash.hex(),
            'from': transaccion['from'],
            'to': transaccion['to'],
            'value': transaccion['value'],
            'gas': transaccion['gas'],
            # Agrega más campos según lo que necesites
            'input_data_text' : transaccion['input'].decode('utf-8','ignore') if transaccion['input'] else None,
            'input_data': transaccion['input'].hex() if transaccion['input'] else None

        }
        # Aquí puedes procesar la información de la transacción como desees
        text_pros = transaccion_json['input_data_text']
        cleaned_data = pattern.sub('', text_pros)
        cleaned_data_split = cleaned_data.split("-")
        info_from = {
            'id_event':cleaned_data_split[0][3:],
            'id_client':cleaned_data_split[1],
            'id_ticket':cleaned_data_split[2]
        }

        return jsonify({'status': 'success','info':info_from}),200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}),500


#///////////////////////////////////Email/////////////////////////7
def generar_enlace_validacion():
    # Generar un enlace único de validación (por ejemplo, utilizando una cadena aleatoria)
    longitud = 20
    caracteres = string.ascii_letters + string.digits
    enlace = ''.join(random.choice(caracteres) for i in range(longitud))
    return enlace

def enviar_correo_validacion(correo_destino,enlace_validacion):
    # Configuración del servidor SMTP
    servidor_smtp = config('SERVIDOR_SMPT')
    puerto_smtp = config('PUERTO_SMPT')
    remitente = config('CORREO_REMITENTE')
    contraseña = config('PASSWORD_GMAIL')

    # Crear el mensaje
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = correo_destino
    mensaje['Subject'] = "Validación de correo electrónico"

    # Cuerpo del mensaje en formato HTML
    cuerpo_mensaje = f"""
       <html>
       <head>
        <style>
          body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            padding: 20px;
          }}
          .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #fff;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
          }}
          h1 {{
            color: #333;
          }}
          p {{
            color: #666;
          }}
          .button {{
            display: inline-block;
            background-color: #007bff;
            color: #fff;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <h1>Hola,  de MR biglietto </h1>
          <p>Por favor, haz clic en el siguiente enlace para validar tu correo electrónico:</p>
          <a class="button" href="https://mrbigliettoweb.vercel.app/login">Validar correo electrónico</a>
          <p>¡Gracias!</p>
        </div>
      </body>
    </html>
    """
    mensaje.attach(MIMEText(cuerpo_mensaje, 'html'))
    # Iniciar sesión en el servidor SMTP y enviar el mensaje
    with smtplib.SMTP(servidor_smtp, puerto_smtp) as servidor:
        servidor.starttls()
        servidor.login(remitente, contraseña)
        servidor.send_message(mensaje)


@app.route('/send_validation_email', methods=['POST'])
def send_validation_email():
    # Asegúrate de que el cuerpo de la solicitud contenga los parámetros necesarios para el método create_event
    if not request.json or 'email_des' not in request.json:
        return jsonify({'error': 'Missing parameters'}), 400

    email_des = request.json['email_des']
    # Llama al método create_event del contrato inteligente con los parámetros proporcionados
    try:
        enlace_validacion = generar_enlace_validacion()
        enviar_correo_validacion(email_des,enlace_validacion)
        return jsonify({'status': 'success'}),200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def generar_codigo_autenticacion():
    # Generar un código de autenticación de 6 dígitos
    return ''.join(random.choices(string.digits, k=6))

def enviar_codigo_autenticacion(correo_destino,codigo):
    # Configuración del servidor SMTP
    servidor_smtp = config('SERVIDOR_SMPT')
    puerto_smtp = config('PUERTO_SMPT')
    remitente = config('CORREO_REMITENTE')
    contraseña = config('PASSWORD_GMAIL')

    # Crear el mensaje
    mensaje = MIMEMultipart("alternative")
    mensaje['From'] = remitente
    mensaje['To'] = correo_destino
    mensaje['Subject'] = "Código de autenticación de dos factores"

	
    # Cuerpo del mensaje en HTML con CSS
    cuerpo_html = f"""
    <html>
      <head>
        <style>
          body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            padding: 20px;
          }}
          .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #fff;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
          }}
          h1 {{
            color: #333;
          }}
          p {{
            color: #666;
          }}
          .code {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <h1>Hola,</h1>
          <p>Por favor, utiliza el siguiente código de autenticación de dos factores para completar tu proceso de verificación:</p>
          <p class="code">{codigo}</p>
          <p>Este código es válido por un tiempo limitado.</p>
          <p>¡Gracias!</p>
        </div>
      </body>
    </html>
    """

    # Adjuntar parte del mensaje
    mensaje.attach(MIMEText(cuerpo_html, "html"))

	# Iniciar sesión en el servidor SMTP y enviar el mensaje
    with smtplib.SMTP(servidor_smtp, puerto_smtp) as servidor:
        servidor.starttls()
        servidor.login(remitente, contraseña)
        servidor.send_message(mensaje)

@app.route('/api/v1/send_2fa_email', methods=['POST'])
def send_2fa_email():
    # Asegúrate de que el cuerpo de la solicitud contenga los parámetros necesarios para el método create_event
    if not request.json or 'email_des' not in request.json or 'token' not in request.json:
        return jsonify({'error': 'Missing parameters'}), 400

    email_des = request.json['email_des']
    token = request.json['token']
    # Llama al método create_event del contrato inteligente con los parámetros proporcionados
    try:
        codigo = generar_codigo_autenticacion()
        payload = {'code':int(codigo)}
        headers = {'Authorization':'Bearer '+token}
        response = requests.put(config('URL_BASE_BD')+'/api/v1/TwoFactorAuth',json=payload,headers=headers)
       
        if response.status_code == 200:
          enviar_codigo_autenticacion(email_des, codigo)
          return jsonify({'status': 'success'}),200
        else:
          return jsonify({'error': 'Failed to send 2FA code'}), response.status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def enviar_notificacion(correo_destino):
    # Configuración del servidor SMTP
    servidor_smtp = config('SERVIDOR_SMPT')
    puerto_smtp = config('PUERTO_SMPT')
    remitente = config('CORREO_REMITENTE')
    contraseña = config('PASSWORD_GMAIL')

    # Crear el mensaje
    mensaje = MIMEMultipart("alternative")
    mensaje['From'] = remitente
    mensaje['To'] = correo_destino
    mensaje['Subject'] = "Notificacion"

	
    # Cuerpo del mensaje en HTML con CSS
    cuerpo_html = f"""
    <html>
      <head>
        <style>
          body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            padding: 20px;
          }}
          .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #fff;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
          }}
          h1 {{
            color: #333;
          }}
          p {{
            color: #666;
          }}
          .code {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <h1>Hola,</h1>
          <p>Felicidades por tu compra, esperamos que te diviertas en tu evento:</p>
          <p>¡Gracias! por usar Mr biglietto</p>
        </div>
      </body>
    </html>
    """

    # Adjuntar parte del mensaje
    mensaje.attach(MIMEText(cuerpo_html, "html"))

	# Iniciar sesión en el servidor SMTP y enviar el mensaje
    with smtplib.SMTP(servidor_smtp, puerto_smtp) as servidor:
        servidor.starttls()
        servidor.login(remitente, contraseña)
        servidor.send_message(mensaje)

@app.route('/send_notification', methods=['POST'])
def send_notification():
    # Asegúrate de que el cuerpo de la solicitud contenga los parámetros necesarios para el método create_event
    if not request.json or 'email_des' not in request.json:
        return jsonify({'error': 'Missing parameters'}), 400

    email_des = request.json['email_des']
    
    # Llama al método create_event del contrato inteligente con los parámetros proporcionados
    try:
        enviar_notificacion(email_des)
        return jsonify({'status': 'success'}),200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def send_change_pass(correo_destino,token):
    # Configuración del servidor SMTP
    servidor_smtp = config('SERVIDOR_SMPT')
    puerto_smtp = config('PUERTO_SMPT')
    remitente = config('CORREO_REMITENTE')
    contraseña = config('PASSWORD_GMAIL')

    # Crear el mensaje
    mensaje = MIMEMultipart("alternative")
    mensaje['From'] = remitente
    mensaje['To'] = correo_destino
    mensaje['Subject'] = "Cambio de contraseña"

	
    # Cuerpo del mensaje en HTML con CSS
    cuerpo_html = f"""
    <html>
       <head>
        <style>
          body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            padding: 20px;
          }}
          .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #fff;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
          }}
          h1 {{
            color: #333;
          }}
          p {{
            color: #666;
          }}
          .button {{
            display: inline-block;
            background-color: #007bff;
            color: #fff;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <h1>Hola, soy misterbiglietto</h1>
          <p>Por favor, haz clic en el siguiente enlace para restablecer tu contraseña:</p>
          <a class="button" href="https://mrbigliettoweb.vercel.app/login/change?token={token}">Cambiar contraseña</a>
          <p>¡Gracias!</p>
        </div>
      </body>
    </html>
    """

    # Adjuntar parte del mensaje
    mensaje.attach(MIMEText(cuerpo_html, "html"))

	# Iniciar sesión en el servidor SMTP y enviar el mensaje
    with smtplib.SMTP(servidor_smtp, puerto_smtp) as servidor:
        servidor.starttls()
        servidor.login(remitente, contraseña)
        servidor.send_message(mensaje)

@app.route('/send_email_change_password', methods=['POST'])
def send_email_change_password():
    # Asegúrate de que el cuerpo de la solicitud contenga los parámetros necesarios para el método create_event
    if not request.json or 'email' not in request.json or 'token' not in request.json:
        return jsonify({'error': 'Missing parameters'}), 400

    email_des = request.json['email']
    token = request.json['token']
    # Llama al método create_event del contrato inteligente con los parámetros proporcionados
    try:
        send_change_pass(email_des,token)
        return jsonify({'status': 'success'}),200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#/////////////////////////////////Página web////////////////////
@app.route('/')
def index():
  return redirect(url_for('login'))


@app.route('/login', methods =  ['GET','POST'])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    #print(username)
    #print(password)
    user = User(1,username,password) 
    logged_user  = ModelUser.login(user)
    if logged_user.status_code == 200:
      login_user(user)
      return redirect(url_for('home'))
    else:
      flash("User or password are wrong ...")
      return render_template('/auth/login.html') 
  else:
    return render_template('/auth/login.html') 

@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
  return render_template('/home.html')

@app.route('/protected')
@login_required
def protected():
  return "<h1>Esta es una vista protegida, solo para usuario autenticados</h1>"

def status_401(error):
  return redirect(url_for('login'))

def status_404(errror):
  return "<h1>Página no encontrada</h1>",404

app.register_error_handler(401,status_401)
app.register_error_handler(404,status_404)
csrf.init_app(app)

if __name__ == '__main__':
    app.config.from_object(d_config['development'])   
  
    app.run()