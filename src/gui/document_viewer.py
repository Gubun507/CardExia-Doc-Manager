import customtkinter as ctk
import os
from tkinter import messagebox
from src.core.math_solver import MathSolver
from src.core.document_handler import DocumentHandler

class DocumentViewer(ctk.CTkToplevel):
    def __init__(self, master, file_path, auto_math_mode=False, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.file_path = file_path
        self.title(f"Editor Universal - {os.path.basename(file_path)}")
        self.geometry("950x800")
        
        self.configure(fg_color="#0A0A12")
        try:
            self.attributes("-alpha", 0.95)
        except Exception:
            pass
            
        self.original_content = ""
        self.showing_math = False
        
        self._build_ui()
        self._load_document()
        
        if auto_math_mode:
            # Ligero delay para asegurar que el UI se renderizó antes de activar el cálculo pesado
            self.after(300, self.toggle_math)

    def _build_ui(self):
        # Top Toolbar para acciones de Guardado
        self.top_bar = ctk.CTkFrame(self, height=45, corner_radius=0, fg_color="#121220")
        self.top_bar.pack(fill="x", padx=10, pady=(10, 0))
        
        self.save_btn = ctk.CTkButton(
            self.top_bar, 
            text="[ GUARDAR TXT ]", 
            command=self.save_document,
            fg_color="#FF007F",
            hover_color="#CC0066",
            font=ctk.CTkFont(weight="bold")
        )
        self.save_btn.pack(side="left", padx=10, pady=8)
        
        self.export_btn = ctk.CTkButton(
            self.top_bar, 
            text="[ EXPORTAR A PDF (CEDM) ]", 
            command=self.export_document,
            fg_color="#00E5FF",
            text_color="#0A0A12",
            hover_color="#00B3CC",
            font=ctk.CTkFont(weight="bold")
        )
        self.export_btn.pack(side="left", padx=10, pady=8)

        # Toolbar Matemática Inferior
        self.math_bar = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#121220", border_width=1, border_color="#00E5FF")
        self.math_bar.pack(fill="x", padx=10, pady=(5,0))
        
        self.math_btn = ctk.CTkButton(
            self.math_bar, 
            text="[ ] MODO CALCULADORA", 
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
            self.math_bar, 
            text=f"TARGET: {os.path.basename(self.file_path)}", 
            text_color="#00E5FF",
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.file_label.pack(side="left", padx=15, pady=10)

        # Editor Multipropósito
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
        text = DocumentHandler.read_text(self.file_path)
        self._update_text(text)
        
        # Desactivar guardado original para PDFs y DOCX
        ext = os.path.splitext(self.file_path)[1].lower()
        if ext in ['.pdf', '.docx', '.doc']:
            self.save_btn.configure(
                state="disabled", 
                text="[ GUARDAR ORIGINAL BLOQUEADO ]",
                fg_color="#333333"
            )

    def _update_text(self, text, is_readonly=False):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.insert("end", text)
        if is_readonly:
            self.textbox.configure(state="disabled")

    def save_document(self):
        # Solo para archivos TXT u otros textos planos
        if self.showing_math:
            messagebox.showwarning("Modo Calculadora", "Desactiva el modo calculadora antes de sobreescribir el archivo original para evitar guardar las superposiciones matemáticas.")
            return
            
        current_text = self.textbox.get("1.0", "end-1c")
        try:
            DocumentHandler.save_plain_text(self.file_path, current_text)
            messagebox.showinfo("Guardado", "Documento guardado exitosamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el documento:\n{e}")

    def export_document(self):
        # Exporta el contenido exacto que se ve en el textbox en este instante
        current_text = self.textbox.get("1.0", "end-1c")
        try:
            new_path = DocumentHandler.export_to_pdf(self.file_path, current_text)
            messagebox.showinfo("Exportación Exitosa", f"Nuevo archivo PDF seguro creado:\n{new_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Falla en la compilación del PDF:\n{e}")

    def toggle_math(self):
        if not self.showing_math:
            # Guardamos lo que el usuario haya editado antes de aplicar matemáticas
            self.original_content = self.textbox.get("1.0", "end-1c")
            
            results = MathSolver.solve_math_in_text(self.original_content)
            
            if not results:
                self.math_btn.configure(text="[!] NO SE DETECTARON FÓRMULAS", border_color="#FF007F", text_color="#FF007F")
                self.after(2000, lambda: self.math_btn.configure(text="[ ] MODO CALCULADORA", border_color="#00E5FF", text_color="#00E5FF"))
                return
                
            new_text = ""
            last_idx = 0
            
            for res in results:
                start = res['start']
                end = res['end']
                val = res['result']
                expr = res['expression']
                
                new_text += self.original_content[last_idx:end]
                # Inyección explícita de fórmula y resultado para verificación del usuario
                new_text += f"\n\n    >>> [Fórmula detectada: {expr} = {val}] <<<\n"
                last_idx = end
                
            new_text += self.original_content[last_idx:]
            
            self._update_text(new_text, is_readonly=True)
            self.showing_math = True
            
            self.math_btn.configure(
                text="[X] MODO CALCULADORA ACTIVO", 
                fg_color="#39FF14", 
                border_color="#39FF14",
                text_color="#0A0A12",
                hover_color="#2ECC10"
            )
            self.math_btn.unbind("<Enter>")
            self.math_btn.unbind("<Leave>")
            
        else:
            # Restaurar el texto y volver a permitir edición
            self._update_text(self.original_content, is_readonly=False)
            self.showing_math = False
            self.math_btn.configure(
                text="[ ] MODO CALCULADORA", 
                fg_color="transparent", 
                border_color="#00E5FF",
                text_color="#00E5FF",
                hover_color="#00E5FF"
            )
            self.math_btn.bind("<Enter>", lambda e: self.math_btn.configure(text_color="#0A0A12") if not self.showing_math else None)
            self.math_btn.bind("<Leave>", lambda e: self.math_btn.configure(text_color="#00E5FF") if not self.showing_math else None)
