import sqlite3
from typing import Optional
import os

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: str = 'password_manager.db'):
        if not self._initialized:
            self.db_path = db_path
            self._create_tables()
            self._initialized = True
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def _create_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Supprimer les tables si elles existent déjà
            cursor.executescript('''
                DROP TABLE IF EXISTS grp_pwd;
                DROP TABLE IF EXISTS user_pwd;
                DROP TABLE IF EXISTS membre;
                DROP TABLE IF EXISTS password;
                DROP TABLE IF EXISTS groupe;
                DROP TABLE IF EXISTS app_user;
            ''')
            
            # Table utilisateur
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_user (
                id TEXT PRIMARY KEY,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                mail TEXT UNIQUE NOT NULL,
                mdp_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Table groupe
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS groupe (
                id TEXT PRIMARY KEY,
                nom TEXT NOT NULL,
                admin_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES app_user(id) ON DELETE CASCADE
            )
            ''')
            
            # Table mot de passe
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS password (
                id TEXT PRIMARY KEY,
                valeur_chiffree TEXT NOT NULL,
                intitule TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES app_user(id) ON DELETE CASCADE
            )
            ''')
            
            # Table membre (user <-> groupe)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS membre (
                user_id TEXT,
                groupe_id TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, groupe_id),
                FOREIGN KEY (user_id) REFERENCES app_user(id) ON DELETE CASCADE,
                FOREIGN KEY (groupe_id) REFERENCES groupe(id) ON DELETE CASCADE
            )
            ''')
            
            # Table user_pwd (user <-> password)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_pwd (
                user_id TEXT,
                password_id TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, password_id),
                FOREIGN KEY (user_id) REFERENCES app_user(id) ON DELETE CASCADE,
                FOREIGN KEY (password_id) REFERENCES password(id) ON DELETE CASCADE
            )
            ''')
            
            # Table grp_pwd (groupe <-> password)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS grp_pwd (
                groupe_id TEXT,
                password_id TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (groupe_id, password_id),
                FOREIGN KEY (groupe_id) REFERENCES groupe(id) ON DELETE CASCADE,
                FOREIGN KEY (password_id) REFERENCES password(id) ON DELETE CASCADE
            )
            ''')
            
            conn.commit()

# Instance unique de la base de données
db = Database()
