
import logging
import semantic_kernel as sk
from openai import OpenAI
from semantic_kernel.connectors.ai.function_choice_behavior import     FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import     AzureChatPromptExecutionSettings
from backend.helpers.sql_procedures_plugin import SqlProceduresPlugin
from backend import config
import json
from backend.helpers.procedure_manager import ProcedureManager
import pyodbc
import os

logger = logging.getLogger(__name__)


current_dir = os.path.dirname(__file__)
json_path = os.path.join(current_dir, 'sql_procedures', 'procedure_list.json')

with open(json_path, 'r') as f:
    procedure_list = json.load(f)

# Only pass the procedure_list — the rest is read from environment inside the class
procedure_manager = ProcedureManager(procedure_list)

kernel = sk.Kernel()

kernel.add_plugin(SqlProceduresPlugin(procedure_manager), plugin_name = "SqlProceduresPlugin")

execution_settings = AzureChatPromptExecutionSettings()
execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

chat_completion = AzureChatCompletion(
    deployment_name=config.DEPLOYMENT_NAME,
    endpoint=config.OPENAI_ENDPOINT,
    api_key=config.OPENAI_API_KEY,
    api_version=config.MODEL_VERSION
)
