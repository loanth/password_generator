# Documentation de l'API - Gestionnaire de Mots de Passe

## Table des matières
1. [Authentification](#authentification)
   - [Créer un compte](#créer-un-compte)
   - [Se connecter](#se-connecter)

2. [Gestion des Mots de Passe](#gestion-des-mots-de-passe)
   - [Générer un mot de passe](#générer-un-mot-de-passe)
   - [Lister les mots de passe](#lister-les-mots-de-passe)
   - [Créer un mot de passe personnalisé](#créer-un-mot-de-passe-personnalisé)
   - [Supprimer un mot de passe](#supprimer-un-mot-de-passe)

3. [Gestion des Groupes](#gestion-des-groupes)
   - [Créer un groupe](#créer-un-groupe)
   - [Lister les groupes](#lister-les-groupes)
   - [Ajouter un membre à un groupe](#ajouter-un-membre-à-un-groupe)
   - [Retirer un membre d'un groupe](#retirer-un-membre-dun-groupe)
   - [Ajouter un mot de passe à un groupe](#ajouter-un-mot-de-passe-à-un-groupe)
   - [Voir les mots de passe d'un groupe](#voir-les-mots-de-passe-dun-groupe)

## Authentification

### Créer un compte
```python
from models.user import User

try:
    user = User.create(
        nom="Dupont",
        prenom="Jean",
        mail="jean.dupont@example.com",
        mdp="motdepasse123"
    )
    print(f"Utilisateur créé avec l'ID: {user.id}")
except Exception as e:
    print(f"Erreur: {e}")
```

### Se connecter
```python
from models.user import User

user = User.get_by_credentials(
    mail="jean.dupont@example.com",
    mdp="motdepasse123"
)
if user:
    print(f"Connecté en tant que {user.prenom} {user.nom}")
else:
    print("Identifiants invalides")
```

## Gestion des Mots de Passe

### Générer un mot de passe
```python
from models.password import Password

# Génère un mot de passe aléatoire de 16 caractères
password = Password.generate(16)
print(f"Mot de passe généré: {password}")

# Pour l'enregistrer
password_id = Password.create(
    intitule="Compte Google",
    valeur=password,
    created_by=user_id  # ID de l'utilisateur
)
```

### Lister les mots de passe
```python
from models.user import User

user = User.get_by_id(user_id)
passwords = user.get_passwords()
for pwd in passwords:
    print(f"{pwd['intitule']}: {pwd['valeur']}")
```

### Créer un mot de passe personnalisé
```python
from models.password import Password

password_id = Password.create(
    intitule="Compte perso",
    valeur="monMotDePasse123",
    created_by=user_id
)
```

### Supprimer un mot de passe
```python
from models.password import Password

Password.delete(password_id, user_id)  # Vérifie que l'utilisateur est bien le propriétaire
```

## Gestion des Groupes

### Créer un groupe
```python
from models.groupe import Groupe

groupe = Groupe.create(
    nom="Équipe Développement",
    created_by=user_id
)
```

### Lister les groupes
```python
from models.groupe import Groupe

groupes = Groupe.get_by_user(user_id)
for groupe in groupes:
    print(f"Groupe: {groupe.nom} (ID: {groupe.id})")
```

### Ajouter un membre à un groupe
```python
from models.groupe import Groupe

# Vérifie d'abord que l'utilisateur est admin du groupe
if Groupe.is_admin(groupe_id, current_user_id):
    Groupe.add_member(groupe_id, new_user_id, is_admin=False)
```

### Retirer un membre d'un groupe
```python
from models.groupe import Groupe

if Groupe.is_admin(groupe_id, current_user_id):
    Groupe.remove_member(groupe_id, user_id_to_remove)
```

### Ajouter un mot de passe à un groupe
```python
from models.groupe import Groupe

# Vérifie que l'utilisateur a les droits d'écriture sur le groupe
if Groupe.can_write(groupe_id, user_id):
    password_id = Password.create(
        intitule="Accès serveur",
        valeur="motdepasse123",
        created_by=user_id,
        groupe_id=groupe_id
    )
```

### Voir les mots de passe d'un groupe
```python
from models.groupe import Groupe

# Vérifie que l'utilisateur a accès au groupe
if Groupe.is_member(groupe_id, user_id):
    passwords = Groupe.get_passwords(groupe_id)
    for pwd in passwords:
        print(f"{pwd['intitule']}: {pwd['valeur']}")
```

## Sécurité
- Tous les mots de passe sont stockés de manière sécurisée
- L'accès aux mots de passe est contrôlé par des permissions au niveau de la base de données
- Les mots de passe ne sont jamais stockés en clair

## Gestion des Erreurs
Toutes les méthodes peuvent lever des exceptions en cas d'erreur. Il est recommandé d'utiliser des blocs try/except pour les gérer proprement.
