import pandas as pd
import os

# Try to find the file
filename = 'Diseño Inicial.xlsx'
paths_to_check = [
    filename,
    os.path.join('mi_juego', filename),
    os.path.join('..', filename)
]

found_path = None
for path in paths_to_check:
    if os.path.exists(path):
        found_path = path
        break

if not found_path:
    print(f"Error: Could not find {filename}")
    exit(1)

print(f"File found at: {found_path}")

try:
    xl = pd.ExcelFile(found_path)
    
    # Analyze 'Elementos' sheet deeper
    if 'Elementos' in xl.sheet_names:
        print("\n--- Sheet: Elementos (First 50 rows) ---")
        df = pd.read_excel(found_path, sheet_name='Elementos', header=None) # No header to see raw layout
        print(df.head(50).to_string())

    # Analyze 'Tablas' sheet
    if 'Tablas' in xl.sheet_names:
        print("\n--- Sheet: Tablas (First 20 rows) ---")
        df = pd.read_excel(found_path, sheet_name='Tablas', header=None)
        print(df.head(20).to_string())

except Exception as e:
    print(f"Error reading Excel file: {e}")
