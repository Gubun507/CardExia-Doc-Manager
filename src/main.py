import os
import sys
import customtkinter as ctk
import threading
from tkinter import filedialog, messagebox

# Añadir src al path si ejecutamos desde raíz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.search_engine import SearchEngine
from src.core.indexer import FileIndexer
from src.gui.document_viewer import DocumentViewer

# Forzar tema oscuro general
ctk.set_appearance_mode("dark")

class CardExiaSmartSearch(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CardExia Doc-Manager - Búsqueda Predictiva Universal")
        self.geometry("1100x700")

        # Configuración de Tema Neón y Transparencia
        self.configure(fg_color="#0A0A12") # Fondo ultra oscuro
        try:
            self.attributes("-alpha", 0.93) # Semi-transparencia
        except Exception:
            pass # En caso de que el SO no soporte alpha

        # Motores Core
        self.search_engine = SearchEngine('cardexia_index.db')
        self.indexer = FileIndexer(self.search_engine)
        self.debounce_timer = None
        
        self._build_ui()
        self._update_status()

    def _build_ui(self):
        # Header Frame
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Título Neón
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="CARDEXIA // DOC-MANAGER", 
            font=ctk.CTkFont(family="Consolas", size=26, weight="bold"),
            text_color="#00E5FF" # Cyan Neón
        )
        self.title_label.pack(side="left")

        # Botón Escanear
        self.index_btn = ctk.CTkButton(
            self.header_frame, 
            text="⚡ Escanear Sistema", 
            command=self.request_index_permission,
            font=ctk.CTkFont(weight="bold"),
            fg_color="#FF007F", # Magenta Neón
            hover_color="#CC0066",
            text_color="#FFFFFF",
            corner_radius=8
        )
        self.index_btn.pack(side="right")

        # Barra de Búsqueda Neón
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.on_search_type)
        
        self.entry = ctk.CTkEntry(
            self, 
            placeholder_text="Inicia la búsqueda predictiva (ej: Factura.pdf, Reporte)...",
            placeholder_text_color="#007A88",
            textvariable=self.search_var,
            font=ctk.CTkFont(size=20),
            height=55,
            fg_color="#121220",
            border_color="#00E5FF",
            border_width=2,
            text_color="#00E5FF",
            corner_radius=12
        )
        self.entry.pack(fill="x", padx=20, pady=15)

        # Status Label
        self.status_label = ctk.CTkLabel(
            self, 
            text="SISTEMA EN LÍNEA. ESPERANDO CONSULTA...", 
            text_color="#39FF14", # Verde Neón
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.status_label.pack(anchor="w", padx=25)

        # Resultados (Lista Scrolleable) con scrollbars neón
        self.results_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#08080E",
            scrollbar_button_color="#00E5FF",
            scrollbar_button_hover_color="#FF007F",
            corner_radius=10
        )
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

    def _update_status(self):
        count = self.search_engine.count_documents()
        if self.indexer.is_indexing:
            self.status_label.configure(
                text=f"// RASTREANDO DIRECTORIOS... [{self.indexer.total_scanned} ARCHIVOS] // [{count} EN DB]",
                text_color="#FF007F"
            )
            self.after(800, self._update_status)
        else:
            self.status_label.configure(
                text=f"// ÍNDICE ACTIVO // {count} DOCUMENTOS DISPONIBLES",
                text_color="#39FF14"
            )

    def request_index_permission(self):
        if self.indexer.is_indexing:
            return

        resp = messagebox.askyesno(
            "Autorización Requerida", 
            "Iniciando protocolo de rastreo predictivo.\n\n"
            "Se requiere acceso a la jerarquía de archivos para construir el índice.\n"
            "¿Deseas seleccionar el punto de montaje/directorio?"
        )
        
        if resp:
            folder = filedialog.askdirectory(title="Seleccionar Punto de Montaje")
            if folder:
                self.indexer.start_indexing(folder, callback=self.on_index_complete)
                self.index_btn.configure(state="disabled", text="Rastreando...")
                self._update_status()

    def on_index_complete(self, total_scanned):
        self.index_btn.configure(state="normal", text="⚡ Actualizar Índice")
        self._update_status()
        self.execute_search()

    def on_search_type(self, *args):
        if self.debounce_timer is not None:
            self.after_cancel(self.debounce_timer)
        self.debounce_timer = self.after(250, self.execute_search)

    def execute_search(self):
        query = self.search_var.get().strip()
        
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if len(query) < 2:
            return

        results = self.search_engine.search(query, limit=20)
        
        if not results:
            lbl = ctk.CTkLabel(self.results_frame, text="NO MATCH FOUND", text_color="#FF007F", font=ctk.CTkFont(family="Consolas"))
            lbl.pack(pady=20)
            return

        for name, path, mtime in results:
            row = ctk.CTkFrame(
                self.results_frame, 
                fg_color="#121220", 
                border_color="#00E5FF", 
                border_width=1,
                corner_radius=8
            )
            row.pack(fill="x", pady=4, padx=5)
            
            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=8)
            
            name_lbl = ctk.CTkLabel(
                info_frame, 
                text=name, 
                font=ctk.CTkFont(weight="bold", size=14), 
                text_color="#E0E0E0",
                anchor="w"
            )
            name_lbl.pack(fill="x")
            
            path_lbl = ctk.CTkLabel(
                info_frame, 
                text=f"{mtime} | {path}", 
                text_color="#A0A0B0", 
                font=ctk.CTkFont(size=11), 
                anchor="w"
            )
            path_lbl.pack(fill="x")
            
            open_btn = ctk.CTkButton(
                row, 
                text="[ LEER DOC ]", 
                width=110,
                font=ctk.CTkFont(weight="bold", size=11),
                fg_color="transparent",
                border_color="#39FF14",
                border_width=1,
                text_color="#39FF14",
                hover_color="#39FF14",
                command=lambda p=path: self.open_document(p)
            )
            open_btn.bind("<Enter>", lambda e, b=open_btn: b.configure(text_color="#0A0A12"))
            open_btn.bind("<Leave>", lambda e, b=open_btn: b.configure(text_color="#39FF14"))
            open_btn.pack(side="right", padx=10)

            calc_btn = ctk.CTkButton(
                row, 
                text="[ 🖩 CALCULAR ]", 
                width=110,
                font=ctk.CTkFont(weight="bold", size=11),
                fg_color="transparent",
                border_color="#00E5FF",
                border_width=1,
                text_color="#00E5FF",
                hover_color="#00E5FF",
                command=lambda p=path: self.open_document(p, auto_math_mode=True)
            )
            calc_btn.bind("<Enter>", lambda e, b=calc_btn: b.configure(text_color="#0A0A12"))
            calc_btn.bind("<Leave>", lambda e, b=calc_btn: b.configure(text_color="#00E5FF"))
            calc_btn.pack(side="right", padx=5)

    def open_document(self, path, auto_math_mode=False):
        if not os.path.exists(path):
            messagebox.showerror("Error", "El archivo ya no existe.")
            return
            
        viewer = DocumentViewer(self, path, auto_math_mode=auto_math_mode)
        viewer.focus()

if __name__ == "__main__":
    app = CardExiaSmartSearch()
    app.mainloop()
