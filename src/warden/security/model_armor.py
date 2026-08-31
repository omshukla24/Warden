import os
from typing import Dict, Any
from google.api_core.client_options import ClientOptions
from google.cloud import modelarmor_v1
from warden.config import GCP_PROJECT_ID, GCP_REGION, MODEL_ARMOR_TEMPLATE

def screen(payload: str) -> Dict[str, Any]:
    # Local bypass — no Model Armor setup needed to run locally.
    if os.environ.get("MODEL_ARMOR_ENABLED", "true").lower() != "true":
        return {"blocked": False, "categories": []}
    try:
        client = modelarmor_v1.ModelArmorClient(
            client_options=ClientOptions(api_endpoint=f"modelarmor.{GCP_REGION}.rep.googleapis.com")  # REQUIRED — else 404
        )
        name = f"projects/{GCP_PROJECT_ID}/locations/{GCP_REGION}/templates/{MODEL_ARMOR_TEMPLATE}"
        request = modelarmor_v1.SanitizeUserPromptRequest(
            name=name,
            user_prompt_data=modelarmor_v1.DataItem(text=payload),
        )
        result = client.sanitize_user_prompt(request=request).sanitization_result
        blocked = result.filter_match_state == modelarmor_v1.FilterMatchState.MATCH_FOUND  # correct enum
        categories = list(result.filter_results.keys()) if blocked else []
        return {"blocked": blocked, "categories": categories}
    except Exception as e:
        return {"blocked": True, "categories": [f"ERROR: {str(e)}"]}   # fail-closed

