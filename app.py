from flask import Flask, request, jsonify
from web3 import Web3, HTTPProvider
from solcx import compile_source
from decouple import config
from flask_cors import CORS
import re
from web3.middleware import construct_sign_and_send_raw_middleware

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
CORS(app)

@app.route('/')
def root():
    return "root"

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




if __name__ == '__main__':
    app.run()