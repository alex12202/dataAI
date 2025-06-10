import os
import pyodbc

def ping_database():
    try:
        # 1. Read environment variables
        DB_SERVER = os.environ.get("DB_SERVER")          # e.g. "universityai.database.windows.net"
        DB_NAME   = os.environ.get("DB_NAME")            # e.g. "university_ai"
        DB_UID    = os.environ.get("DB_UID")             # e.g. "admin_user"
        DB_PWD    = os.environ.get("DB_PWD")             # e.g. "Heslo.12345"

        # 2. Build the ODBC connection string for Azure SQL
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={DB_SERVER},1433;"
            f"DATABASE={DB_NAME};"
            f"UID={DB_UID};"
            f"PWD={DB_PWD};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )

        # 3. Try to connect (timeout=5 to fail fast if no network)
        conn = pyodbc.connect(conn_str, timeout=5)
        cursor = conn.cursor()

        # 4. Run a simple SELECT 1 to verify
        cursor.execute("SELECT 1;")
        row = cursor.fetchone()
        if row and row[0] == 1:
            print("✅ Connection successful: SELECT 1 returned 1.")
        else:
            print("⚠️ Connected, but unexpected result:", row)

        cursor.close()
        conn.close()
        return True

    except pyodbc.InterfaceError as ie:
        print("❌ Interface error (ODBC driver or network issue):", ie)
    except pyodbc.OperationalError as oe:
        print("❌ Operational error (couldn't connect or authentication failed):", oe)
    except Exception as e:
        print("❌ Unexpected error:", e)

    return False

if __name__ == "__main__":
    success = ping_database()
    exit(0 if success else 1)
