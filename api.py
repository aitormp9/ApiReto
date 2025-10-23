from flask import Flask, request, jsonify
import xmlrpc.client

url = "http://reto1odoo.duckdns.org:8069"
bd = "Reto1odoo"
usuario = "mikelaitoribai"
contrasena = "maireto"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(bd, usuario, contrasena, {})

app = Flask(__name__)
clientes = list()

@app.route('/getDatos', methods=['GET'])
def getDatos():
    nombre = request.args.get('nombre')

@app.route('/modificarCliente', methods=[''])

@app.route('/eliminarCliente', methods=['DELETE'])
def eliminarCliente(nombre):
    for cliente in clientes:
        if cliente[0].strip() == nombre.strip():
            clientes.remove(cliente)
            return jsonify({'mensaje' : f'Se ha eliminado a {nombre}'})
        return jsonify({'mensaje' : 'No se ha eliminado a nadie'})


if __name__ == '__main__':
    app.run()