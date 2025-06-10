import os

class ProcedureManager:

    def __init__(self, procedure_list: dict, DB_DSN: str = None, DB_UID: str = None, DB_PWD: str = None):
        if not procedure_list:
            logger.warning(
                "There are no procedures defined in the procedure list. Agent will not be able to do any tasks."
            )

        self.procedure_list = procedure_list

        # Get values from environment
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
