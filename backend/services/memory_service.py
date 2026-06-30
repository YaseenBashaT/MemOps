"""
memory_service.py — single gateway between MemOps and Cognee.

All Cognee imports live here. No other file in the project may import cognee.
Swapping Cognee for another backend means editing only this file.
"""

import os
import cognee
from cognee.modules.search.types.SearchType import SearchType
from cognee.infrastructure.llm.config import get_llm_config
from cognee.infrastructure.databases.vector.embeddings.config import get_embedding_config


def _configure_cognee() -> None:
    cognee.config.set_llm_provider(os.getenv("LLM_PROVIDER", "custom"))
    cognee.config.set_llm_model(os.getenv("LLM_MODEL", "openai/llama-3.3-70b-versatile"))
    cognee.config.set_llm_endpoint(os.getenv("LLM_ENDPOINT", "https://api.groq.com/openai/v1"))
    cognee.config.set_llm_api_key(os.getenv("LLM_API_KEY"))
    cognee.config.set_embedding_provider("fastembed")
    cognee.config.set_embedding_model("BAAI/bge-small-en-v1.5")
    cognee.config.set_embedding_dimensions(384)


_configure_cognee()


def _format_incident(incident: dict) -> str:
    """
    Serialise an incident dict into a rich natural-language block so Cognee
    can build a dense, relationship-aware graph from it.
    """
    slack = "\n  ".join(incident.get("slack_thread", []))
    commits = "\n  ".join(incident.get("git_commits", []))
    jira = incident.get("jira_ticket", {})
    return f"""
INCIDENT REPORT
===============
Incident ID   : {incident.get('incident_id')}
Alert Name    : {incident.get('alert_name')}
Service       : {incident.get('service_affected')}
Severity      : {incident.get('severity')}
Timestamp     : {incident.get('timestamp')}
Engineer      : {incident.get('engineer_name')}
Resolution    : {incident.get('resolution_time_minutes')} minutes
Outcome       : {incident.get('outcome')}

ERROR LOG
---------
{incident.get('error_log')}

FIX APPLIED
-----------
{incident.get('fix_applied')}

SLACK THREAD
------------
  {slack}

JIRA TICKET
-----------
ID      : {jira.get('id')}
Title   : {jira.get('title')}
Resolution: {jira.get('resolution')}

GIT COMMITS
-----------
  {commits}
""".strip()


# All incidents share one dataset so Cognee builds a single connected graph
# (shared nodes like services, engineers, fixes link incidents together).
# This makes recall a single graph traversal/completion instead of fanning
# out one LLM call per incident dataset.
INCIDENTS_DATASET = "incidents"


async def ingest_incident(incident: dict) -> None:
    """
    Ingest a single incident into Cognee's shared incident graph.
    """
    text = _format_incident(incident)
    await cognee.remember(text, dataset_name=INCIDENTS_DATASET)


async def recall_for_alert(alert_text: str) -> dict:
    """
    Query Cognee's graph for past incidents relevant to an alert.
    Returns a dict with the raw results list and their count.

    Uses GRAPH_COMPLETION: a single LLM call that reasons over the retrieved
    graph triplets (connected nodes + relationships). This is fully graph-aware
    but far cheaper than the auto-routed GRAPH_COMPLETION_CONTEXT_EXTENSION mode,
    which fires 5+ LLM calls per recall and trips strict free-tier rate limits.
    """
    results = await cognee.recall(alert_text, query_type=SearchType.GRAPH_COMPLETION)
    return {
        "query": alert_text,
        "count": len(results),
        "results": [
            {
                "type": type(r).__name__,
                "source": getattr(r, "source", None),
                "text": getattr(r, "text", None) or getattr(r, "answer", None),
                "search_type": getattr(r, "search_type", None),
                "dataset_name": getattr(r, "dataset_name", None),
                "raw": str(r),
            }
            for r in results
        ],
    }


async def reinforce_fix(dataset_name: str) -> None:
    """
    Run Cognee's self-improvement pass on a dataset to strengthen graph edges.
    """
    await cognee.improve(dataset=dataset_name)


async def forget_incident(dataset_name: str) -> None:
    """
    Remove a specific incident dataset from Cognee's graph memory.
    """
    await cognee.forget(dataset=dataset_name)
