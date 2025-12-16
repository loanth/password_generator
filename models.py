from typing import List, Optional
import sqlite3
import hashlib
import secrets
import string
from database import db

class User:
    def __init__(self, id: int, nom: str, prenom: str, mail: str, mdp_hash: str):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.mail = mail
        self.mdp_hash = mdp_hash
    
    @staticmethod
    def create(nom: str, prenom: str, mail: str, mdp: str) -> 'User':
        mdp_hash = hashlib.sha256(mdp.encode()).hexdigest()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO app_user (nom, prenom, mail, mdp_hash) VALUES (?, ?, ?, ?)',
                (nom, prenom, mail, mdp_hash)
            )
            user_id = cursor.lastrowid
            return User(user_id, nom, prenom, mail, mdp_hash)
    
    @staticmethod
    def get_by_credentials(mail: str, mdp: str) -> Optional['User']:
        mdp_hash = hashlib.sha256(mdp.encode()).hexdigest()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, nom, prenom, mail, mdp_hash FROM app_user WHERE mail = ? AND mdp_hash = ?',
                (mail, mdp_hash)
            )
            row = cursor.fetchone()
            if row:
                return User(*row)
            return None
    
    def get_passwords(self) -> List[dict]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, p.intitule, p.valeur_chiffree, p.created_at 
                FROM password p
                JOIN user_pwd up ON p.id = up.password_id
                WHERE up.user_id = ?
            ''', (self.id,))
            return [{'id': row[0], 'intitule': row[1], 'valeur': row[2], 'created_at': row[3]} for row in cursor.fetchall()]


class Groupe:
    def __init__(self, id: int, nom: str, admin_id: int):
        self.id = id
        self.nom = nom
        self.admin_id = admin_id
    
    @staticmethod
    def create(nom: str, admin_id: int) -> 'Groupe':
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO groupe (nom, admin_id) VALUES (?, ?)',
                (nom, admin_id)
            )
            groupe_id = cursor.lastrowid
            # Ajouter l'admin comme membre du groupe
            cursor.execute(
                'INSERT INTO membre (user_id, groupe_id) VALUES (?, ?)',
                (admin_id, groupe_id)
            )
            return Groupe(groupe_id, nom, admin_id)
    
    @staticmethod
    def get_by_user(user_id: int) -> List['Groupe']:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT g.id, g.nom, g.admin_id 
                FROM groupe g
                JOIN membre m ON g.id = m.groupe_id
                WHERE m.user_id = ?
            ''', (user_id,))
            return [Groupe(*row) for row in cursor.fetchall()]
    
    def add_member(self, user_id: int, added_by: int) -> bool:
        if self.admin_id != added_by:
            return False
        
        with db.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO membre (user_id, groupe_id) VALUES (?, ?)',
                    (user_id, self.id)
                )
                return True
            except sqlite3.IntegrityError:
                return False
    
    def remove_member(self, user_id: int, removed_by: int) -> bool:
        if self.admin_id != removed_by or user_id == self.admin_id:
            return False
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM membre WHERE user_id = ? AND groupe_id = ?',
                (user_id, self.id)
            )
            return cursor.rowcount > 0
    
    def add_password(self, password_id: int, added_by: int) -> bool:
        if self.admin_id != added_by:
            return False
        
        with db.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO grp_pwd (groupe_id, password_id) VALUES (?, ?)',
                    (self.id, password_id)
                )
                return True
            except sqlite3.IntegrityError:
                return False
    
    def get_passwords(self) -> List[dict]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, p.intitule, p.valeur_chiffree, p.created_at, u.nom, u.prenom
                FROM password p
                JOIN grp_pwd gp ON p.id = gp.password_id
                JOIN app_user u ON p.created_by = u.id
                WHERE gp.groupe_id = ?
            ''', (self.id,))
            return [{
                'id': row[0], 
                'intitule': row[1], 
                'valeur': row[2], 
                'created_at': row[3],
                'created_by': f"{row[4]} {row[5]}"
            } for row in cursor.fetchall()]


class Password:
    @staticmethod
    def generate(length: int = 16) -> str:
        """Génère un mot de passe aléatoire"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def create(intitule: str, valeur: str, user_id: int, groupe_id: int = None) -> int:
        """Crée un nouveau mot de passe et le lie à un utilisateur ou un groupe"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO password (valeur_chiffree, intitule, created_by) VALUES (?, ?, ?)',
                (valeur, intitule, user_id)
            )
            password_id = cursor.lastrowid
            
            if groupe_id:
                cursor.execute(
                    'INSERT INTO grp_pwd (groupe_id, password_id) VALUES (?, ?)',
                    (groupe_id, password_id)
                )
            else:
                cursor.execute(
                    'INSERT INTO user_pwd (user_id, password_id) VALUES (?, ?)',
                    (user_id, password_id)
                )
            
            return password_id
    
    @staticmethod
    def get_by_id(password_id: int, user_id: int) -> Optional[dict]:
        """Récupère un mot de passe par son ID si l'utilisateur y a accès"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            # Vérifier si l'utilisateur a accès au mot de passe directement ou via un groupe
            cursor.execute('''
                SELECT p.id, p.intitule, p.valeur_chiffree, p.created_at, u.nom, u.prenom
                FROM password p
                LEFT JOIN user_pwd up ON p.id = up.password_id
                LEFT JOIN grp_pwd gp ON p.id = gp.password_id
                LEFT JOIN membre m ON gp.groupe_id = m.groupe_id
                JOIN app_user u ON p.created_by = u.id
                WHERE p.id = ? AND (up.user_id = ? OR m.user_id = ? OR p.created_by = ?)
            ''', (password_id, user_id, user_id, user_id))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'intitule': row[1],
                    'valeur': row[2],
                    'created_at': row[3],
                    'created_by': f"{row[4]} {row[5]}"
                }
            return None
