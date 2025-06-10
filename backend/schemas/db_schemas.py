from typing import Optional, Dict
from pydantic import BaseModel

class ProcedureRequest(BaseModel):
    proc_name: str
    params: Optional[Dict[str, str]] = None