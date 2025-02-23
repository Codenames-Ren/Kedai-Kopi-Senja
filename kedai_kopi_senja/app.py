from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import hashlib

class Database:
    def __init__(self, db_name='database.db'):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        create_table_query = ''' CREATE TABLE IF NOT EXISTS users (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user'
        )
        '''
        self.query(create_table_query)

    def query(self, query, args=(), one=False):
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            print(f"Query yang di eksekusi : {query}")
            print(f"Dengan Argument : {args}")

            if isinstance(args,(list, tuple)):
                cursor.execute(query, args)
            else:
                cursor.execute(query, (args,))

            if query.strip().upper().startswith('SELECT'):
                rv = cursor.fetchall()
            else:
                rv = []
                conn.commit()  # Commit untuk INSERT, UPDATE, DELETE

            conn.close()
            return (rv[0] if rv else None) if one else rv
        
        except Exception as e:
            print(f"Database Error : {str(e)}")
            print(f"Query : {query}")
            print(f"Argument : {args}")
            conn.close()
            raise e


class Auth:
    def __init__(self, db):
        self.db = db
    
    def login(self, username, password):
        try:
            user = self.db.query('SELECT * FROM users WHERE username = ?', 
                                (username), one=True)
            if user:
                input_password_hash = hashlib.sha256(password.encode()).hexdigest()
                if input_password_hash == user[2]:
                    return {'username': user[1], 'role': user[3]}
            return None
        
        except Exception as e:
            print(f"Login Error : {str(e)}")
            return None

    def check_auth(self):
        return 'username' in session

    def check_admin(self):
        return self.check_auth() and session.get('role') == 'admin'
    
    def register(self, username, password, role='user'):
        if not username or not password:
            return {'error': 'Username dan password harus diisi!'}
        
        try:
            existing_user = self.db.query('SELECT * FROM users WHERE username = ?', (username,), one=True)
        
            if existing_user:
                return {"error": 'Username sudah terdaftar!'}
        
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            self.db.query('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, hashed_password, role))
            return {'success': True, 'username': username, 'role': role}
        
        except Exception as e:
            print (f"error': 'Gagal mendaftarkan user: {str(e)}")
            return {"error': 'Gagal mendaftarkan user: {str(e)}"}

class MenuManager:
    def __init__(self, db):
        self.db = db
    
    def get_all_menu(self):
        return self.db.query('SELECT * FROM menu')
    
    def get_formatted_menu(self):
        menu = self.get_all_menu()
        return [{"id": item[0], "name": item[1], "price": item[2], 
                "stock": item[3], "image": item[4]} for item in menu]

    def update_stock(self, name, quantity):
        self.db.query('UPDATE menu SET stock = stock - ? WHERE name = ?', 
                     [quantity, name])

    def check_stock(self, name, quantity):
        menu_item = self.db.query('SELECT stock FROM menu WHERE name = ?', 
                                 [name], one=True)
        return menu_item and menu_item[0] >= quantity

class OrderManager:
    def __init__(self, db):
        self.db = db
    
    def add_order(self, menu_name, quantity, total_price, username):
        self.db.query('INSERT INTO orders(menu_name, quantity, total_price, username) VALUES (?, ?, ?, ?)', 
                     [menu_name, quantity, total_price, username])
        
    def process_cart(self, cart_data, username):
        try:
            for item in cart_data:
                menu_name = item['name']
                quantity = item['jumlah']
                price = item['harga']
                total_price = price * quantity
                
                self.db.query('UPDATE menu SET stock = stock - ? WHERE name = ?', 
                             [quantity, menu_name])
                self.add_order(menu_name, quantity, total_price, username)
            return {"message": "Pesanan berhasil ditambahkan!"}, 200
        except Exception as e:
            print(f"Error: {e}")
            return {"error": "Gagal mencatat pesanan. Mohon coba lagi."}, 400

class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__, static_folder='static')
        self.app.secret_key = "Algoritma"
        self.init_dependencies()
        self.init_routes()

    def init_dependencies(self):
        self.db = Database()
        self.auth = Auth(self.db)
        self.menu = MenuManager(self.db)
        self.order = OrderManager(self.db)
        
    def init_routes(self):
        self.app.add_url_rule('/register', 'register', self.register, methods=['GET', 'POST'])
        self.app.add_url_rule('/login', 'login', self.login, methods=['GET', 'POST'])
        self.app.add_url_rule('/logout', 'logout', self.logout)
        self.app.add_url_rule('/', 'homepage', self.homepage)
        self.app.add_url_rule('/menu', 'menu', self.menu_page)
        self.app.add_url_rule('/admin_menu', 'admin_menu', self.admin_menu)
        self.app.add_url_rule('/about', 'about', self.about)
        
        # Rute buat API
        self.app.add_url_rule('/api/menu', 'api_get_menu', self.api_get_menu)
        self.app.add_url_rule('/api/add_order', 'api_add_order', self.api_add_order, methods=['POST'])
        self.app.add_url_rule('/add_to_cart', 'add_to_cart', self.add_to_cart, methods=['POST'])
        self.app.add_url_rule('/api/update_stock', 'api_update_stock', self.api_update_stock, methods=['POST'])
    
    def register(self):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            if password != confirm_password:
                return render_template('register.html', error='Password dan Konfirmasi password tidak sama!')
            
            result = self.auth.register(username, password)

            if 'error' in result:
                return render_template('register.html', error=result['error'])
            
            print(f"Registration successful for user: {username}")
            return redirect(url_for('login'))
        
        return render_template('register.html')
    
    def login(self):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = self.auth.login(username, password)
            if user:
                session['username'] = user['username']
                session['role'] = user['role']
                return redirect(url_for('homepage'))
            return render_template('login.html', error="Username atau Password Salah!")
        return render_template('login.html')
    
    def logout(self):
        session.clear()
        return redirect(url_for('login'))
    
    def homepage(self):
        if not self.auth.check_auth():
            return redirect(url_for('login'))
        return render_template('homepage.html', 
                             username=session['username'], 
                             role=session['role'])
    
    def menu_page(self):
        if not self.auth.check_auth():
            return redirect(url_for('login'))
        elif session['role'] == 'admin':
            return redirect(url_for('admin_menu'))
        return render_template('menu.html', menu=self.menu.get_all_menu())
    
    def admin_menu(self):
        if not self.auth.check_auth() or session['role'] != 'admin':
            return redirect(url_for('login'))
        return render_template('admin_menu.html', menu=self.menu.get_all_menu())
    
    def about(self):
        if not self.auth.check_auth():
            return redirect(url_for('login'))
        return render_template('about.html', 
                             username=session['username'], 
                             role=session['role'])

    def api_get_menu(self):
        menu_list = self.menu.get_formatted_menu()
        return jsonify({"menu": menu_list})

    def api_add_order(self):
        if not self.auth.check_auth():
            return jsonify({"error": "Unauthorized"}), 401
        
        try:
            data = request.json
            print(f"Data yang diterima: {data}")
            result = self.order.process_cart(data['cart'], session['username'])
            return jsonify(result[0]), result[1]
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Gagal mencatat pesanan. Mohon coba lagi."}), 400

    def add_to_cart(self):
        if not self.auth.check_auth():
            return redirect(url_for('login'))
        
        try:
            data = request.get_json()
            for item in data:
                if not self.menu.check_stock(item['name'], item['jumlah']):
                    return jsonify({"message": f"Stock {item['name']} tidak cukup!"}), 400
                
                self.menu.update_stock(item['name'], item['jumlah'])
                self.order.add_order(
                    item['name'], 
                    item['jumlah'], 
                    item['harga'], 
                    session['username']
                )
            return jsonify({"message": "Pesanan berhasil ditambahkan!"})
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)}), 400

    def api_update_stock(self):
        try:
            data = request.json
            print(data)
            for item in data['cart']:
                self.menu.update_stock(item['name'], item['jumlah'])
            return jsonify({"message": "Success"}), 200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Terjadi kesalahan saat memproses permintaan"}), 400

    def run(self):
        self.app.run(debug=True)

if __name__ == "__main__":
    app = FlaskApp()
    app.run()