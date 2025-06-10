from fastapi import APIRouter
from backend.decorators import log_endpoint
from typing import Dict, Optional
from backend.schemas.db_schemas import ProcedureRequest
from backend.dependencies import procedure_manager

router = APIRouter()

@router.get('/active_connection')
@log_endpoint
async def active_connection() -> Dict[str,str] :
    """
    Retrieve the currently active database connection.
    This asynchronous function interacts with the procedure manager to fetch
    details about the active database connection.
    Returns:
        Dict[str, str]: A dictionary containing information about the active
        database connection.
    """
    
    return await procedure_manager.active_connection()     

@router.post('/execute_procedure')
@log_endpoint
async def execute_procedure(request: ProcedureRequest) -> Optional[str]:
    """
    Executes a stored procedure using the provided request.
    Args:
        request (ProcedureRequest): The request object containing the details
            required to execute the procedure.
    Returns:
        Optional[str]: The result of the procedure execution as a string, or None
            if no result is returned.
    """
    
    return await procedure_manager.execute_procedure(request)