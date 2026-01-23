# Documentation de l'API Password Generator

## Table des matières
1. [Authentification](#authentification)
   - [Inscription](#inscription)
   - [Connexion](#connexion)
2. [Mots de passe](#mots-de-passe)
   - [Lister les mots de passe](#lister-les-mots-de-passe)
   - [Obtenir un mot de passe](#obtenir-un-mot-de-passe)
   - [Supprimer un mot de passe](#supprimer-un-mot-de-passe)
   - [Générer un mot de passe](#générer-un-mot-de-passe)
3. [Groupes](#groupes)
   - [Lister les groupes](#lister-les-groupes)
   - [Créer un groupe](#créer-un-groupe)
   - [Gérer un groupe](#gérer-un-groupe)
   - [Gérer les membres d'un groupe](#gérer-les-membres-dun-groupe)
   - [Gérer les mots de passe d'un groupe](#gérer-les-mots-de-passe-dun-groupe)

---

## Authentification

### Inscription
Crée un nouvel utilisateur.

**URL** : `/api/auth/register`

**Méthode** : `POST`

**Corps de la requête** :
```json
{
    "nom": "Doe",
    "prenom": "John",
    "email": "john.doe@example.com",
    "password": "motdepasse123"
}
```

**Réponse en cas de succès** :
```json
{
    "message": "Utilisateur créé avec succès",
    "user": {
        "id": "uuid_utilisateur",
        "nom": "Doe",
        "prenom": "John",
        "email": "john.doe@example.com"
    },
    "token": "jwt_token"
}
```

---

### Connexion
Connecte un utilisateur et retourne un token JWT.

**URL** : `/api/auth/login`

**Méthode** : `POST`

**Corps de la requête** :
```json
{
    "email": "john.doe@example.com",
    "password": "motdepasse123"
}
```

**Réponse en cas de succès** :
```json
{
    "message": "Connexion réussie",
    "token": "jwt_token",
    "user": {
        "id": "uuid_utilisateur",
        "nom": "Doe",
        "prenom": "John",
        "email": "john.doe@example.com"
    }
}
```

---

## Mots de passe

### Lister les mots de passe
Récupère la liste des mots de passe de l'utilisateur connecté.

**URL** : `/api/passwords`

**Méthode** : `GET`

**En-têtes** :
- `Authorization: Bearer jwt_token`

**Réponse en cas de succès** :
```json
[
    {
        "id": "uuid_mot_de_passe",
        "intitule": "Compte Gmail",
        "created_at": "2023-01-01T12:00:00.000Z"
    }
]
```

---

### Obtenir un mot de passe
Récupère les détails d'un mot de passe spécifique.

**URL** : `/api/passwords/<password_id>`

**Méthode** : `GET`

**En-têtes** :
- `Authorization: Bearer jwt_token`

**Réponse en cas de succès** :
```json
{
    "id": "uuid_mot_de_passe",
    "intitule": "Compte Gmail",
    "valeur_chiffree": "chiffré_abc123",
    "created_at": "2023-01-01T12:00:00.000Z"
}
```

---

### Supprimer un mot de passe
Supprime un mot de passe.

**URL** : `/api/passwords/<password_id>`

**Méthode** : `DELETE`

**En-têtes** :
- `Authorization: Bearer jwt_token`

**Réponse en cas de succès** :
```json
{
    "message": "Mot de passe supprimé avec succès"
}
```

---

### Générer un mot de passe
Génère un mot de passe aléatoire.

**URL** : `/api/generate`

**Méthode** : `GET`

**Paramètres de requête** :
- `length` (optionnel) : Longueur du mot de passe (défaut: 12)
- `uppercase` (optionnel) : Inclure des majuscules (défaut: true)
- `digits` (optionnel) : Inclure des chiffres (défaut: true)
- `special` (optionnel) : Inclure des caractères spéciaux (défaut: true)

**Exemple de requête** :
```
GET /api/generate?length=16&uppercase=true&digits=true&special=false
```

**Réponse en cas de succès** :
```json
{
    "password": "aB3dE5fG7hI9jK1"
}
```

---

## Groupes

### Lister les groupes
Récupère la liste des groupes de l'utilisateur connecté.

**URL** : `/api/groups`

**Méthode** : `GET`

**En-têtes** :
- `Authorization: Bearer jwt_token`

**Réponse en cas de succès** :
```json
[
    {
        "id": "uuid_groupe",
        "nom": "Famille",
        "admin_id": "uuid_admin",
        "created_at": "2023-01-01T12:00:00.000Z"
    }
]
```

---

### Créer un groupe
Crée un nouveau groupe.

**URL** : `/api/groups`

**Méthode** : `POST`

**En-têtes** :
- `Authorization: Bearer jwt_token`
- `Content-Type: application/json`

**Corps de la requête** :
```json
{
    "nom": "Famille"
}
```

**Réponse en cas de succès** :
```json
{
    "id": "uuid_groupe",
    "nom": "Famille",
    "admin_id": "votre_uuid",
    "created_at": "2023-01-01T12:00:00.000Z"
}
```

---

### Gérer un groupe
Récupère, met à jour ou supprime un groupe.

**URL** : `/api/groups/<group_id>`

**Méthodes** :
- `GET` : Récupère les détails du groupe
- `PUT` : Met à jour le groupe
- `DELETE` : Supprime le groupe

**En-têtes** :
- `Authorization: Bearer jwt_token`
- `Content-Type: application/json` (pour PUT)

**Corps de la requête (PUT)** :
```json
{
    "nom": "Nouveau nom"
}
```

**Réponse en cas de succès (GET)** :
```json
{
    "id": "uuid_groupe",
    "nom": "Famille",
    "admin_id": "uuid_admin",
    "created_at": "2023-01-01T12:00:00.000Z",
    "membres": [
        {
            "id": "uuid_utilisateur",
            "nom": "Doe",
            "prenom": "John",
            "email": "john.doe@example.com",
            "is_admin": true
        }
    ]
}
```

---

### Gérer les membres d'un groupe
Gère les membres d'un groupe.

**URL** : `/api/groups/<group_id>/members`

**Méthodes** :
- `GET` : Liste les membres du groupe
- `POST` : Ajoute un membre au groupe par email
- `DELETE` : Retire un membre du groupe

**En-têtes** :
- `Authorization: Bearer jwt_token`
- `Content-Type: application/json` (pour POST et DELETE)

**Corps de la requête (POST)** :
```json
{
    "email": "membre@example.com"
}
```

**Corps de la requête (DELETE)** :
```json
{
    "email": "membre@example.com"
}
```

**Réponse en cas de succès (GET)** :
```json
[
    {
        "id": "uuid_utilisateur",
        "nom": "Doe",
        "prenom": "John",
        "email": "john.doe@example.com",
        "is_admin": true
    }
]
```

---

### Gérer les mots de passe d'un groupe
Gère les mots de passe partagés dans un groupe.

**URL** : `/api/groups/<group_id>/passwords`

**Méthodes** :
- `GET` : Liste les mots de passe du groupe
- `POST` : Ajoute un mot de passe au groupe

**En-têtes** :
- `Authorization: Bearer jwt_token`
- `Content-Type: application/json` (pour POST)

**Corps de la requête (POST)** :
```json
{
    "password_id": "uuid_mot_de_passe"
}
```

**Réponse en cas de succès (GET)** :
```json
[
    {
        "id": "uuid_mot_de_passe",
        "intitule": "Compte Netflix",
        "valeur_chiffree": "chiffré_abc123",
        "created_at": "2023-01-01T12:00:00.000Z",
        "auteur_nom": "Doe",
        "auteur_prenom": "John"
    }
]
```

**Réponse en cas de succès (POST)** :
```json
{
    "message": "Mot de passe ajouté au groupe avec succès",
    "password": {
        "id": "uuid_mot_de_passe",
        "intitule": "Compte Netflix",
        "created_at": "2023-01-01T12:00:00.000Z"
    }
}
```

---

## Codes d'état HTTP

| Code | Description |
|------|-------------|
| 200 | Requête réussie |
| 201 | Ressource créée avec succès |
| 400 | Requête invalide |
| 401 | Non autorisé (authentification requise) |
| 403 | Accès refusé (permissions insuffisantes) |
| 404 | Ressource non trouvée |
| 500 | Erreur serveur interne |

## Authentification
Toutes les routes (sauf `/api/auth/register` et `/api/auth/login`) nécessitent un token JWT dans l'en-tête `Authorization` :
```
Authorization: Bearer votre_jwt_token
```
