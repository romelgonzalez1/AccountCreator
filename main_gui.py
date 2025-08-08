import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import pandas as pd
import threading
import time
import random
import os
import sys
from tksheet import Sheet

from account_creator import AccountCreator

def resource_path(relative_path):
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- DEFINICIÓN DE ESTILO VISUAL (Colores y Fuentes) ---
COLORS = {
    "bg_main": "#F8F9FA",
    "primary": "#34495E",
    "primary_hover": "#4A627E",
    "text_dark": "#212529",
    "text_light": "#FFFFFF",
    "text_secondary": "#6C757D",
    "highlight_processing": "#FFF3CD",
    "highlight_success": "#D4EDDA",
    "highlight_error": "#F8D7DA",
}

FONTS = {
    "title": ("Segoe UI", 18, "bold"),
    "body": ("Segoe UI", 10, "normal"),
    "button": ("Segoe UI", 10, "bold"),
}

# --- CLASE PRINCIPAL DE LA APLICACIÓN GUI ---
class AccountCreatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Automatizador de Creación de Cuentas")
        self.geometry("900x600")
        self.configure(bg=COLORS["bg_main"])

        self.dataframe = None
        self.excel_file_path = "datos_cuentas.xlsx"

        self.setup_styles()
        self.create_widgets()
        self.load_existing_data()

    def setup_styles(self):
        """Configura los estilos personalizados para los widgets ttk."""
        style = ttk.Style(self)
        style.theme_use('clam')

        # Estilos para botones
        style.configure('Primary.TButton', background=COLORS["primary"], foreground=COLORS["text_light"], font=FONTS["button"], padding=(10, 8), borderwidth=0, relief=tk.FLAT)
        style.map('Primary.TButton', background=[('active', COLORS["primary_hover"]), ('disabled', COLORS["text_secondary"])])
        
        style.configure('Secondary.TButton', background=COLORS["bg_main"], foreground=COLORS["text_dark"], font=FONTS["button"], padding=(10, 8), borderwidth=1, bordercolor=COLORS["text_secondary"], relief=tk.SOLID)
        style.map('Secondary.TButton', background=[('active', "#EAECEE")])
        
        # Estilos generales para Frames, Labels, etc.
        style.configure('TFrame', background=COLORS["bg_main"])
        style.configure('TLabelframe', background=COLORS["bg_main"], borderwidth=0, relief=tk.FLAT)
        style.configure('TLabelframe.Label', background=COLORS["bg_main"], foreground=COLORS["text_dark"], font=FONTS["title"])
        style.configure('TLabel', background=COLORS["bg_main"], foreground=COLORS["text_dark"], font=FONTS["body"])
        style.configure('Status.TLabel', background=COLORS["primary"], foreground=COLORS["text_light"], font=FONTS["body"])

    def create_widgets(self):
        """Crea la interfaz de usuario con una estructura simple de una columna."""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Controles Superiores ---
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 15))

        self.load_button = ttk.Button(controls_frame, text="Cargar Archivo Excel", command=self.load_excel_file, style='Secondary.TButton')
        self.load_button.pack(side=tk.LEFT, padx=(0, 10))

        self.start_button = ttk.Button(controls_frame, text="Iniciar Proceso", command=self.start_processing_thread, state="disabled", style='Primary.TButton')
        self.start_button.pack(side=tk.LEFT)

        # --- Tabla de Datos ---
        table_frame = ttk.LabelFrame(main_frame, text="Datos de Cuentas")
        table_frame.pack(fill=tk.BOTH, expand=True)

        self.sheet = Sheet(table_frame)
        self.sheet.set_options(table_grid_fg=COLORS["bg_main"])
        self.sheet.change_theme("light blue")
        self.sheet.pack(fill=tk.BOTH, expand=True)
        self.sheet.enable_bindings("auto_resize_columns", "column_drag_and_drop")
        
        # --- Barra de Estado Inferior ---
        self.status_bar = ttk.Label(self, text="Listo. Cargue un archivo Excel para comenzar.", relief=tk.FLAT, anchor=tk.W, style='Status.TLabel', padding=(10, 5))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_data(self, filepath):
        try:
            temp_df = pd.read_excel(filepath)
            
            # CORRECCIÓN: Reemplazar valores NaN (Not a Number) por strings vacíos para una vista limpia
            self.dataframe = temp_df.fillna('')

            required_cols = ['Correo', 'Contrasena', 'Nombre', 'Genero', 'CodigoSeccion']
            if not all(col in self.dataframe.columns for col in required_cols):
                messagebox.showerror("Error de Formato", f"El archivo Excel debe contener las columnas: {', '.join(required_cols)}")
                return

            # Añadir columnas de estado si no existen (ahora sobre el DataFrame limpio)
            if 'Status' not in self.dataframe.columns: self.dataframe['Status'] = ''
            if 'Mensaje' not in self.dataframe.columns: self.dataframe['Mensaje'] = ''
            
            self.dataframe.to_excel(self.excel_file_path, index=False)
            
            self.display_dataframe()
            self.start_button.config(state="normal")
            self.update_status(f"Archivo '{os.path.basename(filepath)}' cargado. Listo para iniciar.")

        except Exception as e:
            messagebox.showerror("Error al Cargar", f"No se pudo cargar o procesar el archivo:\n{e}")
            self.update_status("Error al cargar el archivo.")

    def display_dataframe(self):
        if self.dataframe is not None:
            self.sheet.set_sheet_data(data=[])
            headers = list(self.dataframe.columns)
            self.sheet.headers(headers)
            self.sheet.set_sheet_data(data=self.dataframe.values.tolist())
            self.sheet.align(align="w") # Alinear texto a la izquierda
            # Ajustar anchos manualmente para mejor visualización
            try:
                self.sheet.set_column_widths([200, 100, 150, 80, 120, 80, 250])
            except:
                pass # No falla si hay menos columnas

    # --- El resto de las funciones de lógica no cambian ---
    def highlight_row(self, row_index, color_key):
        color_map = {
            "processing": COLORS["highlight_processing"],
            "success": COLORS["highlight_success"],
            "error": COLORS["highlight_error"],
            "skipped": "#EAECEE"
        }
        self.sheet.highlight_rows(rows=[row_index], bg=color_map.get(color_key, "#FFFFFF"), redraw=True)

    def update_row_in_gui(self, row_index, status, message):
        status_col_index = self.dataframe.columns.get_loc('Status')
        message_col_index = self.dataframe.columns.get_loc('Mensaje')
        
        self.sheet.set_cell_data(row_index, status_col_index, status, redraw=False)
        self.sheet.set_cell_data(row_index, message_col_index, message, redraw=True)
        
        color_key = "success" if status == "Éxito" else "error"
        self.highlight_row(row_index, color_key)
        
    def run_account_creation_logic(self):
        headless_mode = False

        for index, row in self.dataframe.iterrows():
            if str(row.get('Status')).strip() == 'Éxito':
                self.update_status(f"Saltando: {row['Correo']} (ya procesada)")
                self.after(0, self.highlight_row, index, "skipped")
                time.sleep(0.1)
                continue

            self.after(0, self.highlight_row, index, "processing")
            self.update_status(f"Procesando: {row['Correo']}...")

            status_final = "Error"
            mensaje_final = ""
            creator = None
            
            try:
                # Creamos la ruta correcta para chromedriver.exe
                driver_path = resource_path("chromedriver.exe")
                
                # Pasamos la ruta del driver al constructor de AccountCreator
                creator = AccountCreator(headless=headless_mode, driver_path=driver_path)
                
                email = row['Correo']
                password = str(row['Contrasena'])
                display_name = row['Nombre']
                gender = row['Genero']
                section_code = row['CodigoSeccion']

                creator.open_page()
                success = creator.create_account(email, password, display_name, "15", gender)
                
                if success:
                    joined = creator.join_section(section_code)
                    if joined:
                        status_final = "Éxito"
                        mensaje_final = "Cuenta creada y unida a la sección."
                    else:
                        mensaje_final = "Creada/Logueada, pero falló al unirse a la sección."
                else:
                    mensaje_final = "Fallo en creación/login de cuenta."

            except Exception as e:
                mensaje_final = f"Excepción: {str(e).splitlines()[0]}"
            finally:
                if creator:
                    creator.quit_driver()
                
                self.dataframe.loc[index, 'Status'] = status_final
                self.dataframe.loc[index, 'Mensaje'] = mensaje_final
                
                self.after(0, self.update_row_in_gui, index, status_final, mensaje_final)

                try:
                    self.dataframe.to_excel(self.excel_file_path, index=False)
                except PermissionError:
                    self.update_status("¡ERROR! Cierre el archivo Excel para poder guardar el progreso.")
                    messagebox.showwarning("Archivo Abierto", "Por favor, cierre el archivo Excel para que el programa pueda guardar los resultados.")
            
            if index < len(self.dataframe) - 1:
                sleep_time = random.randint(5, 10)
                self.update_status(f"Pausa de {sleep_time} segundos...")
                time.sleep(sleep_time)

        self.update_status("¡Proceso completado! Revisa los resultados.")
        self.after(0, self.enable_buttons)
    
    def load_existing_data(self):
        if os.path.exists(self.excel_file_path):
            self.update_status(f"Cargando datos existentes de '{self.excel_file_path}'...")
            self.load_data(self.excel_file_path)

    def load_excel_file(self):
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=(("Archivos de Excel", "*.xlsx"), ("Todos los archivos", "*.*"))
        )
        if not filepath:
            return
        
        self.excel_file_path = filepath
        self.load_data(filepath)

    def update_status(self, message):
        self.status_bar.config(text=message)
        self.update_idletasks()

    def start_processing_thread(self):
        self.start_button.config(state="disabled")
        self.load_button.config(state="disabled")
        self.update_status("Iniciando proceso...")

        processing_thread = threading.Thread(target=self.run_account_creation_logic, daemon=True)
        processing_thread.start()
        
    def enable_buttons(self):
        self.start_button.config(state="normal")
        self.load_button.config(state="normal")

# --- PUNTO DE ENTRADA DE LA APLICACIÓN ---
if __name__ == "__main__":
    app = AccountCreatorApp()
    app.mainloop()