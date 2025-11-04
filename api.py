#Imports
import json
from flask import Flask, request, jsonify
import xmlrpc.client
from flask_cors import CORS 
#Url del Api de nuestro odoo, con su base de datos, nuestro usuario y la contraseña
url = "http://reto1odoo.duckdns.org:8069"
bd = "Reto1-TechSolutions"
usuario = "mikelaitoribai"
contraseña = "maireto"

#Conexion con el endpoint/Common de odoo
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
#Autenticacipn o credenciales correctas
uid = common.authenticate(bd, usuario, contraseña, {})
#Apunta al endpoint/Objecto de odod
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

app = Flask(__name__)
CORS(app)

"""METODOS MOVILES"""
#Metodo de recoger los datos de nuestros contactos de odoo 
@app.route('/getDatos', methods=['GET'])
def getDatos():
    nombre = request.args.get('nombre', '')

    domain = []
    if nombre:
        domain = [['name', 'ilike', nombre]]

    contactos = models.execute_kw(
        bd, uid, contraseña,
        'res.partner', 'search_read',
        [domain],
        {'fields': ['id', 'name', 'email','phone','image_1920']}
    )
    for c in contactos:
        if 'image_1920' in c and c['image_1920']:
            c['image_1920'] = f"data:image/png;base64,{c['image_1920']}"   

    return jsonify(contactos)
    personas = r"C:\Users\ikimatarranz24\Documents\ApiReto\usuario.json"
    # personas = r"C:\\aitormindeguia\\Reto1\\ApiReto1\\ApiReto\\usuario.json"
    # personas = r"C:\Users\ikmsuarez23\Desktop\Reto\ApiReto\usuario.json"
    with open(personas, "w", encoding="utf-8") as usuario:
        json.dump(contactos, usuario, indent=4, ensure_ascii=False)

    return jsonify(contactos)

#Metodo del login en el cual insertamos datos 
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Usuario y contraseña son obligatorios'}), 400

    try:
        uid = common.authenticate(bd, username, password, {})
        if uid:
            return jsonify({'uid': uid, 'username': username}), 200
        else:
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
    except Exception as e:
        return jsonify({'error': f'Error de autenticación: {str(e)}'}), 500

#Metodo añadir tambien en el cual añadimos datos, para poder añadir nuevos contactos
@app.route('/añadirDatos' , methods=['POST'])
def añadirDatos():
    data = request.json
    id_contacto = data.get('id')
    nombre = data.get('name') 
    email = data.get('email')
    telefono = data.get('phone')
    foto = data.get('image_1920')
    
    if not nombre:
        return jsonify({'error': 'El nombre es obligatorio'}), 400
    
 
    nuevo_contacto = {
        'name': nombre
    }
    if email:
        nuevo_contacto['email'] = email
    if id_contacto:
        nuevo_contacto['ref'] = str(id_contacto)    
    if telefono:
        nuevo_contacto['phone'] = telefono
    if foto:
        if foto.startswith('data:image'):
            foto = foto.split(',')[1]  
        nuevo_contacto['image_1920'] = foto
    try:
        contacto_id = models.execute_kw(
            bd, uid, contraseña,
            'res.partner', 'create',
            [nuevo_contacto]
        )
        return jsonify({'mensaje': 'Contacto creado correctamente', 'id_odoo': contacto_id}), 201
    except Exception as e:
        return jsonify({'error': f'Error al crear contacto: {str(e)}'}), 500

#Metodo de modificar el contacto en el cual cogemos un contacto y le indicamos el id de ese contacto y despues hacemos la modificacion
@app.route('/modificarContacto/<int:id>' , methods=['PUT'])
def modificarContacto(id):
    data = request.json
    nuevo_nombre = data.get('name')
    nuevo_email = data.get('email')
    nuevo_telefono = data.get('phone')
    nueva_foto = data.get('image_1920')
    
    values= {}
    if nuevo_nombre: 
        values['name'] = nuevo_nombre
        
    if nuevo_email:
        values['email'] = nuevo_email
        
    if nuevo_telefono:
        values['phone'] = nuevo_telefono
        
    if nueva_foto:
        if nueva_foto.startswith('data:image'):
            nueva_foto = nueva_foto.split(',')[1]  # Base64 limpio
        values['image_1920'] = nueva_foto
        
    if not values :
        return jsonify({'error': 'No hay datos para  modificar '}),400 
        
    
    try:
        models.execute_kw(
            bd, uid, contraseña,
            'res.partner', 'write',
            [[int (id)], values]
        )
        return jsonify({'mensaje': f'Contacto {id} modificado correctamente'})
    except Exception as e:
        return jsonify({'error': f'Error al modificar contacto: {str(e)}'}), 500

#Metodo de eliminar contacto es parecido a modificar solo que el metodo es delete pero tambien cogemos el id de ese contacto    
@app.route('/eliminarContacto/<int:id>' , methods=['DELETE'])
def eliminarContacto(id):
    if not id :
        return jsonify({'error': 'No se ha borrado el contacto'}),400
    
    try:
        models.execute_kw(
            bd, uid, contraseña,
            'res.partner', 'unlink',
            [[id]]
        )
        return jsonify({'mensaje': f'Contacto {id} eliminado correctamente'})
    except Exception as e:
        return jsonify({'error': f'Error al eliminar contacto: {str(e)}'}), 500  
    
    
"""METODOS INTERFACES"""
#Metodo del numero de ventas del mes, hacemos un get desde el primer y el ultimo dia del mes, a traves de la fuente de ventas 
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

#Metodo de total de ventas tambien es un metodo get, en el cual cogemos todo el presupuesto y tambien desde la fuente de ventas
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

 #Metodo de pedidosPendientes hago la llamada de los pedidos pero aqui llamo a todos luego en la interfaz si que los separo por su estado 
@app.route('/PedidosPendientes' , methods=['GET'])
def PedidosPendientes():
    try:
            
            domain =[
          ['state', 'in', ['sale', 'draft', 'done']]
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
    
#Metodo de stockBajo igual que en pedidos pendientes llamo a todos los productos por la fuente de product.product y en la interfaz tambien los separo en funcion de su estado
@app.route('/StockBajo' , methods=['GET'])
def StockBajos():
    
    try:
        domain=[
            ['qty_available', '>' , 0]
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
   
#Metodo de clientes destacados hago la llamada en funcion del numero de compras , en este caso igual a 1 o mayor que 1 
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
    app.run(host='0.0.0.0', debug=True, port=5000)
