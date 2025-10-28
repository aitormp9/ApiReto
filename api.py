import json
from flask import Flask, request, jsonify
import xmlrpc.client

url = "http://reto1odoo.duckdns.org:8069"
bd = "Reto1-TechSolutions"
usuario = "mikelaitoribai"
contraseña = "maireto"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(bd, usuario, contraseña, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

app = Flask(__name__)

"""METODOS MOVILES"""

@app.route('/getDatos', methods=['GET'])
def getDatos():
    nombre = request.args.get('nombre', '')

    domain = []
    if nombre:
        domain = [['name', 'ilike', nombre]]

    clientes = models.execute_kw(
        bd, uid, contraseña,
        'res.partner', 'search_read',
        [domain],
        {'fields': ['id', 'name', 'email']}
    )


    """personas = r"C:\\aitormindeguia\\Reto1\\ApiReto1\\ApiReto\\usuario.json"""
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
            bd, uid, contraseña,
            'res.partner', 'create',
            [nuevo_cliente]
        )
        return jsonify({'mensaje': 'Cliente creado correctamente', 'id_odoo': cliente_id}), 201
    except Exception as e:
        return jsonify({'error': f'Error al crear cliente: {str(e)}'}), 500

@app.route('/modificarCliente/<int:id>' , methods=['PUT'])
def modificarCliente(id):
    data = request.json
    nuevo_nombre = data.get('name')
    nuevo_email = data.get('email')
    

    values= {}
    if nuevo_nombre: 
        values['name'] = nuevo_nombre
        
    if nuevo_email:
        values['email'] = nuevo_email
        
    if not values :
        return jsonify({'error': 'No hay datos para  modificar '}),400 
        
    
    try:
        models.execute_kw(
            bd, uid, contraseña,
            'res.partner', 'write',
            [[int (id)], values]
        )
        return jsonify({'mensaje': f'Cliente {id} modificado correctamente'})
    except Exception as e:
        return jsonify({'error': f'Error al modificar cliente: {str(e)}'}), 500
    
@app.route('/eliminarCliente/<int:id>' , methods=['DELETE'])
def eliminarCliente(id):
    if not id :
        return jsonify({'error': 'No se ha borrado el contacto'}),400
    
    try:
        models.execute_kw(
            bd, uid, contraseña,
            'res.partner', 'unlink',
            [[id]]
        )
        return jsonify({'mensaje': f'Cliente {id} eliminado correctamente'})
    except Exception as e:
        return jsonify({'error': f'Error al eliminar cliente: {str(e)}'}), 500  
    
    
"""METODOS INTERFACES"""
@app.route('/VentasMes', methods=['GET'])
def VentasMes():
    from datetime import datetime
    
    hoy = datetime.today()
    PrimerDia = hoy.replace(day=1).strftime('%Y-%m-%d 00:00:00')
    UltimoDia = hoy.strftime('%Y-%m-%d 23:59:59')
    
    domain = [
    ['date_order', '>=', PrimerDia],
    ['date_order', '<=', UltimoDia],
    ['state', 'in', ['sale','done']]
    ]
    
    try:
        ventas_mes = models.execute_kw(
            bd,uid,contraseña,
            'sale.order' , 'search_count',
            [domain]     
    )
        return jsonify({'Ventas mes' : ventas_mes})
    except Exception as e:
        return jsonify({'error': f'Error al obtener ventas: {str(e)}'}), 500


@app.route('/TotalVentas', methods=['GET'])
def totalVentas():
    try:
        
        domain = [
            ['state', 'in', ['sale', 'done']]
        ]

        ventas_ids = models.execute_kw(
            bd, uid, contraseña,
            'sale.order', 'search',
            [domain]
        )

        if not ventas_ids:
            return jsonify({'TotalVentas': 0, 'mensaje': 'No hay ventas registradas'})

        ventas = models.execute_kw(
            bd, uid, contraseña,
            'sale.order', 'read',
            [ventas_ids],
            {'fields': ['amount_total']}
        )

        total = sum(v['amount_total'] for v in ventas if 'amount_total' in v)

        return jsonify({'TotalVentas': total})
    
    except Exception as e:
        return jsonify({'error': f'Error al obtener el total de ventas: {str(e)}'}), 500

    
@app.route('/PedidosPendientes' , methods=['GET'])
def PedidosPendientes():
    try:
            
            domain =[
                ['state' , '=' , 'sale']
            ]
            
            pedidos_pendientes = models.execute_kw(
                bd,uid,contraseña,
                'sale.order' , 'search_read',
                [domain],
                {'fields' : ['id' , 'name' , 'date_order' , 'amount_total' , 'state']}
            )
            
            return jsonify({'Pedidos Pendientes' : pedidos_pendientes})
    
    except Exception as e :
        return jsonify({'error' : f'Error del estado del pedido: {str(e)}'}),500
    

@app.route('/StockBajo' , methods=['GET'])
def StockBajos():
    
    try:
        domain=[
            ['qty_available', '<' , 5]
            ]
        
        productos_stockBajo = models.execute_kw(
            bd,uid,contraseña,
            'product.product' , 'search_read',
            [domain],
            {'fields' : ['id' , 'name' , 'qty_available' , 'virtual_available']}
        )
        
        return jsonify({'Producto stock bajo' : productos_stockBajo})
    except Exception as e :
        return jsonify({'error' : f'Error de stock del producto: {str(e)}'}),500
    
@app.route('/ClientesDestacados', methods=['GET'])
def ClientesDestacados():
    try:
        nombre = request.args.get('nombre', '')

        domain = [['customer_rank' , '>=' , 1]]
        if nombre:
            domain.append = [['name', 'ilike', nombre]]

        clientes_destacados = models.execute_kw(
            bd, uid, contraseña,
            'res.partner', 'search_read',
            [domain],
            {'fields': ['id', 'name', 'email' , 'customer_rank']}
        )   
        
        return jsonify({'Clientes destacados': clientes_destacados})
    except Exception as e :
        return jsonify({'error' : f'Error de cliente destacado: {str(e)}'}),500
        
if __name__ == '__main__':
    app.run(debug=True)
