# account_creator.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import config
import config_extra

class AccountCreator:

    def login(self, email, password):
        print("Intentando iniciar sesión...")
        self.driver.get(config_extra.LOGIN_URL)
        try:
            self.find_and_type(By.ID, config_extra.LOGIN_EMAIL_ID, email, "campo de email (login)")
            self.find_and_type(By.ID, config_extra.LOGIN_PASSWORD_ID, password, "campo de contraseña (login)")
            self.find_and_click(By.ID, config_extra.LOGIN_BUTTON_ID, "botón de login")
            # Esperar a que la página cambie o aparezca un elemento de éxito (ajusta si es necesario)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print("Login exitoso o página cargada tras login.")
            return True
        except Exception as e:
            print(f"Fallo al iniciar sesión: {e}")
            self.driver.save_screenshot("error_login.png")
            return False
    def __init__(self, headless=False):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless") # Ejecutar el navegador sin interfaz gráfica
            options.add_argument("--disable-gpu") # Necesario para headless en algunos sistemas
        options.add_argument("--window-size=1920,1080") # Tamaño de ventana para evitar problemas de responsive
        options.add_argument("--no-sandbox") # Necesario en algunos entornos Linux
        options.add_argument("--disable-dev-shm-usage") # Para entornos Docker/Linux con espacio limitado

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, config.EXPLICIT_WAIT_TIME)
        self.driver.maximize_window() # Maximizar la ventana para asegurar visibilidad de elementos
        self.driver.implicitly_wait(5) # Espera implícita global para todos los find_element

    def open_page(self):
        try:
            print(f"Abriendo la página: {config.TARGET_URL}")
            self.driver.get(config.TARGET_URL)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body"))) # Esperar a que el body cargue
            print("Página cargada exitosamente.")
        except Exception as e:
            print(f"Error al abrir la página: {e}")
            # self.quit_driver()
            raise

    def find_and_type(self, by_method, locator, text, element_name="campo"):
        try:
            element = self.wait.until(EC.visibility_of_element_located((by_method, locator)))
            element.send_keys(text)
            print(f"Ingresado '{text}' en el {element_name}.")
        except Exception as e:
            print(f"Error al encontrar o escribir en el {element_name} ('{locator}'): {e}")
            # self.quit_driver()
            raise

    def find_and_click(self, by_method, locator, element_name="botón"):
        try:
            element = self.wait.until(EC.element_to_be_clickable((by_method, locator)))
            element.click()
            print(f"Clic en el {element_name}.")
        except Exception as e:
            print(f"Error al encontrar o hacer clic en el {element_name} ('{locator}'): {e}")
            # self.quit_driver()
            raise

    def find_element_and_wait(self, by_strategy, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by_strategy, locator))
        )

    def mark_checkbox_and_fill_display_name(self, display_name):
        # 1. Encontrar el checkbox
        checkbox_locator = (By.NAME, config.IS_PARENT_CHECKBOX_NAME)
        is_parent_checkbox = self.find_element_and_wait(
            checkbox_locator[0], checkbox_locator[1]
        )

        # 2. Verificar si ya está marcado y clickearlo si no lo está
        if not is_parent_checkbox.is_selected():
            print(f"Marcando el checkbox: {checkbox_locator[1]}")
            is_parent_checkbox.click()
            # Opcional: una pequeña pausa para que el DOM se actualice si es necesario
            # time.sleep(0.5)
        else:
            print(f"El checkbox {checkbox_locator[1]} ya está marcado.")



    def create_account(self, email, password, display_name, age, gender):
        print("\nIniciando creación de cuenta...")
        try:
            self.find_and_type(By.ID, config.EMAIL_ID, email, "campo de email")
            self.find_and_type(By.ID, config.PASSWORD_ID, password, "campo de contraseña")
            self.find_and_type(By.ID, config.CONFIRM_PASSWORD_ID, password, "campo de confirmación de contraseña")
            self.find_and_click(By.ID, config.CREATE_BUTTON_ID, "botón de registro")

            # Esperar un poco a que la página responda
            time.sleep(2)

            # Verificar si aparece mensaje de error de cuenta existente
            try:
                error_element = self.driver.find_element(By.CLASS_NAME, config.EMAIL_TAKEN_CLASS)
                if error_element and ("existe" in error_element.text.lower() or "already" in error_element.text.lower()):
                    print("La cuenta ya existe. Intentando login...")
                    return self.login(email, password)
            except Exception:
                pass  # No se encontró mensaje de error, continuar

            # Si no hay error, continuar con el flujo normal
            success_element_locator = (By.ID, config.AGE_SELECTOR_ID)
            self.wait.until(EC.presence_of_element_located(success_element_locator))
            # self.mark_checkbox_and_fill_display_name(config.IS_PARENT_CHECKBOX_NAME)
            self.find_and_type(By.ID, config.DISPLAY_NAME_ID, display_name, "campo de nombre para mostrar")
            self.find_and_type(By.ID, config.AGE_SELECTOR_ID, age, "campo de edad")
            self.find_and_type(By.NAME, config.USER_GENDER_NAME, gender, "campo del genero")
            self.find_and_click(By.XPATH, config.GO_TO_MY_ACCOUNT_BUTTON_PATH, "botón de Go to my account")

            time.sleep(1)

            print("Cuenta creada exitosamente. Mensaje de éxito o redirección detectada.")
            return True
        except Exception as e:
            print(f"Fallo al crear la cuenta: {e}")
            self.driver.save_screenshot("error_creacion_cuenta.png")
            return False
        
    def join_section(self, section_code):
        print("\nIniciando asignacion de seccion...")
        
        try:
            self.find_and_click(By.ID, config.HOME_LOGO_ID, "botón de home")

            # Esperar un poco a que la página responda
            time.sleep(2)

            self.find_and_type(By.NAME, config.SECTION_CODE_NAME , section_code, "campo del codigo de la seccion")
            self.find_and_click(By.CLASS_NAME, config.JOIN_SECTION_BUTTON_CLASS, "botón de join section")

            try:
                response_modal = self.driver.find_element(By.CLASS_NAME, config.NOTIFICATION_MODAL)
                if response_modal:
                    if ("Success" in response_modal.text.lower() or "have " in response_modal.text.lower()):
                        print("Se unio a la seccion con exito")
                        return True
                    elif ("Couldn't" in response_modal.text.lower() or "doesn't" in response_modal.text.lower()):
                        print("Error al asignar la seccion")
                        return False
            except Exception as e:
                print(f"Fallo al asignar la seccion: {e}")
                return False

            # Esperar un poco a que la página responda
            time.sleep(2)

            return True

        except Exception as e:
            print(f"Fallo al unirse a la seccion: {e}")
            self.driver.save_screenshot("error_creacion_cuenta.png")
            return False

    def quit_driver(self):
        if self.driver:
            print("Cerrando el navegador...")
            self.driver.quit()
            print("Navegador cerrado.")
