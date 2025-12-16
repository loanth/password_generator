import sys
from getpass import getpass
from models import User, Groupe, Password

def print_menu():
    print("\n=== Gestionnaire de Mots de Passe ===")
    print("1. Créer un compte")
    print("2. Se connecter")
    print("0. Quitter")
    return input("Choisissez une option: ")

def print_user_menu(user):
    print(f"\n=== Bienvenue {user.prenom} {user.nom} ===")
    print("1. Générer un mot de passe")
    print("2. Voir mes mots de passe")
    print("3. Créer un groupe")
    print("4. Voir mes groupes")
    print("5. Gérer un groupe")
    print("0. Se déconnecter")
    return input("Choisissez une option: ")

def print_group_menu():
    print("\n=== Gestion du Groupe ===")
    print("1. Ajouter un membre")
    print("2. Retirer un membre")
    print("3. Ajouter un mot de passe")
    print("4. Voir les mots de passe du groupe")
    print("0. Retour")
    return input("Choisissez une option: ")

def create_account():
    print("\n=== Création de compte ===")
    nom = input("Nom: ")
    prenom = input("Prénom: ")
    mail = input("Email: ")
    mdp = getpass("Mot de passe: ")
    
    try:
        user = User.create(nom, prenom, mail, mdp)
        print("Compte créé avec succès!")
        return user
    except Exception as e:
        print(f"Erreur lors de la création du compte: {e}")
        return None

def login():
    print("\n=== Connexion ===")
    mail = input("Email: ")
    mdp = getpass("Mot de passe: ")
    
    user = User.get_by_credentials(mail, mdp)
    if user:
        print(f"Bienvenue {user.prenom} {user.nom}!")
        return user
    else:
        print("Identifiants incorrects.")
        return None

def generate_password(user):
    print("\n=== Générer un mot de passe ===")
    intitule = input("Intitulé (ex: 'Compte Google'): ")
    length = input("Longueur du mot de passe [16]: ") or "16"
    
    try:
        length = int(length)
        if length < 8:
            print("La longueur minimale est de 8 caractères.")
            return
            
        password = Password.generate(length)
        print(f"\nMot de passe généré: {password}")
        
        save = input("Voulez-vous enregistrer ce mot de passe? (o/n): ").lower()
        if save == 'o':
            Password.create(intitule, password, user.id)
            print("Mot de passe enregistré avec succès!")
    except ValueError:
        print("Veuillez entrer un nombre valide.")

def view_passwords(user):
    print("\n=== Mes Mots de Passe ===")
    passwords = user.get_passwords()
    
    if not passwords:
        print("Aucun mot de passe enregistré.")
        return
    
    for i, pwd in enumerate(passwords, 1):
        print(f"{i}. {pwd['intitule']} - {pwd['valeur']} (créé le {pwd['created_at']})")

def create_group(user):
    print("\n=== Créer un Groupe ===")
    nom = input("Nom du groupe: ")
    
    try:
        groupe = Groupe.create(nom, user.id)
        print(f"Groupe '{groupe.nom}' créé avec succès!")
    except Exception as e:
        print(f"Erreur lors de la création du groupe: {e}")

def view_groups(user):
    print("\n=== Mes Groupes ===")
    groupes = Groupe.get_by_user(user.id)
    
    if not groupes:
        print("Vous n'êtes dans aucun groupe.")
        return []
    
    for i, groupe in enumerate(groupes, 1):
        admin = " (Admin)" if groupe.admin_id == user.id else ""
        print(f"{i}. {groupe.nom}{admin}")
    
    return groupes

def manage_group(user, groupe):
    while True:
        choice = print_group_menu()
        
        if choice == '1':  # Ajouter un membre
            if groupe.admin_id != user.id:
                print("Seul l'administrateur peut ajouter des membres.")
                continue
                
            email = input("Email du membre à ajouter: ")
            # Ici, vous devriez chercher l'utilisateur par email
            # Pour simplifier, on suppose que l'ID est entré directement
            try:
                member_id = int(input("ID du membre: "))
                if groupe.add_member(member_id, user.id):
                    print("Membre ajouté avec succès!")
                else:
                    print("Impossible d'ajouter ce membre.")
            except ValueError:
                print("ID invalide.")
                
        elif choice == '2':  # Retirer un membre
            if groupe.admin_id != user.id:
                print("Seul l'administrateur peut retirer des membres.")
                continue
                
            try:
                member_id = int(input("ID du membre à retirer: "))
                if groupe.remove_member(member_id, user.id):
                    print("Membre retiré avec succès!")
                else:
                    print("Impossible de retirer ce membre.")
            except ValueError:
                print("ID invalide.")
                
        elif choice == '3':  # Ajouter un mot de passe
            intitule = input("Intitulé du mot de passe: ")
            valeur = getpass("Mot de passe (laissez vide pour en générer un): ")
            
            if not valeur:
                length = input("Longueur du mot de passe [16]: ") or "16"
                try:
                    length = int(length)
                    if length < 8:
                        print("La longueur minimale est de 8 caractères.")
                        continue
                    valeur = Password.generate(length)
                    print(f"Mot de passe généré: {valeur}")
                except ValueError:
                    print("Longueur invalide.")
                    continue
            
            try:
                password_id = Password.create(intitule, valeur, user.id, groupe.id)
                print("Mot de passe ajouté au groupe avec succès!")
            except Exception as e:
                print(f"Erreur lors de l'ajout du mot de passe: {e}")
                
        elif choice == '4':  # Voir les mots de passe du groupe
            print(f"\n=== Mots de passe du groupe {groupe.nom} ===")
            passwords = groupe.get_passwords()
            
            if not passwords:
                print("Aucun mot de passe dans ce groupe.")
                continue
                
            for i, pwd in enumerate(passwords, 1):
                print(f"{i}. {pwd['intitule']} - {pwd['valeur']} (par {pwd['created_by']}, le {pwd['created_at']})")
                
        elif choice == '0':  # Retour
            break
        else:
            print("Option invalide.")

def main():
    current_user = None
    
    while True:
        if current_user is None:
            choice = print_menu()
            
            if choice == '1':  # Créer un compte
                current_user = create_account()
            elif choice == '2':  # Se connecter
                current_user = login()
            elif choice == '0':  # Quitter
                print("Au revoir!")
                sys.exit(0)
            else:
                print("Option invalide.")
        else:
            choice = print_user_menu(current_user)
            
            if choice == '1':  # Générer un mot de passe
                generate_password(current_user)
            elif choice == '2':  # Voir mes mots de passe
                view_passwords(current_user)
            elif choice == '3':  # Créer un groupe
                create_group(current_user)
            elif choice == '4':  # Voir mes groupes
                groupes = view_groups(current_user)
                if groupes:
                    try:
                        group_choice = input("\nEntrez le numéro du groupe à gérer (0 pour annuler): ")
                        if group_choice != '0':
                            groupe = groupes[int(group_choice) - 1]
                            manage_group(current_user, groupe)
                    except (ValueError, IndexError):
                        print("Choix invalide.")
            elif choice == '5':  # Gérer un groupe
                groupes = view_groups(current_user)
                if groupes:
                    try:
                        group_choice = input("\nEntrez le numéro du groupe à gérer (0 pour annuler): ")
                        if group_choice != '0':
                            groupe = groupes[int(group_choice) - 1]
                            manage_group(current_user, groupe)
                    except (ValueError, IndexError):
                        print("Choix invalide.")
            elif choice == '0':  # Se déconnecter
                current_user = None
                print("Déconnexion réussie.")
            else:
                print("Option invalide.")

if __name__ == "__main__":
    main()
