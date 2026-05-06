##app/teams_validation_service/http.py
import time
import warnings
import requests
import pandas as pd
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.config import settings
from config.log_config import logger
from app.utills.utills import get_array, get_date_time

########### config ##############
pd.set_option("display.max_rows", 5)
warnings.simplefilter("ignore", UserWarning)
#################################


class EnvSolicitud:
    """
    Servicio encargado del envío de solicitudes HTTP hacia un endpoint
    (por ejemplo, Power Automate), utilizando información previamente generada.

    Funcionalidades principales:
        - Leer archivo de destinatarios desde Excel
        - Construir payloads JSON
        - Enviar solicitudes HTTP con manejo de retries
        - Registrar resultados de ejecución
    """
    def __init__(self, file_dest: str) -> None:
        """
        Inicializa el servicio de envío.

        Args:
            file_dest (str): Nombre del archivo Excel (sin extensión)
                             que contiene destinatarios y mensajes.
        """
        self.file_dest = file_dest
        self.dir_path = Path(settings.path_output)
        self.file_result = Path(settings.path_result)
        self.url = str(settings.url_p_automate)

        logger.debug(
            "Inicializando EnvSolicitud | file_dest=%s | url=%s",
            self.file_dest,
            self.url,
        )
        self.session = self._create_session()
        print("\neste es el nombre del archivo", self.file_dest
              ,'\n')

    # -------------------------------------------------- #
    def lista_destinatarios(self) -> tuple[bool, str, pd.DataFrame]:
        """
        Lee un archivo Excel y obtiene la lista de destinatarios.

        El archivo debe contener al menos dos columnas:
            - destinatario
            - mensaje

        Returns:
            Tuple[bool, str, pd.DataFrame]:
                - success (bool): Estado de la operación
                - message (str): Mensaje descriptivo
                - df (pd.DataFrame): DataFrame con columnas normalizadas

        Errores:
            - Archivo no existe
            - Archivo no es .xlsx
            - Error de formato en Excel
        """
        logger.info("Procesando lista de destinatarios")

        file_path = self.dir_path / f"{self.file_dest}.xlsx"

        if not file_path.exists():
            logger.error("La ruta no existe: %s", file_path)
            return False, f"La ruta {file_path} no existe", pd.DataFrame()

        if file_path.suffix.lower() != ".xlsx":
            logger.error("El archivo no es Excel: %s", file_path)
            return False, "El archivo no es un Excel", pd.DataFrame()

        try:
            df = pd.read_excel(file_path, sheet_name="Sheet1")
            df = df.rename(
                columns={
                    df.columns[0]: "destinatario",
                    df.columns[1]: "mensaje",
                }
            )

            logger.info("Destinatarios cargados correctamente: %s", len(df))
            return True, "OK", df

        except ValueError as e:
            logger.exception("Error de formato en el Excel")
            return False, f"Error en el Excel: {e}", pd.DataFrame()

        except Exception as e:
            logger.exception("Error inesperado leyendo Excel")
            return False, f"Error inesperado leyendo Excel: {e}", pd.DataFrame()

    # -------------------------------------------------- #
    def _create_session(self) -> requests.Session:
        """
        Crea una sesión HTTP con política de reintentos (retry).

        Configuración:
            - Reintentos totales: 4
            - Backoff exponencial
            - Códigos a reintentar: 429, 500, 502, 503, 504
            - Método permitido: POST

        Returns:
            requests.Session: Sesión configurada con retry.
        """
        logger.debug("Creando sesión HTTP con retry")
        retry = Retry(
            total=4,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
            raise_on_status=False,
        )
        
        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    # -------------------------------------------------- #
    def _build_payload(self, request_id: str
                       , destinatario: str, mensaje: str) -> tuple[str, dict, list]:
        """
        Construye el payload JSON a enviar.

        Args:
            request_id (str): Identificador único de la solicitud
            destinatario (str): Correo o identificador del destinatario
            mensaje (str): Mensaje en formato JSON/string

        Returns:
            Tuple[str, dict, list]:
                - request_id
                - payload (dict): Estructura JSON para envío
                - colaboradores (list): Lista extraída desde el mensaje
        """
        colaboradores = get_array(mensaje)
        payload = {
            "request_id": request_id,
            "destinatario": destinatario,
            "mensaje": mensaje,
        }

        logger.debug(
            "Payload construido | request_id=%s | destinatario=%s",
            request_id,
            destinatario,
        )
        return request_id, payload, colaboradores

    # -------------------------------------------------- #
    def _send_request(self, payload: dict) -> int:
        response = self.session.post(
            self.url,
            json=payload,
            timeout=30,
        )

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            wait = int(retry_after) if retry_after else 10

            logger.warning(
                "429 recibido, esperando %s segundos antes de continuar",
                wait,
            )
            time.sleep(wait)
        else:
            time.sleep(settings.timesleep)
        return response.status_code

    # -------------------------------------------------- #
    def creacion_json(self, request_id: str, destinatario: str, mensaje: str):
        request_id, payload, colaboradores = self._build_payload(
            request_id, destinatario, mensaje
        )

        result = {
            "request_id": request_id,
            "destinatario": destinatario,
            "lista_colaboradores": colaboradores,
        }

        try:
            status_code = self._send_request(payload)
            result["status_code"] = int(status_code)

            logger.info(
                "Request enviado | request_id=%s | destinatario=%s | status=%s",
                request_id,
                destinatario,
                status_code,
            )

            return True, result

        except requests.exceptions.RequestException as e:
            logger.exception(
                "Error de red enviando request | request_id=%s", request_id
            )
            result["status_code"] = 400
            result["error"] = str(e)
            return False, result

        except Exception as e:
            logger.exception(
                "Error inesperado enviando request | request_id=%s", request_id
            )
            result["status_code"] = 500
            result["error"] = str(e)
            return False, result

    # -------------------------------------------------- #
    def envio_json(self, data: pd.DataFrame):
        total = len(data)
        resultados = []

        logger.info("Iniciando envío de %s formularios", total)

        for i, row in enumerate(data.itertuples(index=False), start=1):
            success, result = self.creacion_json(
                str(row.request_id),
                str(row.destinatario),
                str(row.mensaje),
            )

            result.update(
                {
                    "success": success,
                    "timestamp": get_date_time(),
                }
            )

            logger.info(
                "%s/%s - %s - status:%s",
                i,
                total,
                row.destinatario,
                result.get("status_code"),
            )

            resultados.append(result)

        logger.info("Proceso de envío finalizado")
        return True, pd.DataFrame(resultados)
