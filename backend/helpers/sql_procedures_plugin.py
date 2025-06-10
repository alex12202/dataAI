from semantic_kernel.functions import kernel_function
from backend.helpers.procedure_manager import ProcedureManager
from sentence_transformers import SentenceTransformer, util
from rapidfuzz import fuzz
import re
import itertools

class SqlProceduresPlugin:
    def __init__(self, procedure_manager: ProcedureManager):
        self.procedure_manager = procedure_manager
        self.aliases = {}
        self.reverse_lookup = {}
        self.embeddings = {}
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self._build_aliases()

    def _build_aliases(self):
        self.aliases.clear()
        self.reverse_lookup.clear()
        self.embeddings.clear()

        procedures = self.procedure_manager.procedure_list

        for proc_key, props in procedures.items():
            all_aliases = set()
            description = props.get("description", "")
            keywords = props.get("keywords", [])

            # Add explicit keywords
            all_aliases.update([kw.strip().lower() for kw in keywords])

            # Add smart permutations
            parts = re.split(r"[_\s]+", proc_key.lower())
            permutations = itertools.permutations(parts, min(2, len(parts)))
            all_aliases.update([" ".join(p) for p in permutations])

            # Add common action phrases
            action_templates = [
                f"get {proc_key}",
                f"fetch {proc_key}",
                f"{proc_key} info",
                f"{proc_key} stats",
                f"run {proc_key}",
                f"execute {proc_key}",
                f"use {proc_key}",
            ]
            all_aliases.update([a.lower() for a in action_templates])

            # Store aliases and reverse mapping
            for alias in all_aliases:
                self.aliases[alias] = proc_key
                self.reverse_lookup.setdefault(proc_key, []).append(alias)

            # Store semantic embedding
            embedding_text = " ".join(all_aliases) + " " + description
            self.embeddings[proc_key] = self.model.encode(embedding_text, convert_to_tensor=True)

    def _resolve_method_key(self, user_input: str) -> str:
        input_clean = user_input.strip().lower()

        # 1. Direct match
        if input_clean in self.aliases:
            return self.aliases[input_clean]

        # 2. Fuzzy match
        fuzzy_scores = [(alias, fuzz.token_sort_ratio(input_clean, alias)) for alias in self.aliases]
        best_match, score = max(fuzzy_scores, key=lambda x: x[1])
        if score > 85:
            return self.aliases[best_match]

        # 3. Semantic similarity
        input_embedding = self.model.encode(input_clean, convert_to_tensor=True)
        best_key, best_score = None, -1
        for proc_key, emb in self.embeddings.items():
            score = util.cos_sim(input_embedding, emb).item()
            if score > best_score:
                best_key, best_score = proc_key, score
        return best_key if best_score > 0.55 else None

    @kernel_function(
        description="Call a stored procedure from the defined list using a method key and parameters."
    )
    async def call_procedure(self, method_key: str, **kwargs) -> dict:
        if not self.aliases:
            self._build_aliases()

        method_key_resolved = self._resolve_method_key(method_key)

        proc_list = await self.procedure_manager.get_procedure_list()
        if not proc_list:
            return {"status": "error", "message": "❌ No procedures available."}

        if method_key_resolved not in proc_list:
            return {"status": "error", "message": f"❌ Procedure key '{method_key}' not found."}

        expected_params = proc_list[method_key_resolved].get("parameters", {})
        supplied_params = {k: v for k, v in kwargs.items() if k in expected_params}

        missing = [k for k in expected_params if k not in supplied_params]
        if missing:
            prompts = [
                f"{k} ({expected_params[k].get('prompt', 'please provide a value')})"
                for k in missing
            ]
            return {"status": "error", "message": f"⚠️ Missing parameters: {', '.join(prompts)}"}

        try:
            result_csv = await self.procedure_manager.execute_procedure_from_method(method_key_resolved, supplied_params)
        except Exception as e:
            return {"status": "error", "message": f"❌ Execution failed: {str(e)}"}

        if not result_csv:
            return {"status": "success", "message": f"✅ Procedure `{method_key_resolved}` executed successfully, but returned no results."}

        preview_lines = result_csv.strip().splitlines()
        preview = "\n".join(preview_lines[:6])  # header + up to 5 rows

        return {
            "status": "success",
            "method": method_key_resolved,
            "preview": preview,
            "message": f"✅ Results from `{method_key_resolved}`:\n\n```\n{preview}\n```"
        }
