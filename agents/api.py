"""
FastAPI REST API Server for Dermatopath Melanoma Agent.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Dermatopath Melanoma Agent API",
    description="Enterprise Distributed Component Platform (Digital Pathology & Histology Systems)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "dermatopath-melanoma-agent", "domain": "Digital Pathology & Histology Systems", "standard": "Demonstration only (not validated melanoma staging)", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException:
        raise HTTPException(status_code=422, detail="Possible direct identifier detected; supply synthetic data only.")
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=422, detail="Possible direct identifier detected; supply synthetic data only.")


@app.get("/api/audit/logs")
def api_audit_logs():
    # Avoid exposing task identifiers and audit metadata through an unauthenticated endpoint.
    return {"audit_blocks_total": len(AuditLogger.get_trail()), "verified": AuditLogger.verify_integrity()}
