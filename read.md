Sistema de Validación de Equipos – Arquitectura y Flujo Técnico
1. Objetivo del Sistema
Automatizar el proceso de validación de equipos (reportes directos) mediante:
Extracción controlada desde BigQuery (fuente oficial)
Generación dinámica de Adaptive Cards
Envío vía Power Automate (Webhook HTTP)
Persistencia en BigQuery (modelo staging + merge)
Soporte de reprocesamiento idempotente
El sistema está diseñado para evitar duplicidades y permitir ejecuciones parciales o completas.

2. Arquitectura Lógica
2.1 Componentes
Capa	Componente	Responsabilidad
Orquestación	main.py	CLI + ejecución de flujos
Fuente de datos	ListaUsuarios	Query + construcción tarjetas
Utilidades	utills.py	Helpers + reprocesamiento
Integración HTTP	EnvSolicitud	Envío a Power Automate
Persistencia	BigQueryTableRepository	Staging + MERGE
2.2 Flujo End-to-End
BigQuery (Prod)
    ↓
ListaUsuarios.exec_query()
    ↓
Construcción Adaptive Cards
    ↓
Generación request_id (hash)
    ↓
Reprocess (consulta QA)
    ↓
Export Excel / CSV
    ↓
EnvSolicitud.envio_json()
    ↓
Power Automate
    ↓
BigQuery (QA / Persistencia)
3. Orquestación – main.py

Archivo de entrada que controla ejecución manual vía CLI.

Soporta:

Descarga de destinatarios

Carga de respuestas CSV

Reprocesamiento parcial

Flujo completo

No contiene lógica de negocio. Solo coordinación.

4. Fuente de la Verdad – ListaUsuarios

Archivo:
app/teams_validation_service/fuente_de_la_verdad.py

4.1 Query Base

Origen:

tc-sc-bi-bigdata-edp-prod.trf_cor_cl_edp_restricted_prod.acc_btd_cor_emp_headcount_clear
Filtros relevantes

emp_update_period = 202512

Excluye India / China

workplace_unified = casa matriz

Excluye job_subfamily TM-3 y TM-4

Manager con < 25 reportes

Solo último registro por empleado (ROW_NUMBER())

Consideración técnica

Se utiliza QUALIFY ROW_NUMBER() para garantizar última versión del registro sin subqueries adicionales.

4.2 Construcción de Adaptive Card

Por cada manager:

Se agrupan reportes directos.

Se construye dinámicamente el bloque choices.

Se arma JSON completo de Adaptive Card v1.4.

Se convierte a dict y luego a JSON serializado.

Se incluye:

MultiSelect ChoiceSet

Toggle “Falta alguien”

Action.Submit

4.3 Generación de request_id
hashlib.sha256(f"{destinatario}|{mes}".encode())
Propósito

Identificador determinístico

Permite control de duplicidad

Base para MERGE posterior

Observación técnica

Actualmente usa solo month, no fecha completa → puede generar colisiones inter-mensuales futuras.

4.4 Reprocesamiento

Si reprocesar=True:

df_mensajes = reprocess(df_mensajes)

Este paso:

Consulta QA

Evalúa estado de respuestas

Excluye request_id válidos

Permite idempotencia parcial del flujo.

5. Integración HTTP – EnvSolicitud

Archivo:
app/teams_validation_service/http.py

5.1 Diseño de sesión HTTP

Se crea requests.Session() con:

Retry automático (hasta 4 intentos)

Backoff progresivo

Manejo explícito de 429

status_forcelist=[429, 500, 502, 503, 504]
Importante

Si recibe 429:

Lee header Retry-After

Aplica sleep dinámico

5.2 Contrato del Payload

Payload enviado a Power Automate:

{
  "request_id": "string",
  "destinatario": "email",
  "mensaje": "AdaptiveCard JSON"
}

Power Automate es responsable de:

Enviar tarjeta a Teams

Gestionar respuesta

Persistir respuesta en BigQuery QA

5.3 Resultado del envío

Por cada registro se retorna:

request_id

destinatario

lista_colaboradores

status_code

success

timestamp

Se devuelve como DataFrame para persistencia posterior.

6. Capa de Persistencia – BigQuery Repository

Archivo:
app/bigquery/bigquery_repository.py

Implementa patrón Repository para desacoplar lógica SQL.

6.1 read_query()

Wrapper simple sobre:

self.client.query(query).to_dataframe()
6.2 load_staging()

Carga DataFrame en:

<project>.<sandbox>.stg_<table>

Opcional:

DROP TABLE IF EXISTS

Usa LoadJobConfig.

6.3 merge_into()

Construcción dinámica de MERGE.

Estructura generada:
MERGE target t
USING (
  SELECT *
  FROM staging
  QUALIFY ROW_NUMBER() OVER (PARTITION BY request_id ORDER BY X DESC) = 1
) s
ON PK


WHEN MATCHED THEN UPDATE
WHEN NOT MATCHED THEN INSERT
Configurable vía dict:

pk

columns

update

order_by

where_update

Ventaja

Permite reutilizar clase para múltiples tablas.

7. Reprocesamiento Técnico

Función: reprocess()

Extrae lista de destinatarios.

Consulta QA.

Evalúa última respuesta por request_id.

Excluye registros válidos.

Se basa en:

ROW_NUMBER() OVER (PARTITION BY request_id ORDER BY responseTime DESC)

Evita:

Reenvío innecesario

Spam a managers

Sobrescritura incorrecta

8. Control de Errores
Implementado en todas las capas:

try/except granular

Logging estructurado

Distinción BigQueryError vs Exception

Manejo de RequestException

Validación de existencia de archivos

9. Consideraciones Técnicas Relevantes
Idempotencia parcial

El reprocesamiento no depende solo del request_id, sino también del estado en QA.

Acoplamiento

SQL está embebido en código.

Adaptive Card construida como string (alto acoplamiento).

Performance

Envío secuencial (no async).

No usa batch HTTP.

Seguridad

Endpoint configurable.

No hay validación explícita de esquema del payload.

10. Puntos Críticos
Riesgo	Impacto
request_id basado solo en mes	Posible colisión futura
Query hardcodeada	Baja flexibilidad
JSON armado manualmente	Riesgo de error de formato
No paralelización	Escalabilidad limitada
11. Mejoras Técnicas Recomendadas

Parametrizar periodo vía settings

Versionar Adaptive Cards

Implementar Async HTTP (aiohttp)

Separar SQL en archivos externos

Agregar validación de esquema con Pydantic

Mejorar estrategia de request_id (usar datetime completo)

Agregar test unitarios con mocks

12. Diseño Conceptual

El sistema implementa un patrón similar a:

ETL controlado

Integración event-driven (Power Automate)

Persistencia con patrón staging + merge

Control de idempotencia