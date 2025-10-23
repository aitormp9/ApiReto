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
    return jsonify(clientes)


if __name__ == '__main__':
    app.run(debug=True)
