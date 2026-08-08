"""
FastAPI Server Entrypoint for Judex AI -- 4-LLM Panel Analyzer
"""

import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from typing import Optional, List

from backend.analyzer import analyze_contract_clause
from backend.doc_parser import parse_contract_document


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan: Initialize RAG engine and LangGraph on startup."""
    print("[Startup] Initializing Judex AI Advanced RAG + LangGraph Pipeline...")
    try:
        from backend.rag_engine import initialize_rag
        initialize_rag()
    except Exception as e:
        print(f"[Startup] RAG engine init warning: {e}")
    try:
        from backend.langgraph_pipeline import get_compiled_graph
        get_compiled_graph()
    except Exception as e:
        print(f"[Startup] LangGraph compile warning: {e}")
    print("[Startup] Judex AI ready.")
    yield
    print("[Shutdown] Judex AI shutting down.")


app = FastAPI(
    title="Judex AI -- 4-LLM Multi-Domain Analyzer",
    description="4-LLM Panel: Groq Llama 3.3 (Security) + Mistral Small (Performance) + Gemini 2.0 Flash (Quality) + Chief Judge | Advanced RAG + LangGraph",
    version="4.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisRequest(BaseModel):
    clause: str
    selected_type: Optional[str] = "auto"  # auto | code | specs | api | logs


@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "Judex AI -- 4-LLM Multi-Domain Analyzer",
        "models": [
            "Groq Llama 3.3 70B -- Security Inspector",
            "Mistral Small -- Performance Inspector",
            "Gemini 2.0 Flash -- Code Quality Inspector",
            "GPT-4o-mini -- Chief Judge Verdict Synthesizer"
        ]
    }


@app.post("/api/upload-document")
async def upload_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        parsed = parse_contract_document(content, file.filename)
        return parsed
    except Exception as e:
        print(f"Error parsing uploaded document: {e}")
        raise HTTPException(status_code=400, detail=f"Could not parse document: {str(e)}")


@app.post("/api/analyze")
def analyze(req: AnalysisRequest):
    try:
        result = analyze_contract_clause(
            clause_text=req.clause,
            selected_type=req.selected_type or "auto"
        )
        return result
    except Exception as e:
        print(f"Error during analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-zip")
async def analyze_zip(file: UploadFile = File(...)):
    try:
        from backend.repo_analyzer import analyze_repository_zip_bytes
        content = await file.read()
        result = analyze_repository_zip_bytes(content, file.filename)
        return result
    except Exception as e:
        print(f"Error during ZIP repository analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Could not analyze zip repository: {str(e)}")


class PatchRequest(BaseModel):
    content: str
    content_type: str = "code_generic"
    findings: List[str] = []
    recommendations: List[str] = []


@app.post("/api/generate-patch")
def generate_patch_endpoint(req: PatchRequest):
    try:
        from backend.patch_engine import generate_code_patch
        res = generate_code_patch(
            content=req.content,
            content_type=req.content_type,
            findings=req.findings,
            recommendations=req.recommendations
        )
        return res
    except Exception as e:
        print(f"Error generating patch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/patch-zip")
async def patch_zip_endpoint(
    file: UploadFile = File(...),
    patches_json: str = Form(...)
):
    try:
        from backend.patch_engine import patch_repository_zip_bytes
        zip_bytes = await file.read()
        file_patches = json.loads(patches_json)

        patched_bytes = patch_repository_zip_bytes(zip_bytes, file_patches)
        filename_patched = f"patched_{file.filename or 'project.zip'}"

        return Response(
            content=patched_bytes,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename_patched}"}
        )
    except Exception as e:
        print(f"Error patching ZIP: {e}")
        raise HTTPException(status_code=500, detail=str(e))



dist_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(dist_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        file_path = os.path.join(dist_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(dist_dir, "index.html"))