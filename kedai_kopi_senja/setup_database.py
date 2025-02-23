import sqlite3

class DatabaseSetup:
    def __init__(self, db_name='database.db'):
        self.db_name = db_name
    
    def connect(self):
        #Buka koneksi database
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
    
    def close_connection(self):
        #Tutup koneksi dari database
        self.conn.commit()
        self.conn.close()
    
    def reset_table(self):
        #hapus tabel lama kalo ada perubahan (matiin aja method ini kalo datanya gak mau diganti)
        self.cursor.execute('DROP TABLE IF EXISTS menu')
        self.cursor.execute('DROP TABLE IF EXISTS orders')
        self.cursor.execute('DROP TABLE IF EXISTS users')

    def create_table(self):
        #Bikin tabel baru di database
        self.cursor.execute(''' CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            price INTEGER NOT NULL,
            stock INTEGER NOT NULL,
            image TEXT NOT NULL
            )
        ''')

        self.cursor.execute(''' CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            menu_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total_price INTEGER NOT NULL,
            username TEXT NOT NULL 
            )
        ''')

        self.cursor.execute(''' CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('admin', 'user'))
            )
        ''')

    def insert_menu_data(self):
        #Ngisi data ke database
        menu_data = [
            ("Espresso", 20000, 6, "/static/images/espresso.png"),
            ("Cappuccino", 25000, 5, "/static/images/cappuccino.jpg"),
            ("Latte", 20000, 12, "/static/images/latte.jpg"),
            ("Mocha", 30000, 20, "/static/images/mocha.jpg"),
            ("Americano", 22000, 25, "/static/images/americano.png"),
            ("Macchiato", 35000, 15, "/static/images/macchiato.jpg"),
            ("Doppio", 28000, 10, "/static/images/doppio.jpg")
        ]

        for name, price, stock, image, in menu_data:
            self.cursor.execute('SELECT * FROM menu WHERE name = ?', (name,))
            existing_data = self.cursor.fetchone()

            if existing_data:
                self.cursor.execute(''' UPDATE menu SET price = ?, stock = stock + ?, image = ? WHERE name = ?
                    ''', (price, stock, image, name))

            else:
                self.cursor.execute(''' INSERT INTO menu (name, price, stock, image) VALUES (?, ?, ?, ?)
                    ''', (name, price, stock, image))
    
    def insert_user_data(self):
        #Bikin data user atau admin buat login

        self.cursor.execute('DELETE FROM users')
        self.cursor.executemany(''' INSERT INTO users (username, password, role) VALUES (?, ?, ?) ''',
            [
                ("admin", "admin11", "admin"),
                ("bayu", "bayu11", "admin"),
                ("ren", "ren11", "user"),
                ("stelle", "stelle11", "user"),
                ("caelus", "caelus11", "user"),
                ("march7", "march11", "user"),
            ])

    def setup_database(self):
        #panggil  semua object buat bikin databasenya
        self.connect()
        self.reset_table()
        self.create_table()
        self.insert_menu_data()
        self.insert_user_data()
        self.close_connection()
        print("Database berhasil di update!")
    
if __name__ == "__main__":
    db_setup = DatabaseSetup()
    db_setup.setup_database()