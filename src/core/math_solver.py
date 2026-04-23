import re
import sympy

class MathSolver:
    @staticmethod
    def solve_math_in_text(text):
        """
        Escanea el texto buscando patrones matemáticos.
        Retorna una lista de diccionarios con el inicio, fin, expresión y resultado.
        """
        # Expresión regular para encontrar posibles operaciones matemáticas
        # Busca números (enteros o decimales), seguidos de al menos un operador y otro número.
        # Permite paréntesis y espacios.
        pattern = r'(?<![\w\.])(?:[\(\s]*(?:\d+(?:\.\d+)?)[\)\s]*)(?:(?:[\+\-\*\/\^])[\(\s]*(?:\d+(?:\.\d+)?)[\)\s]*)+(?![\w\.])'
        
        matches = re.finditer(pattern, text)
        results = []
        
        for match in matches:
            expr_str = match.group(0).strip()
            
            # Filtros de falsos positivos
            if not expr_str:
                continue
            
            # Ignorar posibles fechas, IPs o números de teléfono (ej. 2023-10-12)
            if re.match(r'^\d{1,4}[-/]\d{1,2}[-/]\d{1,4}$', expr_str.replace(" ", "")):
                continue
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', expr_str.replace(" ", "")):
                continue

            try:
                # Usar SymPy para evaluar la expresión de forma segura
                # Convertir ^ a ** para potencias en Python si las hay
                safe_expr_str = expr_str.replace('^', '**')
                
                # Parsear y evaluar
                expr = sympy.parse_expr(safe_expr_str, evaluate=True)
                
                if expr.is_number:
                    val = float(expr)
                    val_str = f"{val:g}" # formatea sin ceros inútiles
                    
                    results.append({
                        'start': match.start(),
                        'end': match.end(),
                        'expression': expr_str,
                        'result': val_str
                    })
            except Exception:
                # Si falla el parseo (ejemplo: es un string malformado), simplemente lo ignoramos
                pass
                
        return results
