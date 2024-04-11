from flask import Flask, request, jsonify, render_template, redirect , url_for,flash
from flask_login import LoginManager,login_user, logout_user, login_required
from web3 import Web3
from decouple import config
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
from flask_cors import CORS
import re
import json
import requests
from web3.middleware import construct_sign_and_send_raw_middleware
from config import d_config
from flask_wtf.csrf import CSRFProtect
from models.ModelUser import ModelUser
from models.entities.User import User
from models.ModelArtist import ModelArtist
from models.entities.Artist import Artist
from models.ModelLocation import ModelLocation
from models.entities.Location import Location
from models.entities.Section import Section
from models.ModelTheater import ModelTheater
from models.entities.Theater import Theater
from models.pub_api import Publisher
from models.ModelEvent import ModelEvent
from models.entities.Event import Event
from models.ModelRefund import ModelRefund
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

@login_manager_app.user_loader
def load_user(username):
  return ModelUser.get_by_username(username)

#/////////////////////////////////////////////////////////

@app.route('/firebase-config')
def get_firebase_config():
    firebase_config = {
        'apiKey': config('FIREBASE_API_KEY'),
        'authDomain': config('FIREBASE_AUTH_DOMAIN'),
        'projectId': config('FIREBASE_PROJECT_ID'),
        'storageBucket': config('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': config('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': config('FIREBASE_APP_ID')
    }
    return jsonify(firebase_config)

#///////////////////////////////////////////////////////////


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


#/////////////////////////////////// API EMAIL /////////////////////////////////////////
def generar_enlace_validacion():
    # Generar un enlace único de validación (por ejemplo, utilizando una cadena aleatoria)
    longitud = 20
    caracteres = string.ascii_letters + string.digits
    enlace = ''.join(random.choice(caracteres) for i in range(longitud))
    return enlace

def enviar_correo_validacion(correo_destino,token):
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
    cuerpo_mensaje = render_template('correo_validacion.html',token=token)
    mensaje.attach(MIMEText(cuerpo_mensaje, 'html'))
    # Iniciar sesión en el servidor SMTP y enviar el mensaje
    with smtplib.SMTP(servidor_smtp, puerto_smtp) as servidor:
        servidor.starttls()
        servidor.login(remitente, contraseña)
        servidor.send_message(mensaje)

@app.route('/send_validation_email', methods=['POST'])
def send_validation_email():
    # Asegúrate de que el cuerpo de la solicitud contenga los parámetros necesarios para el método create_event
    if not request.json or 'email_des' not in request.json or 'token' not in request.json:
        return jsonify({'error': 'Missing parameters'}), 400

    email_des = request.json['email_des']
    token = request.json['token']
    # Llama al método create_event del contrato inteligente con los parámetros proporcionados
    try:
        enlace_validacion = generar_enlace_validacion()
        enviar_correo_validacion(email_des,token)
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

def enviar_notificacion(email,username,event_name):
    # Configuración del servidor SMTP
    servidor_smtp = config('SERVIDOR_SMPT')
    puerto_smtp = config('PUERTO_SMPT')
    remitente = config('CORREO_REMITENTE')
    contraseña = config('PASSWORD_GMAIL')

    # Crear el mensaje
    mensaje = MIMEMultipart("alternative")
    mensaje['From'] = remitente
    mensaje['To'] = email
    mensaje['Subject'] = "Notificacion"
    # Cuerpo del mensaje en HTML con CSS
    cuerpo_mensaje = render_template('email_notification.html',username=username,event_name=event_name)
    # Adjuntar parte del mensaje
    mensaje.attach(MIMEText(cuerpo_mensaje, "html"))

	# Iniciar sesión en el servidor SMTP y enviar el mensaje
    with smtplib.SMTP(servidor_smtp, puerto_smtp) as servidor:
        servidor.starttls()
        servidor.login(remitente, contraseña)
        servidor.send_message(mensaje)

@app.route('/api/v1/send_notification', methods=['POST'])
def send_notification():
    # Asegúrate de que el cuerpo de la solicitud contenga los parámetros necesarios para el método create_event
    if not request.json or 'email' not in request.json or 'username' not in request.json or 'event_name' not in request.json:
        return jsonify({'error': 'Missing parameters'}), 400

    email = request.json['email']
    username = request.json['username']
    event_name = request.json['event_name']
    
    # Llama al método create_event del contrato inteligente con los parámetros proporcionados
    try:
        enviar_notificacion(email,username,event_name)
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

    cuerpo_mensaje = render_template('correo_change_pass.html',token=token)
    # Adjuntar parte del mensaje
    mensaje.attach(MIMEText(cuerpo_mensaje, "html"))

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
      
def send_email_help_to(email_user,email_help,message):
    servidor_smtp = config('SERVIDOR_SMPT')
    puerto_smtp = config('PUERTO_SMPT')
    remitente = config('CORREO_REMITENTE')
    contraseña = config('PASSWORD_GMAIL')

    # Crear el mensaje
    mensaje = MIMEMultipart("alternative")
    mensaje['From'] = remitente
    mensaje['To'] = email_help
    mensaje['Subject'] = "Solicitud de ayuda"

    cuerpo_mensaje = render_template('email_help.html',email_user = email_user,message = message)
    # Adjuntar parte del mensaje
    mensaje.attach(MIMEText(cuerpo_mensaje, "html"))

	# Iniciar sesión en el servidor SMTP y enviar el mensaje
    with smtplib.SMTP(servidor_smtp, puerto_smtp) as servidor:
        servidor.starttls()
        servidor.login(remitente, contraseña)
        servidor.send_message(mensaje)

      
@app.route('/api/v1/send_email_help',methods=['POST'])
def send_email_help():
  if not request.json or 'email_user' not in request.json or 'email_help' not in request.json or 'message' not in request.json:
    return jsonify({'error':'Missing parameters'}), 400
  
  email_user = request.json['email_user']
  email_help = request.json['email_help']
  message = request.json['message']
  
  try:
    send_email_help_to(email_user,email_help,message)
    return jsonify({'status': 'success'}),200
  except Exception as e:
    return jsonify({'error':str(e)}), 500
  
def send_email_resale_to(email, status):
    #Configuración del servidor SMTP
    servidor_smtp = config('SERVIDOR_SMPT')
    puerto_smtp = config('PUERTO_SMPT')
    remitente = config('CORREO_REMITENTE')
    contraseña = config('PASSWORD_GMAIL')

    # Crear el mensaje
    mensaje = MIMEMultipart("alternative")
    mensaje['From'] = remitente
    mensaje['To'] = email
    mensaje['Subject'] = "Respuesta de venta de boleto"

    cuerpo_mensaje = render_template('email_resale.html',status=status)
    # Adjuntar parte del mensaje
    mensaje.attach(MIMEText(cuerpo_mensaje, "html"))

	# Iniciar sesión en el servidor SMTP y enviar el mensaje
    with smtplib.SMTP(servidor_smtp, puerto_smtp) as servidor:
        servidor.starttls()
        servidor.login(remitente, contraseña)
        servidor.send_message(mensaje)


@app.route('/api/v1/send_email_resale',methods=['POST'])
def send_email_resale():
  if not request.json or 'email' not in request.json or 'status' not in request.json:
    return jsonify({'error':'Missing parameters'}), 400
  
  email = request.json['email']
  status = request.json['status']
  try:
    send_email_resale_to(email,status)
    return jsonify({'status': 'success'}),200
  except Exception as e:
    return jsonify({'error':str(e)}), 500
  

def send_email_refund_to(email,id_refund,message):
  # Configuración del servidor SMTP
    servidor_smtp = config('SERVIDOR_SMPT')
    puerto_smtp = config('PUERTO_SMPT')
    remitente = config('CORREO_REMITENTE')
    contraseña = config('PASSWORD_GMAIL')

    # Crear el mensaje
    mensaje = MIMEMultipart("alternative")
    mensaje['From'] = remitente
    mensaje['To'] = email
    mensaje['Subject'] = "Respuesta de devolucion"

    cuerpo_mensaje = render_template('email_refund.html',id_refund=id_refund, message = message)
    # Adjuntar parte del mensaje
    mensaje.attach(MIMEText(cuerpo_mensaje, "html"))

	# Iniciar sesión en el servidor SMTP y enviar el mensaje
    with smtplib.SMTP(servidor_smtp, puerto_smtp) as servidor:
        servidor.starttls()
        servidor.login(remitente, contraseña)
        servidor.send_message(mensaje)

@app.route('/api/v1/send_email_refund',methods=['POST'])
def send_email_refund():
  if not request.json or 'email' not in request.json or 'status' not in request.json or 'id_refund' not in request.json:
    return jsonify({'error':'Missing parameters'}), 400
  
  email = request.json['email']
  status = request.json['status']
  id_refund = request.json['id_refund']
  message = ""
  if status == 1:
    message = "Ha sido aprobado"
  elif status == 0:
    message = "Ha sido rechazado"
  elif status == -1:
    message = "Has cancelado la devolucion"
  else:
    return jsonify({'error':'Status out of range'}),500
    
  
  try:
    send_email_refund_to(email,id_refund,message)
    return jsonify({'status': 'success'}),200
  except Exception as e:
    return jsonify({'error':str(e)}), 500
  
  

#/////////////////////////////////Página web////////////////////
@app.route('/')
def index():
  return redirect(url_for('login'))


@app.route('/login', methods =  ['GET','POST'])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    user = User(1,username,password) 
    logged_user  = ModelUser.login(user)
    if logged_user.status_code == 200:
      data = json.loads(logged_user.text)
      user.setUserId(data['name'])
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

@app.route('/home',methods=['GET','POST'])
@login_required
def home():
  if request.method == 'POST':
    form_data = request.form.to_dict()
    artist = form_data['artists']
    artist_json = artist.replace("'",'"')
    artist_dict = json.loads(artist_json)
    id_artist = artist_dict['idArtist']
    theater = form_data['theaters']
    theater_json = theater.replace("'",'"')
    theater_json = theater_json.replace("None","0")
    theater_json = theater_json.replace("False","false")
    theater_dict = json.loads(theater_json)
    id_theater = theater_dict['idTheater']
    date_hour = form_data['fecha_y_hora'] + ":00"
    section_list = []
    sections = theater_dict['sections']
    for s in sections:
      id_section = s['idSection']
      available_seats = s['availableSeats']
      price = form_data[f"precio{id_section}"]
      section = Section(id_section,available_seats,price)
      section_list.append(section)       
    
    event = Event(id_artist,id_theater,date_hour,section_list)
    response = ModelEvent.register_event(event)
    if response.status_code == 200:
      flash("Evento registrado correctamente")
      return set_events_view()
    elif response.status_code == 401:
      flash("Bad Request")
      return set_events_view()
    else:
      flash("server error")
      return set_events_view()
  else:
    return set_events_view()


def set_events_view():
  response_artist = ModelArtist.get_artists()
  artists_json = response_artist.json()
  artists = []
  response_theaters = ModelTheater.get_theaters()
  theaters_json = response_theaters.json()
  theaters = []
  for a in artists_json:
    artists.append(a)
  for t in theaters_json:
    theaters.append(t)
  return render_template('/home.html',artists=artists,theaters=theaters) 

@app.route('/register_theater',methods=['GET','POST'])
@login_required
def register_theater():
  if request.method == 'POST':
    form_data = request.form.to_dict()
    name_theater = form_data['nameTheather']
    theater_url = form_data['theaterUrl']
    locations = form_data['options']
    locations_dict = eval(locations)
    id_location = locations_dict['idLocation']
    aux_dict = form_data
    del aux_dict['nameTheather']
    del aux_dict['options']
    del aux_dict['theaterUrl']
    sections = []
    section_index = 1
    while True:
      section_key = f"section_name_{section_index}"
      if section_key not in aux_dict:
        break
    
      section_name = aux_dict.get(section_key)
      num_columns = aux_dict.get(f"num_columns_{section_index}")
      num_rows = aux_dict.get(f"num_rows_{section_index}")
      seats_ave = aux_dict.get(f"seats_ave_{section_index}")

      if section_name is None or num_columns is None or num_rows is None or seats_ave is None:
        break
      is_general = True
      section = Section(section_name, num_columns, num_rows,is_general, seats_ave)
      sections.append(section)
    
      section_index += 1

    theater = Theater(name_theater,id_location,sections,theater_url)
    response = ModelTheater.register_theater(theater)
    print(response)
    if response.status_code == 200:
      flash("Teatro registrado correctamente")
      return send_register_theater_view()
    elif response.status_code == 409:
      flash("Error con el id")
      return send_register_theater_view() 
    elif response.status_code == 400:
      flash("Error en la base de datos")
      return send_register_theater_view()
    else:
      flash("Server error")
      return send_register_theater_view()
  else:
    return send_register_theater_view()

def send_register_theater_view():
  response = ModelLocation.get_locations()
  locations = response.json() 
  opciones = []
  for location in locations:     
    opciones.append(location)  
  return render_template('/register_theater.html',lista=opciones)


@app.route('/register_artist',methods=['GET','POST'])
@login_required
def register_artist():
  if request.method == 'POST':
    artistName = request.form['artistName']
    artistDescription = request.form['artistDescription']
    artistGenre = request.form['artistGenre']
    artistUrl = request.form['artistUrl']
    artistTourName = request.form['artistTourName']
    artist = Artist(artistName,
                  artistDescription,
                  artistGenre,
                  artistUrl,
                  artistTourName)
    response = ModelArtist.register_artist(artist)
    if response.status_code == 200:
      flash("Artista registrado correctamente")
      return render_template('/register_artist.html')
    elif response.status_code == 400:
      flash("Error" + response.text['title'])
      return render_template('/register_artist.html')
    else:
      flash("Something went wrong ...")
      return render_template('/register_artist.html')
  else:
    return render_template('/register_artist.html')
  
@app.route('/refund_view',methods=['GET','POST'])
@login_required
def refund_view():
  if request.method == 'POST':
    data = request.json
    request_id = data['requestId']
    answer = data['answer']
    result = True
    if answer == 'APPROVED':
      result = True
    elif answer == 'DENIED':
      result == False
    else:
      return jsonify({'message': 'Dato raro'}),500
    
    response = ModelRefund.set_answer(request_id,result)
    if response.status_code == 200:
      flash("Respuesta enviada y recibida")
      return jsonify({'message': 'Bien'}),200
    else:
      flash("Error al guardar la respuesta")
      return jsonify({'message': 'mal'}),500

  else:
    return set_view_refund()
  
  
def set_view_refund():
  response = ModelRefund.get_refunds()
  refunds = response.json() 
  ids = []
  for r in refunds:     
    ids.append(r)
  return render_template('/refund_view.html',list_refund = ids)
    

@app.route('/register_location',methods=['GET','POST'])
@login_required
def register_location():
  if request.method == 'POST':
    id = request.form['id']
    country = request.form['country']
    state = request.form['state']
    city = request.form['city']
    colony = request.form['colony']
    postal_code = request.form['postal_code']
    address = request.form['address']
    location = Location(id,country,state,city,colony,postal_code,address)
    response = ModelLocation.register_location(location)
    if response.status_code == 200:
      flash("Ubicacion registrado correctamente")
      return render_template('/register_location.html')
    elif response.status_code == 409:
      flash("Error con el id")
      return render_template('/register_location.html')
    elif response.status_code == 400:
      flash("Error en la base de datos")
      return render_template('/register_location.html')
    else:
      flash("Server error")
      return render_template('/register_location.html')
  else:
    response = ModelLocation.get_locations()
    locations = response.json() 
    ids = []
    for location in locations:     
      ids.append(location['idLocation'])  
    return render_template('/register_location.html',ids=ids)

#PUB SUB///////////////////////////////////////////////////////////////////////////////////////////
@app.route('/pub_task', methods=['GET','POST'])
def pub_task():
    if request.method == 'POST':
        if not request.json or 'id_event' not in request.json or 'id_client' not in request.json or 'id_ticket' not in request.json or 'email' not in request.json or 'username' not in request.json or 'event_name' not in request.json:
            return jsonify({'error':'Missing parameters'}), 400
        
        id_event = request.json['id_event']
        id_client = request.json['id_client']
        id_ticket = request.json['id_client']
        email = request.json['email']
        username = request.json['username']
        event_name = request.json['event_name']
        
        try:
            message = f"{id_event} {id_client} {id_ticket} {email} {username} {event_name}"
            pub = Publisher()
            pub.pub_task(message)
            return jsonify({"message": "Task published successfully"}), 200
        except Exception as ex:
                raise Exception(ex)
    else:
        return "<h1>Get</h1>"


def status_401(error):
  return redirect(url_for('login'))

def status_404(errror):
  return render_template('/error_404.html')

# Manejador de errores para excepciones no manejadas
#@app.errorhandler(Exception)
#def handle_unhandled_exception(e):
#  flash("Error en servidor...")
#  return redirect(url_for('home'))

#@app.route('/api/v1/test_email/<status>',methods=['GET'])
#def test_email(status):
#  return render_template('email_resale.html',status=status)
 
app.register_error_handler(401,status_401)
app.register_error_handler(404,status_404)

if __name__ == '__main__':
    app.config.from_object(d_config['development'])   
  
    app.run()