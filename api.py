from flask import Flask, request, jsonify

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
    #app.run(debug=True, port=8069,host='54.196.237.226')