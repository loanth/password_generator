import sqlite3
from typing import Any, List, Optional, Tuple, TypeVar, Generic, Type
from database import db

T = TypeVar('T')

class Model:
    """Classe de base pour tous les modèles"""
    
    @classmethod
    def open_database(cls) -> sqlite3.Connection:
        """Ouvre une connexion à la base de données"""
        return db.get_connection()
    
    @classmethod
    def close_database(cls, conn: sqlite3.Connection) -> None:
        """Ferme la connexion à la base de données"""
        if conn:
            conn.close()
    
    @classmethod
    def query_insert(cls, query: str, params: tuple = ()) -> int:
        """Exécute une requête INSERT et retourne l'ID du dernier élément inséré"""
        conn = cls.open_database()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            cls.close_database(conn)
    
    @classmethod
    def query_update(cls, query: str, params: tuple = ()) -> None:
        """Exécute une requête UPDATE"""
        conn = cls.open_database()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
        finally:
            cls.close_database(conn)
    
    @classmethod
    def query_delete(cls, query: str, params: tuple = ()) -> None:
        """Exécute une requête DELETE"""
        conn = cls.open_database()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
        finally:
            cls.close_database(conn)
    
    @classmethod
    def query_one(cls, query: str, params: tuple = ()) -> Optional[Tuple]:
        """Exécute une requête et retourne un seul résultat"""
        conn = cls.open_database()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        finally:
            cls.close_database(conn)
    
    @classmethod
    def query_many(cls, query: str, params: tuple = ()) -> List[Tuple]:
        """Exécute une requête et retourne plusieurs résultats"""
        conn = cls.open_database()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        finally:
            cls.close_database(conn)

# Imports des modèles
from .user import User
from .groupe import Groupe
from .password import Password

# Expose les modèles pour une importation plus facile
__all__ = ['User', 'Groupe', 'Password']
