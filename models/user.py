import hashlib
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from database import Model

class User(Model):
    def __init__(self, id: str, nom: str, prenom: str, mail: str, mdp_hash: str, created_at: Optional[str] = None):
        super().__init__()
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.mail = mail
        self.mdp_hash = mdp_hash
        self.created_at = created_at or datetime.now().isoformat()
    
    @classmethod
    def create(cls, nom: str, prenom: str, mail: str, mdp: str) -> 'User':
        """Crée un nouvel utilisateur"""
        # Vérification de la validité de l'email
        if not cls._is_valid_email(mail):
            raise ValueError("Format d'email invalide")
            
        # Vérification de l'unicité de l'email
        if cls.get_by_email(mail) is not None:
            raise ValueError("Cet email est déjà utilisé")
            
        user_id = str(uuid.uuid4())
        mdp_hash = hashlib.sha256(mdp.encode()).hexdigest()
        created_at = datetime.now().isoformat()
        
        # Utilisation de query_insert de la classe Model via super()
        super().query_insert(
            'INSERT INTO app_user (id, nom, prenom, mail, mdp_hash, created_at) VALUES (?, ?, ?, ?, ?, ?)',
            (user_id, nom, prenom, mail, mdp_hash, created_at)
        )
        
        return cls(user_id, nom, prenom, mail, mdp_hash, created_at)
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Vérifie si l'email est valide"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @classmethod
    def get_by_credentials(cls, mail: str, mdp: str) -> Optional['User']:
        """Récupère un utilisateur par ses identifiants"""
        mdp_hash = hashlib.sha256(mdp.encode()).hexdigest()
        row = super().query_one(
            'SELECT id, nom, prenom, mail, mdp_hash, created_at FROM app_user WHERE mail = ? AND mdp_hash = ?',
            (mail, mdp_hash)
        )
        if row:
            return cls(*row)
        return None
    
    @classmethod
    def get_by_id(cls, user_id: str) -> Optional['User']:
        """Récupère un utilisateur par son ID"""
        row = super().query_one(
            'SELECT id, nom, prenom, mail, mdp_hash, created_at FROM app_user WHERE id = ?',
            (user_id,)
        )
        if row:
            return cls(*row)
        return None
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        """Récupère un utilisateur par son email"""
        row = super().query_one(
            'SELECT id, nom, prenom, mail, mdp_hash, created_at FROM app_user WHERE mail = ?',
            (email,)
        )
        if row:
            return cls(*row)
        return None
    
    def get_passwords(self) -> List[Dict[str, Any]]:
        """Récupère tous les mots de passe de l'utilisateur"""
        rows = super().query_many(
            'SELECT id, intitule, valeur_chiffree, created_at FROM password WHERE created_by = ?',
            (self.id,)
        )
        return [{
            'id': row[0],
            'intitule': row[1],
            'valeur': row[2],
            'created_at': row[3]
        } for row in rows]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'utilisateur en dictionnaire"""
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'mail': self.mail,
            'created_at': self.created_at
        }
