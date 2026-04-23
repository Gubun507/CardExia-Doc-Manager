import re
import sympy
from src.core.brain_engine import BrainEngine

class MathSolver:
    @staticmethod
    def solve_math_in_text(text):
        """
        Escanea el texto línea por línea usando el Cerebro Interno para detectar 
        lenguaje natural financiero y resolver las ecuaciones subyacentes.
        """
        pattern = r'(?<![\w\.])[\(\s]*(?:\d{1,3}(?:,\d{3})*|\d+)(?:\.\d+)?[\)\s]*(?:[\+\-\*\/\^xX][\(\s]*(?:\d{1,3}(?:,\d{3})*|\d+)(?:\.\d+)?[\)\s]*)+(?![\w\.])'
        
        results = []
        lines = text.split('\n')
        
        for idx, line in enumerate(lines):
            if not line.strip():
                continue
                
            # 1. El Cerebro traduce finanzas humanas a matemáticas puras
            brain_line = BrainEngine.translate_financial_nlp(line)
            
            # 2. Buscamos los patrones en la línea traducida
            matches = re.finditer(pattern, brain_line)
            
            line_results = []
            for match in matches:
                expr_str = match.group(0).strip()
                
                # Ignorar fechas o IPs (falsos positivos)
                if re.match(r'^\d{1,4}[-/]\d{1,2}[-/]\d{1,4}$', expr_str.replace(" ", "")) or \
                   re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', expr_str.replace(" ", "")):
                    continue

                try:
                    safe_expr_str = expr_str.replace(',', '').replace('^', '**').replace('x', '*').replace('X', '*')
                    expr = sympy.parse_expr(safe_expr_str, evaluate=True)
                    
                    if expr.is_number:
                        val = float(expr)
                        val_str = f"{val:g}"
                        
                        line_results.append({
                            'expression': expr_str,
                            'result': val_str
                        })
                except Exception:
                    continue
            
            if line_results:
                results.append({
                    'line_idx': idx,
                    'calculations': line_results
                })
                
        return results
