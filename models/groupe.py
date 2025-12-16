import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from database import db
from .user import User

class Groupe:
    def __init__(self, id: str, nom: str, admin_id: str, created_at: Optional[str] = None):
        self.id = id
        self.nom = nom
        self.admin_id = admin_id
        self.created_at = created_at or datetime.now().isoformat()
    
    @staticmethod
    def create(nom: str, admin_id: str) -> 'Groupe':
        groupe_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO groupe (id, nom, admin_id, created_at) VALUES (?, ?, ?, ?)',
                (groupe_id, nom, admin_id, created_at)
            )
            # Ajouter l'admin comme membre du groupe
            cursor.execute(
                'INSERT INTO membre (user_id, groupe_id) VALUES (?, ?)',
                (admin_id, groupe_id)
            )
            return Groupe(groupe_id, nom, admin_id, created_at)
    
    @staticmethod
    def get_by_id(groupe_id: str) -> Optional['Groupe']:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, nom, admin_id, created_at FROM groupe WHERE id = ?',
                (groupe_id,)
            )
            row = cursor.fetchone()
            if row:
                return Groupe(*row)
            return None
    
    @staticmethod
    def get_by_user(user_id: str) -> List['Groupe']:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT g.id, g.nom, g.admin_id, g.created_at
                FROM groupe g
                JOIN membre m ON g.id = m.groupe_id
                WHERE m.user_id = ?
            ''', (user_id,))
            return [Groupe(*row) for row in cursor.fetchall()]
    
    def add_member(self, user_id: str, added_by: str) -> bool:
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
            except:
                return False
    
    def remove_member(self, user_id: str, removed_by: str) -> bool:
        if self.admin_id != removed_by or user_id == self.admin_id:
            return False
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM membre WHERE user_id = ? AND groupe_id = ?',
                (user_id, self.id)
            )
            return cursor.rowcount > 0
    
    def add_password(self, password_id: str, added_by: str) -> bool:
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
            except:
                return False
    
    def get_members(self) -> List[Dict[str, Any]]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.nom, u.prenom, u.mail,
                       CASE WHEN u.id = ? THEN 1 ELSE 0 END as is_admin
                FROM app_user u
                JOIN membre m ON u.id = m.user_id
                WHERE m.groupe_id = ?
            ''', (self.admin_id, self.id))
            return [{
                'id': row[0],
                'nom': row[1],
                'prenom': row[2],
                'mail': row[3],
                'is_admin': bool(row[4])
            } for row in cursor.fetchall()]
    
    def get_passwords(self) -> List[Dict[str, Any]]:
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
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'nom': self.nom,
            'admin_id': self.admin_id,
            'member_count': len(self.get_members())
        }
