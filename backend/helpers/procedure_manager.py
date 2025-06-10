import logging
import pyodbc
import datetime
import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv

from backend.schemas.db_schemas import ProcedureRequest
from typing import Optional, Dict, Any
from decimal import Decimal

# Load .env explicitly from project root
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

pd.options.display.float_format = "{:20,.2f}".format

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(message)s")

class ProcedureManager:

    def __init__(self, procedure_list: dict, DB_DSN: str = None, DB_UID: str = None, DB_PWD: str = None):
        if not procedure_list:
            logger.warning("There are no procedures defined in the procedure list. Agent will not be able to do any tasks.")

        self.procedure_list = procedure_list

        DB_SERVER = os.getenv("DB_SERVER")
        DB_NAME = os.getenv("DB_NAME")
        DB_UID = os.getenv("DB_UID")
        DB_PWD = os.getenv("DB_PWD")

        if not all([DB_SERVER, DB_NAME, DB_UID, DB_PWD]):
            raise ValueError("One or more DB connection environment variables are missing.")

        self.connection = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_NAME};"
            f"UID={DB_UID};"
            f"PWD={DB_PWD};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=yes;"
        )

    async def execute_procedure_from_method(self, method_name: str, params: Optional[Dict[str, str]] = None) -> Optional[str]:
        entry = self.procedure_list.get(method_name)
        if not entry:
            raise ValueError(f"No procedure registered under key '{method_name}'")

        real_name = entry.get("procedure_name")
        if not real_name or not isinstance(real_name, str):
            raise ValueError(f"Invalid or missing 'procedure_name' for '{method_name}'")

        template = entry.get("call_template")
        if not template or not isinstance(template, str):
            raise ValueError(f"Invalid or missing 'call_template' for '{method_name}'")

        try:
            sql_text = template.format(**(params or {}))
        except KeyError as e:
            raise ValueError(f"Missing parameter for SQL template: {e}")

        request = ProcedureRequest(proc_name=real_name, params=params or {})

        return await self.execute_procedure(request, sql_text)

    async def get_procedure_list(self) -> Optional[Dict]:
        return self.procedure_list

    async def get_procedure_name(self, method_name: str) -> Optional[str]:
        return self.procedure_list.get(method_name, {}).get("procedure_name")

    async def execute_procedure(self, request: ProcedureRequest, sql: str) -> Optional[str]:
        cursor = self.connection.cursor()
        cursor.execute(sql)

        try:
            first_row = cursor.fetchone()

            if first_row is None:
                logger.info(f"Procedure {request.proc_name} did not return anything.")
                self.connection.commit()
                result = None
            else:
                columns = [column[0] for column in cursor.description]
                data = [first_row] + cursor.fetchall()
                data = [
                    tuple(
                        (
                            float(val)
                            if isinstance(val, Decimal)
                            else (
                                pd.to_datetime(val)
                                if isinstance(val, datetime.datetime)
                                else val
                            )
                        )
                        for val in row
                    )
                    for row in data
                ]
                df = pd.DataFrame(data, columns=columns)
                result = df.to_csv(index=False, sep=";", float_format="%.2f")

            cursor.close()
            return result

        except pyodbc.ProgrammingError:
            logger.info(f"Procedure {request.proc_name} is not supposed to return anything.")
            self.connection.commit()
            cursor.close()
            return None

    async def active_connection(self) -> Dict[str, str]:
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchall()
            cursor.close()
            logger.info("Connection active.")
            return {
                "message": f"Connection successfully established. Returned value from select query: {str(result)}"
            }

        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            return None


# 🔍 Keyword alias generator
def get_keywords_for_procedures(procedure_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Builds a dictionary mapping natural language keywords to method keys
    for matching purposes in the SqlProceduresPlugin.
    """
    keyword_mapping = {}
    for method_key, details in procedure_data.items():
        keywords = details.get("keywords", [])
        for kw in keywords:
            keyword_mapping[kw.lower()] = method_key
    return keyword_mapping
