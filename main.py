# main.py

from account_creator import AccountCreator
import time
import random
import pandas as pd

if __name__ == "__main__":
    headless_mode = False
    excel_file_path = 'datos_cuentas.xlsx'

    try:
        df_accounts = pd.read_excel(excel_file_path)
        print(f"Se encontraron {len(df_accounts)} cuentas para procesar.")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{excel_file_path}'.")
        exit()
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo Excel: {e}")
        exit()

    if 'Status' not in df_accounts.columns:
        df_accounts['Status'] = ''
    if 'Mensaje' not in df_accounts.columns:
        df_accounts['Mensaje'] = ''

    # Bucle principal sobre las filas del Excel
    for index, row in df_accounts.iterrows():
        creator = None  # Inicializamos el creator en cada iteración
        status_final = "Error"
        mensaje_final = ""
        
        # Este bloque try/finally se ejecutará por completo para CADA cuenta
        try:
            # No procesar si ya tiene status de 'Éxito'
            if row.get('Status') == 'Éxito':
                print(f"\n--- Saltando fila {index + 2} (Cuenta: {row['Correo']}) porque ya fue procesada con éxito. ---")
                continue

            # --- CAMBIO CLAVE: INICIAMOS un nuevo driver para ESTA cuenta ---
            creator = AccountCreator(headless=headless_mode)

            email = row['Correo']
            password = str(row['Contrasena'])
            display_name = row['Nombre']
            gender = row['Genero']
            section_code = row['CodigoSeccion']

            print(f"\n--- Procesando fila {index + 2} del Excel (Cuenta: {email}) ---")

            creator.open_page()
            success = creator.create_account(email, password, display_name, "15", gender)
            
            if success:
                print(f"Cuenta {email} creada/logueada exitosamente.")
                joined = creator.join_section(section_code)
                if joined:
                    status_final = "Éxito"
                    mensaje_final = "Cuenta creada y unida a la sección correctamente."
                    print("=> Flujo completado con éxito.")
                else:
                    mensaje_final = "La cuenta se creó/logueó, pero falló al unirse a la sección."
                    print(f"=> Fallo: {mensaje_final}")
            else:
                mensaje_final = "Fallo en el proceso de creación/login de la cuenta."
                print(f"=> Fallo: {mensaje_final}")

        except Exception as e:
            error_msg = str(e).split('\n')[0] # Tomamos solo la primera línea del error para un mensaje más limpio
            print(f"  ERROR INESPERADO al procesar la cuenta {row.get('Correo', 'desconocido')}: {error_msg}")
            mensaje_final = f"Excepción inesperada: {error_msg}"
        finally:
            # --- CAMBIO CLAVE: CERRAMOS el driver de ESTA cuenta al finalizar ---
            if creator:
                creator.quit_driver()
            
            # Actualizamos el DataFrame y guardamos en Excel
            print(f"  Resultado guardado: Status='{status_final}', Mensaje='{mensaje_final}'")
            df_accounts.loc[index, 'Status'] = status_final
            df_accounts.loc[index, 'Mensaje'] = mensaje_final
            
            try:
                df_accounts.to_excel(excel_file_path, index=False)
            except PermissionError:
                print(f"\n¡ERROR DE PERMISO! Cierra el archivo '{excel_file_path}' y presiona Enter para reintentar.")
                input()
                df_accounts.to_excel(excel_file_path, index=False)
        
        # Pausa entre creaciones de cuentas
        if index < len(df_accounts) - 1:
            sleep_time = random.randint(5, 15)
            print(f"Esperando {sleep_time} segundos antes de la siguiente cuenta...")
            time.sleep(sleep_time)

    print("\nProceso terminado. Revisa el archivo 'datos_cuentas.xlsx' para ver los resultados.")