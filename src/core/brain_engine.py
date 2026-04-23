import re

class BrainEngine:
    """
    Cerebro cognitivo interno ligero. 
    Funciona sin dependencias pesadas para compilaciones rápidas,
    usando procesamiento léxico y diccionarios de memoria semántica.
    """

    # Memoria Semántica para expansión de búsquedas
    # Mapea conceptos a sus posibles sinónimos en español/inglés corporativo
    SEMANTIC_MEMORY = {
        # Documentos y Archivos
        "factura": ["factura", "recibo", "invoice", "comprobante", "ticket", "cobro", "boleta", "voucher"],
        "contrato": ["contrato", "acuerdo", "contract", "convenio", "pacto", "ndf", "alianza", "licencia"],
        "reporte": ["reporte", "informe", "report", "balance", "analisis", "estadistica", "auditoria"],
        "cotizacion": ["cotizacion", "presupuesto", "estimacion", "oferta", "proforma"],
        
        # Activos y Finanzas
        "dinero": ["dinero", "pago", "cash", "efectivo", "transferencia", "deposito", "saldo", "capital", "fondo", "divisa"],
        "ingreso": ["ingreso", "venta", "ganancia", "beneficio", "rentabilidad", "utilidad", "revenue"],
        "gasto": ["gasto", "egreso", "costo", "perdida", "compra", "deuda", "pasivo"],
        "impuesto": ["impuesto", "iva", "tax", "tributo", "retencion", "arancel", "aduana"],
        "nomina": ["nomina", "salario", "sueldo", "pago", "empleado", "honorarios"],
        
        # Objetos físicos comunes en reportes
        "auto": ["auto", "coche", "vehiculo", "carro", "camioneta", "motor", "transporte", "flota"],
        "inmueble": ["inmueble", "casa", "edificio", "oficina", "propiedad", "local", "bodega", "terreno"]
    }

    @classmethod
    def build_fts5_query(cls, query):
        """
        Analiza la búsqueda y genera una consulta estructurada FTS5.
        Ej: "factura auto" -> "(factura* OR recibo*...) AND (auto* OR coche*...)"
        """
        words = query.lower().replace("'", "").replace('"', '').split()
        fts_groups = []

        for word in words:
            found_syns = [word]
            for concept, synonyms in cls.SEMANTIC_MEMORY.items():
                if word in synonyms or word == concept:
                    found_syns.extend(synonyms)
            
            # Bloque condicional para esta palabra semántica
            unique_syns = list(set(found_syns))
            group_str = " OR ".join([f"{s}*" for s in unique_syns])
            fts_groups.append(f"({group_str})")
        
        return " AND ".join(fts_groups)

    @classmethod
    def translate_financial_nlp(cls, text):
        """
        Traductor de Lenguaje Natural a Lógica Matemática.
        """
        processed = text.lower()
        
        # Limpieza básica de conectores
        processed = processed.replace(" el ", " ")
        processed = processed.replace(" la ", " ")
        processed = processed.replace(" de iva", "")
        
        # Convertir palabras a operadores
        processed = processed.replace(" mas ", " + ")
        processed = processed.replace(" menos ", " - ")
        processed = processed.replace(" por ", " * ")
        processed = processed.replace(" entre ", " / ")
        
        # 1. Porcentajes: "15% de 1000" -> "15 / 100 * 1000"
        processed = re.sub(r'(\d+(?:\.\d+)?)%\s*(?:de|del)\s*(\d+(?:\.\d+)?)', r'(\1 / 100 * \2)', processed)
        
        # 2. Sumar IVA/Impuestos: "1000 + 16%"
        processed = re.sub(r'(\d+(?:\.\d+)?)\s*\+\s*(\d+(?:\.\d+)?)%', r'(\1 * (1 + \2 / 100))', processed)
        
        # 3. Descontar: "1000 - 15%"
        processed = re.sub(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)%', r'(\1 * (1 - \2 / 100))', processed)
        
        # 4. Lenguaje natural matemático simple
        processed = processed.replace("mitad de", "0.5 *")
        processed = processed.replace("doble de", "2 *")
        processed = processed.replace("triple de", "3 *")
        processed = processed.replace("cuarto de", "0.25 *")
        
        return processed
