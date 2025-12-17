import sys
import os
from getpass import getpass
from models import User, Groupe, Password

def clear_screen():
    """Efface l'écran de la console"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Affiche un en-tête stylisé"""
    clear_screen()
    print("=" * 50)
    print(f"{title:^50}")
    print("=" * 50)

def test_user_creation():
    print_header("TEST : Création d'utilisateur")
    print("Création d'un nouvel utilisateur :")
    nom = input("Nom : ")
    prenom = input("Prénom : ")
    mail = input("Email : ")
    mdp = getpass("Mot de passe : ")
    
    try:
        user = User.create(nom, prenom, mail, mdp)
        print("\n✅ Utilisateur créé avec succès !")
        print(f"ID: {user.id}, Nom: {user.nom}, Email: {user.mail}")
        return user
    except Exception as e:
        print(f"\n❌ Erreur lors de la création de l'utilisateur : {e}")
        return None

def test_login():
    print_header("TEST : Connexion")
    print("Connectez-vous :")
    mail = input("Email : ")
    mdp = getpass("Mot de passe : ")
    
    user = User.get_by_credentials(mail, mdp)
    if user:
        print(f"\n✅ Connexion réussie ! Bienvenue {user.prenom} {user.nom}")
        return user
    else:
        print("\n❌ Identifiants incorrects.")
        return None

def test_password_generation(user):
    print_header("TEST : Génération de mot de passe")
    print("Génération d'un mot de passe sécurisé")
    intitule = input("Intitulé (ex: Compte Google) : ")
    
    # Génération d'un mot de passe
    mdp = Password.generate(16)
    print(f"\nMot de passe généré : {mdp}")
    
    # Demander si l'utilisateur veut sauvegarder
    save = input("\nVoulez-vous sauvegarder ce mot de passe ? (o/n) : ").lower()
    if save == 'o':
        try:
            password_id = Password.create(intitule, mdp, user.id)
            print("\n✅ Mot de passe sauvegardé avec succès !")
            return password_id
        except Exception as e:
            print(f"\n❌ Erreur lors de la sauvegarde : {e}")
    return None

def test_create_group(user):
    print_header("TEST : Création de groupe")
    print("Création d'un nouveau groupe")
    nom = input("Nom du groupe : ")
    
    try:
        groupe = Groupe.create(nom, user.id)
        print(f"\n✅ Groupe '{groupe.nom}' créé avec succès ! (ID: {groupe.id})")
        return groupe
    except Exception as e:
        print(f"\n❌ Erreur lors de la création du groupe : {e}")
        return None

def test_add_member(groupe, admin_user):
    print_header("AJOUT D'UN MEMBRE AU GROUPE")
    if groupe.admin_id != admin_user.id:
        print("❌ Vous devez être l'admin du groupe pour ajouter des membres.")
        return
    
    print(f"\nGroupe : {groupe.nom}")
    print("Ajout d'un nouveau membre par son email")
    email = input("\nEmail de l'utilisateur à ajouter : ").strip()
    
    if not email:
        print("\n❌ L'email ne peut pas être vide")
        return
    
    # Vérifier si l'email est valide
    if not User._is_valid_email(email):
        print("\n❌ Format d'email invalide")
        return
    
    # Ajouter le membre en utilisant l'email
    result = groupe.add_member_by_email(email, admin_user.id)
    
    if result['success']:
        print(f"\n✅ {result['message']}")
    else:
        print(f"\n❌ {result['message']}")

def test_view_passwords(user):
    print_header("MES MOTS DE PASSE")
    print("Récupération de vos mots de passe...")
    
    passwords = user.get_passwords()
    if not passwords:
        print("\nAucun mot de passe enregistré.")
        return
    
    print(f"\n🔑 Vous avez {len(passwords)} mot(s) de passe enregistré(s) :")
    for pwd in passwords:
        print(f"\n📌 {pwd['intitule']}")
        print(f"   Mot de passe : {pwd['valeur']}")
        print(f"   Créé le : {pwd['created_at']}")
    
    input("\nAppuyez sur Entrée pour continuer...")

def test_view_groups(user):
    print_header("MES GROUPES")
    print("Récupération de vos groupes...")
    
    groupes = Groupe.get_by_user(user.id)
    if not groupes:
        print("\nVous n'êtes dans aucun groupe.")
        return []
    
    print(f"\n👥 Vous êtes dans {len(groupes)} groupe(s) :")
    for i, groupe in enumerate(groupes, 1):
        admin_status = " (Admin)" if groupe.admin_id == user.id else ""
        print(f"{i}. {groupe.nom}{admin_status} - {len(groupe.get_members())} membre(s)")
    
    return groupes

def test_group_management(user):
    groupes = test_view_groups(user)
    if not groupes:
        input("\nAppuyez sur Entrée pour continuer...")
        return
    
    try:
        choix = input("\nEntrez le numéro du groupe à gérer (0 pour annuler) : ")
        if choix == '0':
            return
            
        groupe = groupes[int(choix) - 1]
        
        while True:
            print_header(f"GESTION DU GROUPE : {groupe.nom}")
            print("1. Voir les membres")
            print("2. Ajouter un membre")
            print("3. Retirer un membre")
            print("4. Voir les mots de passe du groupe")
            print("5. Ajouter un mot de passe")
            print("0. Retour")
            
            choix_gestion = input("\nChoisissez une option : ")
            
            if choix_gestion == '1':  # Voir les membres
                print_header(f"MEMBRES DU GROUPE : {groupe.nom}")
                membres = groupe.get_members()
                for m in membres:
                    admin_status = " (Admin)" if m['is_admin'] else ""
                    print(f"- {m['prenom']} {m['nom']}{admin_status} ({m['mail']})")
                input("\nAppuyez sur Entrée pour continuer...")
                
            elif choix_gestion == '2':  # Ajouter un membre
                if groupe.admin_id == user.id:
                    test_add_member(groupe, user)
                else:
                    print("\n❌ Seul l'admin peut ajouter des membres.")
                input("\nAppuyez sur Entrée pour continuer...")
                
            elif choix_gestion == '3':  # Retirer un membre
                if groupe.admin_id != user.id:
                    print("\n❌ Seul l'admin peut retirer des membres.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue
                    
                membres = groupe.get_members()
                print_header("RETIRER UN MEMBRE")
                for i, m in enumerate(membres, 1):
                    if m['id'] != user.id:  # Ne pas afficher l'admin
                        print(f"{i}. {m['prenom']} {m['nom']} ({m['mail']})")
                
                try:
                    choix_membre = input("\nNuméro du membre à retirer (0 pour annuler) : ")
                    if choix_membre == '0':
                        continue
                        
                    membre_id = membres[int(choix_membre) - 1]['id']
                    if groupe.remove_member(membre_id, user.id):
                        print("\n✅ Membre retiré avec succès !")
                    else:
                        print("\n❌ Impossible de retirer ce membre.")
                except (ValueError, IndexError):
                    print("\n❌ Choix invalide.")
                input("\nAppuyez sur Entrée pour continuer...")
                
            elif choix_gestion == '4':  # Voir les mots de passe du groupe
                print_header(f"MOTS DE PASSE DU GROUPE : {groupe.nom}")
                mots_de_passe = groupe.get_passwords()
                
                if not mots_de_passe:
                    print("\nAucun mot de passe partagé dans ce groupe.")
                else:
                    print(f"\n🔑 {len(mots_de_passe)} mot(s) de passe partagé(s) :")
                    for pwd in mots_de_passe:
                        print(f"\n📌 {pwd['intitule']}")
                        print(f"   Mot de passe : {pwd['valeur']}")
                        print(f"   Ajouté par : {pwd['created_by']}")
                        print(f"   Date : {pwd['created_at']}")
                input("\nAppuyez sur Entrée pour continuer...")
                
            elif choix_gestion == '5':  # Ajouter un mot de passe
                print_header("AJOUTER UN MOT DE PASSE AU GROUPE")
                intitule = input("Intitulé (ex: Compte Google Pro) : ")
                mdp = input("Mot de passe (laissez vide pour en générer un) : ")
                
                if not mdp:
                    mdp = Password.generate(16)
                    print(f"\nMot de passe généré : {mdp}")
                
                try:
                    password_id = Password.create(intitule, mdp, user.id, groupe.id)
                    print("\n✅ Mot de passe ajouté au groupe avec succès !")
                except Exception as e:
                    print(f"\n❌ Erreur lors de l'ajout : {e}")
                input("\nAppuyez sur Entrée pour continuer...")
                
            elif choix_gestion == '0':  # Retour
                break
            
    except (ValueError, IndexError):
        print("\n❌ Choix invalide.")
        input("\nAppuyez sur Entrée pour continuer...")
    current_user = None
    
    while True:
        if current_user is None:
            # Menu principal (utilisateur non connecté)
            print_header("MENU PRINCIPAL")
            print("1. Créer un compte")
            print("2. Se connecter")
            print("0. Quitter")
            
            try:
                choix = input("\nChoisissez une option : ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nAu revoir ! 👋")
                sys.exit(0)
                
            if not choix:
                continue
                
            if choix == '1':
                test_user_creation()
                input("\nAppuyez sur Entrée pour continuer...")
            elif choix == '2':
                current_user = test_login()
                if current_user:
                    input("\nAppuyez sur Entrée pour accéder au menu principal...")
            elif choix == '0':
                print("\nAu revoir ! 👋")
                sys.exit(0)
            else:
                print("\nOption invalide.")
        else:
            # Menu utilisateur connecté
            print_header(f"BIENVENUE {current_user.prenom.upper()}")
            print("1. Générer un mot de passe")
            print("2. Voir mes mots de passe")
            print("3. Créer un groupe")
            print("4. Gérer mes groupes")
            print("0. Se déconnecter")
            
            try:
                choix = input("\nChoisissez une option : ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nAu revoir ! 👋")
                sys.exit(0)
                
            if choix == '1':
                test_password_generation(current_user)
                input("\nAppuyez sur Entrée pour continuer...")
            elif choix == '2':
                test_view_passwords(current_user)
            elif choix == '3':
                test_create_group(current_user)
                input("\nAppuyez sur Entrée pour continuer...")
            elif choix == '4':
                test_group_management(current_user)
            elif choix == '0':
                print(f"\nAu revoir {current_user.prenom} ! 👋")
                current_user = None
                input("\nAppuyez sur Entrée pour revenir au menu principal...")

def main():
    current_user = None
    
    while True:
        if current_user is None:
            # Menu principal (utilisateur non connecté)
            print_header("MENU PRINCIPAL")
            print("1. Créer un compte")
            print("2. Se connecter")
            print("0. Quitter")
            
            try:
                choix = input("\nChoisissez une option : ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nAu revoir !")
                sys.exit(0)
                
            if not choix:
                continue
                
            if choix == '1':
                test_user_creation()
                input("\nAppuyez sur Entrée pour continuer...")
            elif choix == '2':
                current_user = test_login()
                if current_user:
                    input("\nAppuyez sur Entrée pour accéder au menu principal...")
            elif choix == '0':
                print("\nAu revoir !")
                sys.exit(0)
            else:
                print("\nOption invalide.")
        else:
            # Menu utilisateur connecté
            print_header(f"BIENVENUE {current_user.prenom.upper()}")
            print("1. Générer un mot de passe")
            print("2. Voir mes mots de passe")
            print("3. Créer un groupe")
            print("4. Gérer mes groupes")
            print("0. Se déconnecter")
            
            try:
                choix = input("\nChoisissez une option : ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nAu revoir !")
                sys.exit(0)
                
            if choix == '1':
                test_password_generation(current_user)
                input("\nAppuyez sur Entrée pour continuer...")
            elif choix == '2':
                test_view_passwords(current_user)
            elif choix == '3':
                test_create_group(current_user)
                input("\nAppuyez sur Entrée pour continuer...")
            elif choix == '4':
                test_group_management(current_user)
            elif choix == '0':
                print(f"\nAu revoir {current_user.prenom} !")
                current_user = None
                input("\nAppuyez sur Entrée pour revenir au menu principal...")

if __name__ == "__main__":
    try:
        # S'assurer que la base de données est à jour
        from database import db
        db._create_tables()
        
        main()
    except KeyboardInterrupt:
        print("\n\nAu revoir !")
        sys.exit(0)
