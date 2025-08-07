# main.py

from account_creator import AccountCreator
import time
import random
import string

def generate_random_string(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def generate_random_email():
    return f"usuario_{generate_random_string()}@ejemplo.com"

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

if __name__ == "__main__":
    # Puedes configurar si quieres ver el navegador (headless=False)
    # o ejecutarlo en segundo plano (headless=True)
    headless_mode = False

    creator = None # Inicializa creator a None
    try:
        creator = AccountCreator(headless=headless_mode)
        creator.open_page()

        num_accounts_to_create = 1 # Puedes cambiar esto para crear múltiples cuentas

        for i in range(num_accounts_to_create):
            email = "romel.gonzalez00362@gmail.com"
            password = "romel123"
            display_name = "romel_gonzalez"
            gender = "male"
            section_code = "DWYXDZ"

            print(f"\nIntentando crear cuenta {i+1}:")
            print(f" Email: {email}")
            print(f" Contraseña: {password}")
            print(f" Nombre: {display_name}")
            print(f" Codigo de Seccion: {section_code}")

            success = creator.create_account(email, password, display_name, "15", gender)
            if success:
                print(f"Cuenta {email} creada o logueada exitosamente.")
                joined = creator.join_section(section_code)
                
                if joined:
                    print("Se completo el flujo")
                else:
                    print("Fallo el flujo")
            else:
                print(f"Fallo al crear o loguear la cuenta {email}. Revisa el log de errores.")

            # Pausa entre creaciones de cuentas para evitar ser detectado como bot
            if i < num_accounts_to_create - 1:
                print(f"Esperando {random.randint(5, 15)} segundos antes de la siguiente cuenta...")
                time.sleep(random.randint(5, 15))
    except Exception as e:
        print(f"Un error inesperado ocurrió en la ejecución principal: {e}")
    finally:
        print(f"Finalizando el script...")
        # if creator: # Asegúrate de que creator no sea None antes de intentar cerrarlo
        #     creator.quit_driver()