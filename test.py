import pandas as pd
import json
import ast

# Cargar el archivo Excel
datacsv = pd.read_excel('C:/Users/genesys/Downloads/data_flujo.xlsx'
                        ,sheet_name="data_flujo"
                        ,engine='openpyxl')

# Primero, veamos qué hay en la primera fila de la columna
print("Tipo de dato en la columna:", type(datacsv['Salida del desencadenador'].iloc[0]))
print("\nPrimeros 500 caracteres del contenido:")
print(datacsv['Salida del desencadenador'].iloc[0][:500])
print("\n" + "="*50)

# Función mejorada para extraer el request_id
def extraer_request_id(valor):
    try:
        print(f"Procesando valor de tipo: {type(valor)}")
        
        # Si es NaN o None
        if pd.isna(valor):
            return None
        
        # Si ya es un diccionario (pandas a veces carga JSON como dict)
        if isinstance(valor, dict):
            print("Ya es un diccionario")
            return valor.get('body', {}).get('request_id')
        
        # Si es string
        if isinstance(valor, str):
            print(f"Longitud del string: {len(valor)}")
            
            # Intentar varios métodos de parseo
            
            # Método 1: json.loads directo
            try:
                data = json.loads(valor)
                print("Parseado con json.loads")
                return data.get('body', {}).get('request_id')
            except json.JSONDecodeError as e1:
                print(f"json.loads falló: {e1}")
            
            # Método 2: ast.literal_eval para strings de diccionario
            try:
                data = ast.literal_eval(valor)
                print("Parseado con ast.literal_eval")
                return data.get('body', {}).get('request_id')
            except (SyntaxError, ValueError) as e2:
                print(f"ast.literal_eval falló: {e2}")
            
            # Método 3: buscar el request_id con expresión regular (último recurso)
            import re
            pattern = r'"request_id"\s*:\s*"([a-f0-9]+)"'
            match = re.search(pattern, valor, re.IGNORECASE)
            if match:
                print("Encontrado con regex")
                return match.group(1)
            
            # Método 4: si tiene formato multilínea, limpiarlo
            try:
                # Limpiar posibles problemas de encoding
                cleaned = valor.strip()
                # Reemplazar comillas simples por dobles si es necesario
                if cleaned.startswith("'") and cleaned.endswith("'"):
                    cleaned = cleaned[1:-1]
                data = json.loads(cleaned)
                print("Parseado después de limpieza")
                return data.get('body', {}).get('request_id')
            except Exception as e4:
                print(f"Parseo con limpieza falló: {e4}")
        
        return None
        
    except Exception as e:
        print(f"Error general: {e}")
        return None

# Probar con la primera fila
print("\nProbando extracción en primera fila:")
resultado = extraer_request_id(datacsv['Salida del desencadenador'].iloc[0])
print(f"\nResultado: {resultado}")

# Si funciona, procesar toda la columna
if resultado:
    print("\nProcesando toda la columna...")
    datacsv['request_id_extraido'] = datacsv['Salida del desencadenador'].apply(extraer_request_id)
    
    # Mostrar resultados
    print("\nPrimeras filas con request_id extraído:")
    print(datacsv[['Salida del desencadenador', 'request_id_extraido']].head())
    
    datacsv = datacsv[['Hora de inicio de la ejecuciÃ³n','Hora de finalizaciÃ³n de la ejecuciÃ³n',
                       'Id. de ejecuciÃ³n','Estado de la ejecuciÃ³n',
                       'Mensaje de error de ejecuciÃ³n','VÃ­nculo de la ejecuciÃ³n',
                        'Estado del desencadenador','Entrada del desencadenador',
                        'Salida del desencadenador','Hora de inicio del desencadenador',
                        'Hora de finalizaciÃ³n del desencadenador',
                        'mensaje_auto: estado','request_id_extraido']]
    # Guardar en nuevo archivo
    datacsv.to_excel('C:/Users/genesys/Downloads/data_flujo_con_request_id.xlsx'
                     , index=False
                     ,engine='openpyxl')
else:
    # Si no funciona, mostrar más detalles del contenido
    print("\nContenido completo de la primera fila:")
    print(datacsv['Salida del desencadenador'].iloc[0])

