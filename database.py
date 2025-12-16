import sqlite3
from typing import Optional, List, Tuple, Any, Type, TypeVar, Dict
import os

T = TypeVar('T', bound='Model')

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
    
    def open_database(self) -> sqlite3.Connection:
        """Ouvre une connexion à la base de données"""
        return sqlite3.connect(self.db_path)
    
    def close_database(self, conn: sqlite3.Connection) -> None:
        """Ferme la connexion à la base de données"""
        if conn:
            conn.close()
    
    def query_insert(self, query: str, params: tuple = ()) -> int:
        """Exécute une requête INSERT et retourne l'ID du dernier élément inséré"""
        conn = self.open_database()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            self.close_database(conn)
    
    def query_update(self, query: str, params: tuple = ()) -> None:
        """Exécute une requête UPDATE"""
        conn = self.open_database()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
        finally:
            self.close_database(conn)
    
    def query_delete(self, query: str, params: tuple = ()) -> None:
        """Exécute une requête DELETE"""
        conn = self.open_database()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
        finally:
            self.close_database(conn)
    
    def query_one(self, query: str, params: tuple = (), model_class: Type[T] = None) -> Optional[T]:
        """Exécute une requête et retourne un seul résultat"""
        conn = self.open_database()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row and model_class:
                return model_class(*row)
            return row
        finally:
            self.close_database(conn)
    
    def query_many(self, query: str, params: tuple = (), model_class: Type[T] = None) -> List[T]:
        """Exécute une requête et retourne plusieurs résultats"""
        conn = self.open_database()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            if model_class and rows:
                return [model_class(*row) for row in rows]
            return rows
        finally:
            self.close_database(conn)
    
    def _create_tables(self):
        with self.open_database() as conn:
            cursor = conn.cursor()
            
            # Table utilisateur
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_user (
                    id TEXT PRIMARY KEY,
                    nom TEXT NOT NULL,
                    prenom TEXT NOT NULL,
                    mail TEXT UNIQUE NOT NULL,
                    mdp_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # Table groupe
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS groupe (
                    id TEXT PRIMARY KEY,
                    nom TEXT NOT NULL,
                    admin_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (admin_id) REFERENCES app_user(id)
                )
            ''')
            
            # Table membre (relation many-to-many entre utilisateur et groupe)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS membre (
                    user_id TEXT,
                    groupe_id TEXT,
                    PRIMARY KEY (user_id, groupe_id),
                    FOREIGN KEY (user_id) REFERENCES app_user(id),
                    FOREIGN KEY (groupe_id) REFERENCES groupe(id)
                )
            ''')
            
            # Table mot de passe
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS password (
                    id TEXT PRIMARY KEY,
                    intitule TEXT NOT NULL,
                    valeur_chiffree TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (created_by) REFERENCES app_user(id)
                )
            ''')
            
            # Table de liaison groupe-mot de passe (many-to-many)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS grp_pwd (
                    groupe_id TEXT,
                    password_id TEXT,
                    PRIMARY KEY (groupe_id, password_id),
                    FOREIGN KEY (groupe_id) REFERENCES groupe(id),
                    FOREIGN KEY (password_id) REFERENCES password(id)
                )
            ''')
            
            conn.commit()
    
    # Alias pour la rétrocompatibilité
    get_connection = open_database

# Instance globale de la base de données
db = Database()

class Model:
    """Classe de base pour tous les modèles"""
    
    @classmethod
    def _get_db(cls) -> Database:
        """Retourne l'instance de la base de données"""
        return db
    
    @classmethod
    def query_one(cls, query: str, params: tuple = ()) -> Optional[Tuple]:
        """Exécute une requête et retourne un seul résultat"""
        return cls._get_db().query_one(query, params)
    
    @classmethod
    def query_many(cls, query: str, params: tuple = ()) -> List[Tuple]:
        """Exécute une requête et retourne plusieurs résultats"""
        return cls._get_db().query_many(query, params)
    
    @classmethod
    def query_insert(cls, query: str, params: tuple = ()) -> int:
        """Exécute une requête INSERT et retourne l'ID du dernier élément inséré"""
        return cls._get_db().query_insert(query, params)
    
    @classmethod
    def query_update(cls, query: str, params: tuple = ()) -> None:
        """Exécute une requête UPDATE"""
        cls._get_db().query_update(query, params)
    
    @classmethod
    def query_delete(cls, query: str, params: tuple = ()) -> None:
        """Exécute une requête DELETE"""
        cls._get_db().query_delete(query, params)
