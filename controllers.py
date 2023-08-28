from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

# Configuración de la conexión a la base de datos
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "agustin79agu",
    "database": "sales"
}


# Configuración de la conexión a la base de datos "production"
production_db_config = {
    "host": "localhost",
    "user": "root",
    "password": "agustin79agu",
    "database": "production"
}

# Ejercicio 1.1: Obtener un cliente por su ID
@app.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM sales.customers WHERE customer_id = %s"
        cursor.execute(query, (customer_id,))
        customer = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if customer:
            return jsonify(customer), 200
        else:
            return jsonify({"message": "Cliente no encontrado"}), 404
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Error interno"}), 500


# Ejercicio 1.2: Obtener el listado de clientes con filtro opcional por estado
@app.route('/customers', methods=['GET'])
def get_customers():
    state_filter = request.args.get('state')
    
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        if state_filter:
            query = f"SELECT * FROM customers WHERE state = '{state_filter}'"
        else:
            query = "SELECT * FROM customers"
        
        cursor.execute(query)
        result = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        total_customers = len(result)
        response_data = {
            "customers": result,
            "total": total_customers
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Error interno"}), 500
# Ejercicio 1.3: Registrar un cliente
@app.route('/customers', methods=['POST'])
def create_customer():
    try:
        data = request.json
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        phone = data.get("phone")
        
        if not first_name or not last_name or not email:
            return jsonify({"message": "Nombre, apellido y email son obligatorios"}), 400
        
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = "INSERT INTO sales.customers (first_name, last_name, email, phone) VALUES (%s, %s, %s, %s)"
        values = (first_name, last_name, email, phone)
        cursor.execute(query, values)
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({}), 201
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Error interno"}), 500
# Ejercicio 1.4: Modificar un cliente
@app.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    try:
        data = request.json
        email = data.get("email")
        phone = data.get("phone")
        
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = "UPDATE sales.customers SET email = %s, phone = %s WHERE customer_id = %s"
        values = (email, phone, customer_id)
        cursor.execute(query, values)
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Error interno"}), 500
# Ejercicio 1.5: Eliminar un cliente por su ID
@app.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        query = "DELETE FROM sales.customers WHERE customer_id = %s"
        cursor.execute(query, (customer_id,))
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return jsonify({}), 204
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Error interno"}), 500
    
# Ejercicio 2.1: Obtener un producto por su ID
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT p.product_id, p.product_name, p.model_year, p.list_price, b.brand_id, b.brand_name, c.category_id, c.category_name " \
                "FROM production.products AS p " \
                "JOIN production.brands AS b ON p.brand_id = b.brand_id " \
                "JOIN production.categories AS c ON p.category_id = c.category_id " \
                "WHERE p.product_id = %s"
        
        cursor.execute(query, (product_id,))
        product = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if product:
            response = {
                "product_id": product["product_id"],
                "product_name": product["product_name"],
                "model_year": product["model_year"],
                "list_price": float(product["list_price"]),
                "brand": {
                    "brand_id": product["brand_id"],
                    "brand_name": product["brand_name"]
                },
                "category": {
                    "category_id": product["category_id"],
                    "category_name": product["category_name"]
                }
            }
            return jsonify(response), 200
        else:
            return jsonify({"message": "Producto no encontrado"}), 404
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Error interno"}), 500
    
    
# Ejercicio 2.2: Obtener un listado de productos
@app.route('/products', methods=['GET'])
def get_products():
    brand_id = request.args.get('brand_id')
    category_id = request.args.get('category_id')
    
    try:
        production_connection = mysql.connector.connect(**production_db_config)
        cursor = production_connection.cursor(dictionary=True)
        
        query = "SELECT p.product_id, p.product_name, p.model_year, p.list_price, b.brand_id, b.brand_name, c.category_id, c.category_name " \
                "FROM production.products AS p " \
                "JOIN production.brands AS b ON p.brand_id = b.brand_id " \
                "JOIN production.categories AS c ON p.category_id = c.category_id "
        
        conditions = []
        if brand_id:
            conditions.append(f"b.brand_id = {brand_id}")
        if category_id:
            conditions.append(f"c.category_id = {category_id}")
        
        if conditions:
            query += "WHERE " + " AND ".join(conditions)
        
        cursor.execute(query)
        products = cursor.fetchall()
        
        cursor.close()
        production_connection.close()
        
        total_products = len(products)
        response_data = {
            "products": products,
            "total": total_products
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Error interno"}), 500    

# Ejercicio 2.3: Registrar un producto
@app.route('/products', methods=['POST'])
def create_product():
    try:
        production_connection = mysql.connector.connect(**production_db_config)
        cursor = production_connection.cursor()
        
        data = request.json
        product_name = data.get('product_name')
        brand_id = data.get('brand_id')
        category_id = data.get('category_id')
        model_year = data.get('model_year')
        list_price = data.get('list_price')
        
        if not product_name or not brand_id or not category_id or not model_year or not list_price:
            return jsonify({"message": "Datos incompletos"}), 400
        
        query = "INSERT INTO production.products (product_name, brand_id, category_id, model_year, list_price) " \
                "VALUES (%s, %s, %s, %s, %s)"
        values = (product_name, brand_id, category_id, model_year, list_price)
        cursor.execute(query, values)
        production_connection.commit()
        
        cursor.close()
        production_connection.close()
        
        return jsonify({}), 201
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Error interno"}), 500
    
    
# Ejercicio 2.4: Modificar un producto
@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        production_connection = mysql.connector.connect(**production_db_config)
        cursor = production_connection.cursor()
        
        data = request.json
        list_price = data.get('list_price')
        
        if list_price is None:
            return jsonify({"message": "No se proporcionaron datos para modificar"}), 400
        
        query = "UPDATE production.products SET list_price = %s WHERE product_id = %s"
        values = (list_price, product_id)
        cursor.execute(query, values)
        production_connection.commit()
        
        cursor.close()
        production_connection.close()
        
        return jsonify({"message": "Producto modificado exitosamente"}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Error interno"}), 500
    
    
# Ejercicio 2.5: Eliminar un producto
@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        production_connection = mysql.connector.connect(**production_db_config)
        cursor = production_connection.cursor()
        
        query = "DELETE FROM production.products WHERE product_id = %s"
        cursor.execute(query, (product_id,))
        production_connection.commit()
        
        cursor.close()
        production_connection.close()
        
        return jsonify({"message": "Producto eliminado exitosamente"}), 204
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "Error interno"}), 500    

if __name__ == '__main__':
    app.run(debug=True)
