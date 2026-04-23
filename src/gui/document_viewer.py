import customtkinter as ctk
import os
from src.core.math_solver import MathSolver

class DocumentViewer(ctk.CTkToplevel):
    def __init__(self, master, file_path, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.file_path = file_path
        self.title(f"Visor Seguro - {os.path.basename(file_path)}")
        self.geometry("900x750")
        
        # Tema Neón Oscuro y Transparencia
        self.configure(fg_color="#0A0A12")
        try:
            self.attributes("-alpha", 0.95)
        except Exception:
            pass
            
        self.original_content = ""
        self.showing_math = False
        
        self._build_ui()
        self._load_document()

    def _build_ui(self):
        # Toolbar Neón
        self.toolbar = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#121220", border_width=1, border_color="#00E5FF")
        self.toolbar.pack(fill="x", padx=10, pady=(10,0))
        
        self.math_btn = ctk.CTkButton(
            self.toolbar, 
            text="[ ] EVALUAR MATEMÁTICAS", 
            command=self.toggle_math,
            font=ctk.CTkFont(family="Consolas", weight="bold"),
            fg_color="transparent",
            border_color="#00E5FF",
            border_width=2,
            text_color="#00E5FF",
            hover_color="#00E5FF",
            corner_radius=4
        )
        self.math_btn.bind("<Enter>", lambda e: self.math_btn.configure(text_color="#0A0A12") if not self.showing_math else None)
        self.math_btn.bind("<Leave>", lambda e: self.math_btn.configure(text_color="#00E5FF") if not self.showing_math else None)
        self.math_btn.pack(side="right", padx=15, pady=10)
        
        self.file_label = ctk.CTkLabel(
            self.toolbar, 
            text=f"TARGET: {self.file_path}", 
            text_color="#00E5FF",
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.file_label.pack(side="left", padx=15, pady=10)

        # Editor/Viewer
        self.textbox = ctk.CTkTextbox(
            self, 
            wrap="word", 
            font=("Consolas", 15),
            fg_color="#08080E",
            text_color="#E0E0E0",
            border_color="#00E5FF",
            border_width=1,
            scrollbar_button_color="#00E5FF",
            scrollbar_button_hover_color="#FF007F"
        )
        self.textbox.pack(fill="both", expand=True, padx=10, pady=10)

    def _load_document(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.original_content = f.read()
        except UnicodeDecodeError:
            try:
                with open(self.file_path, 'r', encoding='latin-1') as f:
                    self.original_content = f.read()
            except Exception as e:
                self.original_content = f"// ERROR DE LECTURA //\nDetalle: {e}"
        except Exception as e:
            self.original_content = f"// FALLA DE APERTURA //\n{e}"
            
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
                self.math_btn.configure(text="[!] NO DATA", border_color="#FF007F", text_color="#FF007F")
                self.after(2000, lambda: self.math_btn.configure(text="[ ] EVALUAR MATEMÁTICAS", border_color="#00E5FF", text_color="#00E5FF"))
                return
                
            # Inyectar
            new_text = ""
            last_idx = 0
            
            for res in results:
                start = res['start']
                end = res['end']
                val = res['result']
                
                new_text += self.original_content[last_idx:end]
                # Estilo de respuesta
                new_text += f"  ==> [ {val} ]"
                last_idx = end
                
            new_text += self.original_content[last_idx:]
            
            self._update_text(new_text)
            self.showing_math = True
            self.math_btn.configure(
                text="[X] RESULTADOS VISIBLES", 
                fg_color="#39FF14", 
                border_color="#39FF14",
                text_color="#0A0A12",
                hover_color="#2ECC10"
            )
            # Quitar eventos de hover de cyan
            self.math_btn.unbind("<Enter>")
            self.math_btn.unbind("<Leave>")
            
        else:
            # Ocultar
            self._update_text(self.original_content)
            self.showing_math = False
            self.math_btn.configure(
                text="[ ] EVALUAR MATEMÁTICAS", 
                fg_color="transparent", 
                border_color="#00E5FF",
                text_color="#00E5FF",
                hover_color="#00E5FF"
            )
            # Restaurar hover
            self.math_btn.bind("<Enter>", lambda e: self.math_btn.configure(text_color="#0A0A12") if not self.showing_math else None)
            self.math_btn.bind("<Leave>", lambda e: self.math_btn.configure(text_color="#00E5FF") if not self.showing_math else None)
