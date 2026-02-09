from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

core_bp = APIRouter()

@core_bp.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return request.app.state.templates.TemplateResponse("dashboard.html", {"request": request})

@core_bp.get("/branches", response_class=HTMLResponse)
async def branches(request: Request):
    return request.app.state.templates.TemplateResponse("branches.html", {"request": request})

@core_bp.get("/commits", response_class=HTMLResponse)
async def commits(request: Request):
    return request.app.state.templates.TemplateResponse("commits.html", {"request": request})

@core_bp.get("/stage", response_class=HTMLResponse)
async def stage(request: Request):
    return request.app.state.templates.TemplateResponse("stage.html", {"request": request})

@core_bp.get("/stash", response_class=HTMLResponse)
async def stash(request: Request):
    return request.app.state.templates.TemplateResponse("stash.html", {"request": request})

@core_bp.get("/remotes", response_class=HTMLResponse)
async def remotes(request: Request):
    return request.app.state.templates.TemplateResponse("remotes.html", {"request": request})

@core_bp.get("/tags", response_class=HTMLResponse)
async def tags(request: Request):
    return request.app.state.templates.TemplateResponse("tags.html", {"request": request})

@core_bp.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    return request.app.state.templates.TemplateResponse("analytics.html", {"request": request})

@core_bp.get("/ai-tools", response_class=HTMLResponse)
async def ai_tools(request: Request):
    return request.app.state.templates.TemplateResponse("ai_tools.html", {"request": request})

@core_bp.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    return request.app.state.templates.TemplateResponse("settings.html", {"request": request})
