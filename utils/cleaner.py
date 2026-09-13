import re

def clean_code(code: str) -> str:
    """Remove C/C++ comments, tabs, and unnecessary newlines."""
    pat = re.compile(r'(/\*([^*]|(\*+[^*/]))*\*+/)|(//.*)')
    code = re.sub(pat, '', code)
    code = re.sub(r'\n', ' ', code)
    code = re.sub(r'\t', ' ', code)
    return code.strip()
