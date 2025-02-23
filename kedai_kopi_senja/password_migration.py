import sqlite3
import hashlib

class DbManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def close_connection(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def fetch_users(self):
        self.cursor.execute('SELECT * FROM users')
        return self.cursor.fetchall()

    def update_password(self, user_id, hashed_password):
        self.cursor.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_password, user_id))

class PasswordConverter:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def convert_password(self):
        try:
            self.db_manager.connect()
            users =  self.db_manager.fetch_users()

            for user in users:
                user_id = user[0]
                password = user[2]

                if len(password) != 64:
                    hashed_password = self.hash_password(password)
                    self.db_manager.update_password(user_id, hashed_password)
                    print(f"Convert password untuk users : {user[1]}")
            print("Convert password berhasil!")
        
        except  sqlite3.Error as e:
            print(f"Database Error : {e}")
        except Exception as e:
            print(f"Unxexpected Error : {e}")
        finally:
            self.db_manager.close_connection()

if __name__ == "__main__":
    db_manager = DbManager('database.db')
    converter = PasswordConverter(db_manager)
    converter.convert_password()