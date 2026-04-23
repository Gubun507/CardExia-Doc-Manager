import customtkinter as ctk
import os
from src.core.math_solver import MathSolver

class DocumentViewer(ctk.CTkToplevel):
    def __init__(self, master, file_path, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.file_path = file_path
        self.title(f"Visor de Documentos - {os.path.basename(file_path)}")
        self.geometry("900x700")
        
        self.original_content = ""
        self.showing_math = False
        
        self._build_ui()
        self._load_document()

    def _build_ui(self):
        # Toolbar
        self.toolbar = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.toolbar.pack(fill="x", padx=0, pady=0)
        
        self.math_btn = ctk.CTkButton(
            self.toolbar, 
            text="Resolver Cálculos (Off)", 
            command=self.toggle_math,
            fg_color="#3B8ED0",
            hover_color="#36719F"
        )
        self.math_btn.pack(side="right", padx=10, pady=10)
        
        self.file_label = ctk.CTkLabel(
            self.toolbar, 
            text=f"Ruta: {self.file_path}", 
            text_color="gray"
        )
        self.file_label.pack(side="left", padx=10, pady=10)

        # Editor/Viewer
        self.textbox = ctk.CTkTextbox(self, wrap="word", font=("Consolas", 14))
        self.textbox.pack(fill="both", expand=True, padx=10, pady=10)

    def _load_document(self):
        try:
            # Intentar leer como UTF-8
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.original_content = f.read()
        except UnicodeDecodeError:
            try:
                # Fallback a latin-1 para archivos de Windows comunes
                with open(self.file_path, 'r', encoding='latin-1') as f:
                    self.original_content = f.read()
            except Exception as e:
                self.original_content = f"Error al leer el archivo. (Puede que sea un binario no soportado).\nDetalle: {e}"
        except Exception as e:
            self.original_content = f"Error al abrir el archivo:\n{e}"
            
        self._update_text(self.original_content)

    def _update_text(self, text):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.insert("end", text)
        self.textbox.configure(state="disabled")

    def toggle_math(self):
        if not self.showing_math:
            # Resolver
            results = MathSolver.solve_math_in_text(self.original_content)
            
            if not results:
                # No se encontraron matemáticas
                self.math_btn.configure(text="Sin Cálculos Encontrados")
                self.after(2000, lambda: self.math_btn.configure(text="Resolver Cálculos (Off)"))
                return
                
            # Reconstruir el texto con los resultados inyectados
            new_text = ""
            last_idx = 0
            
            for res in results:
                start = res['start']
                end = res['end']
                val = res['result']
                
                # Añadir el texto original antes del match + el match + el resultado
                new_text += self.original_content[last_idx:end]
                # Inyectar el resultado
                new_text += f" [= {val}]"
                last_idx = end
                
            new_text += self.original_content[last_idx:]
            
            self._update_text(new_text)
            self.showing_math = True
            self.math_btn.configure(text="Ocultar Resultados (On)", fg_color="#2FA572", hover_color="#106A43")
            
        else:
            # Ocultar
            self._update_text(self.original_content)
            self.showing_math = False
            self.math_btn.configure(text="Resolver Cálculos (Off)", fg_color="#3B8ED0", hover_color="#36719F")
