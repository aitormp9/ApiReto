import json
from flask import Flask, request, jsonify
import xmlrpc.client

url = "http://reto1odoo.duckdns.org:8069"
bd = "Reto1-TechSolutions"
usuario = "mikelaitoribai"
contrasena = "maireto"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(bd, usuario, contrasena, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

app = Flask(__name__)

@app.route('/getDatos', methods=['GET'])
def getDatos():
    nombre = request.args.get('nombre', '')

    domain = []
    if nombre:
        domain = [['name', 'ilike', nombre]]

    clientes = models.execute_kw(
        bd, uid, contrasena,
        'res.partner', 'search_read',
        [domain],
        {'fields': ['id', 'name', 'email']}
    )


    personas = r"C:\Users\ikmsuarez23\Desktop\Reto\ApiReto\usuario.json"
    with open(personas, "w", encoding="utf-8") as usuario:
        json.dump(clientes, usuario, indent=4, ensure_ascii=False)

    return jsonify(clientes)

@app.route('/añadirDatos' , methods=['POST'])
def añadirDatos():
    data = request.json
    id_cliente = data.get('id')
    nombre = data.get('name') 
    email = data.get('email')
    
    if not nombre:
        return jsonify({'error': 'El nombre es obligatorio'}), 400
    
 
    nuevo_cliente = {
        'name': nombre
    }
    if email:
        nuevo_cliente['email'] = email
    if id_cliente:
        nuevo_cliente['ref'] = str(id_cliente)  
    
    try:
        cliente_id = models.execute_kw(
            bd, uid, contrasena,
            'res.partner', 'create',
            [nuevo_cliente]
        )
        return jsonify({'mensaje': 'Cliente creado correctamente', 'id_odoo': cliente_id}), 201
    except Exception as e:
        return jsonify({'error': f'Error al crear cliente: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
