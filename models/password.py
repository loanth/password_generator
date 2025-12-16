import secrets
import string
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from database import Model, db

class Password(Model):
    def __init__(self, id: str, intitule: str, valeur_chiffree: str, created_by: str, created_at: str):
        super().__init__()
        self.id = id
        self.intitule = intitule
        self.valeur_chiffree = valeur_chiffree
        self.created_by = created_by
        self.created_at = created_at
    
    @staticmethod
    def generate(length: int = 16) -> str:
        """Génère un mot de passe aléatoire"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @classmethod
    def create(cls, intitule: str, valeur: str, created_by: str) -> 'Password':
        """Crée un nouveau mot de passe"""
        password_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        # Création du mot de passe
        super().query_insert(
            'INSERT INTO password (id, intitule, valeur_chiffree, created_by, created_at) VALUES (?, ?, ?, ?, ?)',
            (password_id, intitule, valeur, created_by, created_at)
        )

        # Ajout du mot de passe à l'utilisateur qui l'a créé
        super().query_insert(
            'INSERT INTO user_pwd (user_id, password_id) VALUES (?, ?)',
            (created_by, password_id)
        )

        return cls(password_id, intitule, valeur, created_by, created_at)

    def delete(self, deleted_by: str) -> bool:
        """Supprime le mot de passe"""
        # Vérifier que la personne qui supprime est le créateur
        if self.created_by != deleted_by:
            return False

        # Supprimer les entrées de partage
        super().query_delete('DELETE FROM user_pwd WHERE password_id = ?', (self.id,))
        super().query_delete('DELETE FROM grp_pwd WHERE password_id = ?', (self.id,))

        # Supprimer le mot de passe
        super().query_delete('DELETE FROM password WHERE id = ?', (self.id,))
        return True

    def share_with_user(self, user_id: str, shared_by: str) -> bool:
        """Partage le mot de passe avec un autre utilisateur"""
        # Vérifier que la personne qui partage a accès au mot de passe
        has_access = super().query_one(
            'SELECT 1 FROM user_pwd WHERE user_id = ? AND password_id = ?',
            (shared_by, self.id)
        )
        if not has_access:
            return False

        # Vérifier si l'utilisateur a déjà accès
        already_shared = super().query_one(
            'SELECT 1 FROM user_pwd WHERE user_id = ? AND password_id = ?',
            (user_id, self.id)
        )
        if already_shared:
            return True

        # Partager le mot de passe
        super().query_insert(
            'INSERT INTO user_pwd (user_id, password_id) VALUES (?, ?)',
            (user_id, self.id)
        )
        return True

    @classmethod
    def get_by_id(cls, password_id: str) -> Optional['Password']:
        """Récupère un mot de passe par son ID"""
        row = super().query_one(
            'SELECT id, intitule, valeur_chiffree, created_by, created_at FROM password WHERE id = ?',
            (password_id,)
        )
        if row:
            return cls(*row)
        return None

    @classmethod
    def get_by_user(cls, user_id: str) -> List['Password']:
        """Récupère tous les mots de passe d'un utilisateur"""
        rows = super().query_many('''
            SELECT p.id, p.intitule, p.valeur_chiffree, p.created_by, p.created_at
            FROM password p
            JOIN user_pwd up ON p.id = up.password_id
            WHERE up.user_id = ?
        ''', (user_id,))
        return [cls(*row) for row in rows]

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le mot de passe en dictionnaire"""
        return {
            'id': self.id,
            'intitule': self.intitule,
            'valeur': self.valeur_chiffree,
            'created_by': self.created_by,
            'created_at': self.created_at
        }
