import uuid
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from database import Model, db
from .user import User

class Groupe(Model):
    def __init__(self, id: str, nom: str, admin_id: str, created_at: Optional[str] = None):
        super().__init__()
        self.id = id
        self.nom = nom
        self.admin_id = admin_id
        self.created_at = created_at or datetime.now().isoformat()
    
    @classmethod
    def create(cls, nom: str, admin_id: str) -> 'Groupe':
        """Crée un nouveau groupe"""
        groupe_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        # Création du groupe
        super().query_insert(
            'INSERT INTO groupe (id, nom, admin_id, created_at) VALUES (?, ?, ?, ?)',
            (groupe_id, nom, admin_id, created_at)
        )
        
        # Ajout de l'admin comme membre du groupe
        super().query_insert(
            'INSERT INTO membre (user_id, groupe_id) VALUES (?, ?)',
            (admin_id, groupe_id)
        )
        
        return cls(groupe_id, nom, admin_id, created_at)
    
    @classmethod
    def get_by_id(cls, groupe_id: str) -> Optional['Groupe']:
        """Récupère un groupe par son ID"""
        row = super().query_one(
            'SELECT id, nom, admin_id, created_at FROM groupe WHERE id = ?',
            (groupe_id,)
        )
        if row:
            return cls(*row)
        return None
    
    @classmethod
    def get_by_user(cls, user_id: str) -> List['Groupe']:
        """Récupère tous les groupes d'un utilisateur"""
        rows = super().query_many('''
            SELECT g.id, g.nom, g.admin_id, g.created_at
            FROM groupe g
            JOIN membre m ON g.id = m.groupe_id
            WHERE m.user_id = ?
        ''', (user_id,))
        return [cls(*row) for row in rows]
    
    def add_member_by_email(self, email: str, added_by: str) -> dict:
        """
        Ajoute un utilisateur au groupe en utilisant son email
        Retourne un dictionnaire avec 'success' et 'message'
        """
        if self.admin_id != added_by:
            return {'success': False, 'message': "Seul l'administrateur peut ajouter des membres"}
            
        # Récupérer l'utilisateur par son email
        user = User.get_by_email(email)
        if not user:
            return {'success': False, 'message': f"Aucun utilisateur trouvé avec l'email {email}"}
            
        # Vérifier si l'utilisateur est déjà membre du groupe
        existing_member = super().query_one(
            'SELECT 1 FROM membre WHERE user_id = ? AND groupe_id = ?',
            (user.id, self.id)
        )
        if existing_member:
            return {'success': False, 'message': "Cet utilisateur est déjà membre du groupe"}
        
        # Ajouter l'utilisateur au groupe
        try:
            super().query_insert(
                'INSERT INTO membre (user_id, groupe_id) VALUES (?, ?)',
                (user.id, self.id)
            )
            return {
                'success': True,
                'message': f"Utilisateur {email} ajouté avec succès au groupe"
            }
        except Exception as e:
            return {'success': False, 'message': f"Erreur lors de l'ajout au groupe : {str(e)}"}
    
    # Conserver l'ancienne méthode pour compatibilité
    def add_member(self, user_id: str, added_by: str) -> bool:
        """Ancienne méthode, à éviter d'utiliser directement"""
        result = self.add_member_by_email(user_id, added_by)
        return result['success']
    
    def remove_member(self, user_id: str, removed_by: str) -> bool:
        """Supprime un membre du groupe"""
        if self.admin_id != removed_by or user_id == self.admin_id:
            return False
        
        super().query_delete(
            'DELETE FROM membre WHERE user_id = ? AND groupe_id = ?',
            (user_id, self.id)
        )
        return True
    
    def add_password(self, password_id: str, added_by: str) -> bool:
        """Ajoute un mot de passe au groupe"""
        if self.admin_id != added_by:
            return False
        
        try:
            super().query_insert(
                'INSERT INTO grp_pwd (groupe_id, password_id) VALUES (?, ?)',
                (self.id, password_id)
            )
            return True
        except Exception:
            return False
    
    def get_members(self) -> List[Dict[str, Any]]:
        """Récupère tous les membres du groupe"""
        rows = super().query_many('''
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
        } for row in rows]
    
    def get_passwords(self) -> List[Dict[str, Any]]:
        """Récupère tous les mots de passe du groupe"""
        rows = super().query_many('''
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
        } for row in rows]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le groupe en dictionnaire"""
        return {
            'id': self.id,
            'nom': self.nom,
            'admin_id': self.admin_id,
            'created_at': self.created_at,
            'member_count': len(self.get_members())
        }
