import secrets
import string
import uuid
from datetime import datetime
from typing import Dict, Optional, List, Any
from database import db

class Password:
    @staticmethod
    def generate(length: int = 16) -> str:
        """Génère un mot de passe aléatoire"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def create(intitule: str, valeur: str, user_id: str, groupe_id: str = None) -> str:
        """Crée un nouveau mot de passe et le lie à un utilisateur ou un groupe"""
        password_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO password (id, valeur_chiffree, intitule, created_by, created_at) VALUES (?, ?, ?, ?, ?)',
                (password_id, valeur, intitule, user_id, created_at)
            )
            
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
    def get_by_id(password_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un mot de passe par son ID si l'utilisateur y a accès"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, p.intitule, p.valeur_chiffree, p.created_at, u.nom, u.prenom, p.created_by
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
    
    @staticmethod
    def delete(password_id: str, user_id: str) -> bool:
        """Supprime un mot de passe si l'utilisateur en est le propriétaire"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            # Vérifier si l'utilisateur est le créateur du mot de passe
            cursor.execute(
                'SELECT created_by FROM password WHERE id = ?',
                (password_id,)
            )
            result = cursor.fetchone()
            
            if not result or result[0] != user_id:
                return False
            
            # Supprimer les références dans les tables de liaison
            cursor.execute('DELETE FROM user_pwd WHERE password_id = ?', (password_id,))
            cursor.execute('DELETE FROM grp_pwd WHERE password_id = ?', (password_id,))
            
            # Supprimer le mot de passe
            cursor.execute('DELETE FROM password WHERE id = ?', (password_id,))
            
            return cursor.rowcount > 0
            
    @staticmethod
    def get_user_passwords(user_id: str) -> List[Dict[str, Any]]:
        """Récupère tous les mots de passe d'un utilisateur"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, p.intitule, p.valeur_chiffree, p.created_at, u.nom, u.prenom
                FROM password p
                JOIN user_pwd up ON p.id = up.password_id
                JOIN app_user u ON p.created_by = u.id
                WHERE up.user_id = ?
                ORDER BY p.created_at DESC
            ''', (user_id,))
            return [{
                'id': row[0],
                'intitule': row[1],
                'valeur': row[2],
                'created_at': row[3],
                'created_by': f"{row[4]} {row[5]}"
            } for row in cursor.fetchall()]
