from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import os
from ..logger.manager import DecisionManager
from ..logger.models import Decision


# Obtener la ruta absoluta del directorio donde está este archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="RS Engineering Decision Logger")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

manager = DecisionManager()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, q: Optional[str] = None):
    if q:
        decisions = manager.search_decisions(q)
    else:
        decisions = manager.list_decisions()
    
    # Sort by date descending
    decisions.sort(key=lambda x: x.date, reverse=True)
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "decisions": decisions,
        "search_query": q
    })

@app.post("/log")
async def log_decision(
    title: str = Form(...),
    context: str = Form(...),
    chosen_option: str = Form(...),
    rationale: str = Form(...),
    impact: str = Form(...)
):
    data = {
        "title": title,
        "context": context,
        "chosen_option": chosen_option,
        "rationale": rationale,
        "impact": impact,
        "status": "Accepted"
    }
    manager.add_decision(data)
    return RedirectResponse(url="/", status_code=303)

@app.get("/decision/{decision_id}", response_class=HTMLResponse)
async def get_decision(request: Request, decision_id: int):
    decision = manager.get_decision(decision_id)
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "selected_decision": decision,
        "decisions": manager.list_decisions()
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
