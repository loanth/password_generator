import hashlib
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from database import db

class User:
    def __init__(self, id: str, nom: str, prenom: str, mail: str, mdp_hash: str, created_at: Optional[str] = None):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.mail = mail
        self.mdp_hash = mdp_hash
        self.created_at = created_at or datetime.now().isoformat()
    
    @staticmethod
    def create(nom: str, prenom: str, mail: str, mdp: str) -> 'User':
        user_id = str(uuid.uuid4())
        mdp_hash = hashlib.sha256(mdp.encode()).hexdigest()
        created_at = datetime.now().isoformat()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO app_user (id, nom, prenom, mail, mdp_hash, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                (user_id, nom, prenom, mail, mdp_hash, created_at)
            )
            return User(user_id, nom, prenom, mail, mdp_hash, created_at)
    
    @staticmethod
    def get_by_credentials(mail: str, mdp: str) -> Optional['User']:
        mdp_hash = hashlib.sha256(mdp.encode()).hexdigest()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, nom, prenom, mail, mdp_hash, created_at FROM app_user WHERE mail = ? AND mdp_hash = ?',
                (mail, mdp_hash)
            )
            row = cursor.fetchone()
            if row:
                return User(*row)
            return None
    
    def get_passwords(self) -> List[Dict[str, Any]]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, p.intitule, p.valeur_chiffree, p.created_at 
                FROM password p
                JOIN user_pwd up ON p.id = up.password_id
                WHERE up.user_id = ?
            ''', (self.id,))
            return [{'id': row[0], 'intitule': row[1], 'valeur': row[2], 'created_at': row[3]} for row in cursor.fetchall()]
    
    @staticmethod
    def get_by_id(user_id: str) -> Optional['User']:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, nom, prenom, mail, mdp_hash, created_at FROM app_user WHERE id = ?',
                (user_id,)
            )
            row = cursor.fetchone()
            if row:
                return User(*row)
            return None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'mail': self.mail
        }
