import os
from pypdf import PdfReader
from docx import Document
from fpdf import FPDF

class DocumentHandler:
    @staticmethod
    def read_text(file_path):
        """Extrae texto de archivos .pdf, .docx o planos."""
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == '.pdf':
                return DocumentHandler._read_pdf(file_path)
            elif ext == '.docx' or ext == '.doc':
                return DocumentHandler._read_docx(file_path)
            else:
                return DocumentHandler._read_plain(file_path)
        except Exception as e:
            return f"// ERROR DE LECTURA DE SISTEMA //\nEl formato no pudo ser parseado.\nDetalle: {e}"

    @staticmethod
    def _read_pdf(file_path):
        reader = PdfReader(file_path)
        text = ""
        for i, page in enumerate(reader.pages):
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text

    @staticmethod
    def _read_docx(file_path):
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    @staticmethod
    def _read_plain(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()

    @staticmethod
    def save_plain_text(file_path, text):
        """Sobreescribe un archivo plano. Peligroso si se usa en PDF/DOCX originales."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)

    @staticmethod
    def export_to_pdf(original_path, text):
        """
        Genera un documento PDF nuevo (ej: Factura_CEDM.pdf) para evitar corromper 
        el archivo fuente original, garantizando la preservación de los datos iniciales.
        """
        base_name, _ = os.path.splitext(original_path)
        new_path = f"{base_name}_CEDM.pdf"
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Helvetica", size=11)
        
        # Sanitización forzada para la fuente core de FPDF (latin-1)
        safe_text = text.encode('latin-1', 'replace').decode('latin-1')
        
        # multi_cell se encarga del wrap de palabras
        pdf.multi_cell(0, 6, safe_text)
        pdf.output(new_path)
        
        return new_path
