from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from functools import wraps
import secrets
import string
import json
import os
from models import User, Groupe, Password
from database import Database  # Import de la classe Database

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_clé_secrète_très_longue_et_sécurisée'

# Initialisation des extensions
CORS(app)  # Active CORS pour toutes les routes

# Initialisation de la base de données
db = Database()  # Crée une instance de la base de données

# Décorateur pour vérifier le token JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1] if ' ' in request.headers['Authorization'] else None
        
        if not token:
            return jsonify({'message': 'Token manquant'}), 401
            
        try:
            # Ici, vous devriez valider le token JWT
            # Pour l'instant, on suppose que le token est l'ID de l'utilisateur
            current_user = User.get_by_id(token)
            if not current_user:
                return jsonify({'message': 'Utilisateur non trouvé'}), 404
        except Exception as e:
            return jsonify({'message': 'Token invalide', 'error': str(e)}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

# Route de base pour vérifier que l'API fonctionne
@app.route('/api', methods=['GET'])
def api_home():
    return jsonify({
        'message': 'Bienvenue sur l\'API de génération de mots de passe',
        'endpoints': {
            'auth': {
                'register': '/api/auth/register',
                'login': '/api/auth/login'
            },
            'passwords': {
                'generate': '/api/passwords/generate',
                'list': '/api/passwords',
                'detail': '/api/passwords/<int:password_id>'
            },
            'groups': {
                'list': '/api/groups',
                'detail': '/api/groups/<int:group_id>',
                'members': '/api/groups/<int:group_id>/members',
                'passwords': '/api/groups/<int:group_id>/passwords'
            },
            'health': '/api/health'
        }
    }), 200

# Routes d'authentification
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['mail', 'password', 'prenom', 'nom']):
        return jsonify({'message': 'Tous les champs sont requis'}), 400
    
    # Vérifier si l'mail existe déjà
    existing_users = User.query_many("SELECT * FROM app_user WHERE mail = ?", (data['mail'],))
    if existing_users:
        return jsonify({'message': 'Cet mail est déjà utilisé'}), 400
        
    try:
        # Créer un nouvel utilisateur en utilisant la méthode de classe create
        user = User.create(
            nom=data['nom'],
            prenom=data['prenom'],
            mail=data['mail'],
            mdp=data['password']
        )
        
        # Récupérer l'ID de l'utilisateur créé
        user_id = user.id
        
        # Générer un token JWT (simplifié pour l'exemple)
        token = str(user_id)
        
        return jsonify({
            'message': 'Compte créé avec succès',
            'user': {
                'id': user_id,
                'mail': user.mail,
                'prenom': user.prenom,
                'nom': user.nom
            },
            'token': token
        }), 201
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['mail', 'password']):
        return jsonify({'message': 'mail et mot de passe requis'}), 400
    
    # Utilisation de la méthode de requête personnalisée
    users = User.query_many("SELECT * FROM app_user WHERE mail = ?", (data['mail'],))
    
    if not users:
        return jsonify({'message': 'mail ou mot de passe incorrect'}), 401
        
    user_data = users[0]  # Récupérer le premier utilisateur trouvé
    
    # Créer une instance User à partir des données de la base de données
    user = User(
        id=user_data[0],
        mail=user_data[1],
        prenom=user_data[2],
        nom=user_data[3],
        mdp_hash=user_data[4]  # Le mot de passe haché est stocké dans la 5ème colonne
    )
    
    if not user.get_by_credentials(data['mail'], data['password']):
        return jsonify({'message': 'mail ou mot de passe incorrect'}), 401
        
    # Générer un token JWT (simplifié pour l'exemple)
    token = str(user.id)
    
    return jsonify({
        'message': 'Connexion réussie',
        'user': {
            'id': user.id,
            'mail': user.mail,
            'prenom': user.prenom,
            'nom': user.nom
        },
        'token': token
    }), 200

# Routes pour les mots de passe
@app.route('/api/passwords', methods=['GET'])
@token_required
def list_user_passwords(current_user):
    """Récupère la liste des mots de passe de l'utilisateur connecté"""
    # Récupérer les mots de passe de l'utilisateur
    rows = Password.query_many('''
        SELECT p.id, p.intitule, p.valeur_chiffree, p.created_at, p.created_by 
        FROM password p
        JOIN user_pwd up ON p.id = up.password_id
        WHERE up.user_id = ?
    ''', (current_user.id,))
    
    return jsonify([{
        'id': row[0],
        'name': row[1],
        'value': row[2],
        'created_at': row[3],
        'created_by': row[4]
    } for row in rows]), 200

@app.route('/api/passwords/<password_id>', methods=['GET'])
@token_required
def get_password(current_user, password_id):
    # Vérifier que l'utilisateur a accès à ce mot de passe
    row = Password.query_one('''
        SELECT p.id, p.intitule, p.valeur_chiffree, p.created_at, p.created_by 
        FROM password p
        JOIN user_pwd up ON p.id = up.password_id
        WHERE p.id = ? AND up.user_id = ?
    ''', (password_id, current_user.id))
    
    if not row:
        return jsonify({'message': 'Mot de passe non trouvé ou accès non autorisé'}), 404
    
    return jsonify({
        'id': row[0],
        'name': row[1],
        'value': row[2],
        'created_at': row[3],
        'created_by': row[4]
    }), 200

@app.route('/api/passwords/<password_id>', methods=['DELETE'])
@token_required
def delete_password(current_user, password_id):
    # Vérifier que l'utilisateur a le droit de supprimer ce mot de passe
    password = Password.query_one('''
        SELECT p.* FROM password p
        JOIN user_pwd up ON p.id = up.password_id
        WHERE p.id = ? AND up.user_id = ?
    ''', (password_id, current_user.id))
    
    if not password:
        return jsonify({'message': 'Mot de passe non trouvé ou accès non autorisé'}), 404
    
    # Supprimer les entrées de la table de liaison
    Password.query_execute('DELETE FROM user_pwd WHERE password_id = ?', (password_id,))
    # Supprimer le mot de passe
    Password.query_execute('DELETE FROM password WHERE id = ?', (password_id,))
    
    return jsonify({'message': 'Mot de passe supprimé avec succès'}), 200

@app.route('/api/passwords/generate', methods=['POST'])
@token_required
def generate_password_route(current_user):
    data = request.get_json()
    length = data.get('length', 12)
    use_uppercase = data.get('use_uppercase', True)
    use_digits = data.get('use_digits', True)
    use_special = data.get('use_special', True)
    
    # Logique de génération de mot de passe
    chars = string.ascii_lowercase
    if use_uppercase:
        chars += string.ascii_uppercase
    if use_digits:
        chars += string.digits
    if use_special:
        chars += '!@#$%^&*()_+{}[]|;:,.<>?'
    
    password = ''.join(secrets.choice(chars) for _ in range(length))
    
    # Enregistrer le mot de passe si un nom est fourni
    name = data.get('name')
    if name:
        try:
            # Utilisation de la méthode create de la classe Password
            new_password = Password.create(
                intitule=name,
                valeur=password,
                created_by=current_user.id
            )
            
            # Si un groupe est spécifié, ajouter le mot de passe au groupe
            if data.get('groupe_id'):
                # Ici, vous devrez implémenter la logique pour ajouter le mot de passe à un groupe
                # Cela dépend de comment vous gérez les groupes de mots de passe
                pass
            
            return jsonify({
                'password': password,
                'saved': True,
                'password_id': new_password.id
            }), 201
        except Exception as e:
            return jsonify({
                'password': password,
                'saved': False,
                'message': str(e)
            }), 500
    
    return jsonify({'password': password, 'saved': False}), 200

# Cette route a été déplacée et renommée en list_user_passwords

# Routes pour les groupes
@app.route('/api/groups', methods=['GET', 'POST'])
@token_required
def manage_groups(current_user):
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'message': 'Le nom du groupe est requis'}), 400
            
        try:
            # Utilisation de la méthode create de la classe Groupe
            groupe = Groupe.create(nom=data['name'], admin_id=current_user.id)
            
            return jsonify({
                'id': groupe.id,
                'name': groupe.nom,
                'created_at': groupe.created_at,
                'creator_id': groupe.admin_id,
                'message': 'Groupe créé avec succès'
            }), 201
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    # GET - Liste des groupes de l'utilisateur
    groupes = Groupe.get_by_user(current_user.id)
    return jsonify([{
        'id': g.id,
        'name': g.nom,
        'created_at': g.created_at,
        'creator_id': g.admin_id,
        'is_creator': g.admin_id == current_user.id
    } for g in groupes]), 200

@app.route('/api/groups/<group_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def manage_group(current_user, group_id):
    # Récupérer le groupe
    groupe = Groupe.query_one('SELECT * FROM groupe WHERE id = ?', (group_id,))
    if not groupe:
        return jsonify({'message': 'Groupe non trouvé'}), 404
    
    # Vérifier que l'utilisateur est membre du groupe
    is_member = Groupe.query_one(
        'SELECT 1 FROM membre WHERE groupe_id = ? AND user_id = ?',
        (group_id, current_user.id)
    )
    if not is_member:
        return jsonify({'message': 'Accès non autorisé'}), 403
    
    # Créer un objet Groupe à partir du résultat de la requête
    groupe_obj = Groupe(
        id=groupe[0],
        nom=groupe[1],
        admin_id=groupe[2],
        created_at=groupe[3]
    )
    
    if request.method == 'GET':
        # Récupérer les membres du groupe
        members = Groupe.query_many('''
            SELECT u.id, u.mail, u.prenom, u.nom 
            FROM app_user u
            JOIN membre m ON u.id = m.user_id
            WHERE m.groupe_id = ?
        ''', (group_id,))
        
        return jsonify({
            'id': groupe_obj.id,
            'name': groupe_obj.nom,
            'created_at': groupe_obj.created_at,
            'admin_id': groupe_obj.admin_id,
            'members': [{
                'id': m[0],
                'mail': m[1],
                'prenom': m[2],
                'nom': m[3]
            } for m in members]
        }), 200
        
    # Seul l'admin peut modifier ou supprimer le groupe
    if groupe_obj.admin_id != current_user.id:
        return jsonify({'message': 'Seul l\'administrateur du groupe peut effectuer cette action'}), 403
    
    if request.method == 'PUT':
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'message': 'Le nom du groupe est requis'}), 400
            
        # Mettre à jour le nom du groupe
        Groupe.query_execute(
            'UPDATE groupe SET nom = ? WHERE id = ?',
            (data['name'], group_id)
        )
        
        return jsonify({
            'id': groupe_obj.id,
            'name': data['name'],
            'message': 'Groupe mis à jour avec succès'
        }), 200
        
    elif request.method == 'DELETE':
        # Supprimer d'abord les membres du groupe
        Groupe.query_execute('DELETE FROM membre WHERE groupe_id = ?', (group_id,))
        # Puis supprimer le groupe
        Groupe.query_execute('DELETE FROM groupe WHERE id = ?', (group_id,))
        
        return jsonify({'message': 'Groupe supprimé avec succès'}), 200

@app.route('/api/groups/<string:group_id>/members', methods=['GET', 'POST', 'DELETE'])
@token_required
def manage_group_members(current_user, group_id):
    from uuid import UUID
    # Récupérer le groupe par son ID
    groupe = Groupe.get_by_id(group_id)
    if not groupe:
        return jsonify({'message': 'Groupe non trouvé'}), 404
    
    # Vérifier que l'utilisateur est membre du groupe
    members = groupe.get_members()
    is_member = any(m['id'] == current_user.id for m in members)
    if not is_member:
        return jsonify({'message': 'Accès non autorisé'}), 403
    
    if request.method == 'GET':
        # On retourne directement la liste des membres formatée par get_members()
        return jsonify(members), 200
        
    # Seul l'administrateur peut ajouter/supprimer des membres
    if groupe.admin_id != current_user.id:
        return jsonify({'message': 'Seul l\'administrateur peut gérer les membres'}), 403
    
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'message': 'Email de l\'utilisateur requis'}), 400
    
    if request.method == 'POST':
        # Utiliser la méthode add_member_by_email de la classe Groupe
        result = groupe.add_member_by_email(data['email'], current_user.id)
        if not result['success']:
            return jsonify({'message': result['message']}), 400
            
        # Récupérer les informations de l'utilisateur pour la réponse
        user = User.get_by_email(data['email'])
        if not user:
            return jsonify({'message': result['message']}), 200
            
        return jsonify({
            'message': result['message'],
            'user': {
                'id': user.id,
                'mail': user.mail,
                'prenom': user.prenom,
                'nom': user.nom
            }
        }), 200
        
    elif request.method == 'DELETE':
        if not data or 'email' not in data:
            return jsonify({'message': 'Email de l\'utilisateur requis'}), 400
            
        # Utiliser la méthode remove_member_by_email de la classe Groupe
        result = groupe.remove_member_by_email(data['email'], current_user.id)
        if not result['success']:
            return jsonify({'message': result['message']}), 400
            
        return jsonify({'message': result['message']}), 200

# Routes pour la gestion des mots de passe d'un groupe

@app.route('/api/groups/<string:group_id>/passwords', methods=['GET', 'POST'])
@token_required
def manage_group_passwords(current_user, group_id):
    """
    GET: Récupère tous les mots de passe d'un groupe
    POST: Ajoute un mot de passe au groupe
    """
    # Récupérer le groupe
    groupe = Groupe.get_by_id(group_id)
    if not groupe:
        return jsonify({'message': 'Groupe non trouvé'}), 404
    
    # Vérifier que l'utilisateur est membre du groupe
    members = groupe.get_members()
    is_member = any(m['id'] == current_user.id for m in members)
    if not is_member:
        return jsonify({'message': 'Accès non autorisé'}), 403
    
    if request.method == 'GET':
        # Récupérer tous les mots de passe du groupe
        passwords = groupe.get_passwords()
        return jsonify(passwords), 200
        
    elif request.method == 'POST':
        # Ajouter un mot de passe au groupe
        data = request.get_json()
        if not data or 'password_id' not in data:
            return jsonify({'message': 'ID du mot de passe requis'}), 400
            
        # Vérifier que le mot de passe existe
        password = Password.get_by_id(data['password_id'])
        if not password:
            return jsonify({'message': 'Mot de passe non trouvé'}), 404
            
        # Vérifier que l'utilisateur a accès à ce mot de passe
        if password.created_by != current_user.id and not any(m['id'] == password.created_by for m in members):
            return jsonify({'message': 'Vous n\'avez pas accès à ce mot de passe'}), 403
            
        # Ajouter le mot de passe au groupe
        result = groupe.add_password_to_group(password.id, current_user.id)
        if not result['success']:
            return jsonify({'message': result['message']}), 400
            
        return jsonify({
            'message': result['message'],
            'password': {
                'id': password.id,
                'intitule': password.intitule,
                'created_at': password.created_at
            }
        }), 201

# Route de vérification de l'état du serveur
@app.route('/api/generate', methods=['GET'])
def generate_password():
    try:
        # Récupération des paramètres de la requête
        length = int(request.args.get('length', 12))  # Longueur par défaut : 12 caractères
        use_uppercase = request.args.get('uppercase', 'true').lower() == 'true'
        use_digits = request.args.get('digits', 'true').lower() == 'true'
        use_special = request.args.get('special', 'true').lower() == 'true'

        # Construction des caractères possibles
        characters = string.ascii_lowercase
        if use_uppercase:
            characters += string.ascii_uppercase
        if use_digits:
            characters += string.digits
        if use_special:
            characters += '!@#$%^&*()_+-=[]{}|;:,.<>?'

        # Vérification qu'il y a au moins un type de caractère
        if not characters:
            return jsonify({'error': 'Au moins un type de caractère doit être activé'}), 400

        # Génération du mot de passe
        password = ''.join(secrets.choice(characters) for _ in range(length))
        
        return jsonify({
            'password': password,
            'length': length,
            'has_uppercase': use_uppercase,
            'has_digits': use_digits,
            'has_special': use_special
        }), 200

    except ValueError:
        return jsonify({'error': 'Le paramètre length doit être un nombre'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route de vérification de l'état du serveur
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

# Gestion des erreurs 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Ressource non trouvée'}), 404

# Gestion des erreurs 500
@app.errorhandler(500)
def internal_error(error):
    # Pas besoin de rollback explicite avec notre implémentation personnalisée
    return jsonify({'message': 'Erreur interne du serveur', 'error': str(error)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
