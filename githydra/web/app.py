from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import uvicorn

from githydra.web.blueprints.core import core_bp
from githydra.web.blueprints.git_ops import git_ops_bp
from githydra.web.blueprints.analytics import analytics_bp
from githydra.web.blueprints.ai import ai_bp

def create_app(repo_path='.'):
    app = FastAPI(title="GitHydra Web Dashboard")

    # Store repo_path in app state
    app.state.repo_path = repo_path

    # Static files and Templates
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

    # Initialize templates and store in app state
    app.state.templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

    # Include routers
    app.include_router(core_bp)
    app.include_router(git_ops_bp, prefix="/api/git")
    app.include_router(analytics_bp, prefix="/api/analytics")
    app.include_router(ai_bp, prefix="/api/ai")

    return app

def run_web_server(repo_path='.', port=5000, debug=True):
    # In FastAPI, debug is handled by log_level and reload in uvicorn
    app = create_app(repo_path)
    print(f"🚀 GitHydra Web Dashboard starting...")
    print(f"📁 Repository: {os.path.abspath(repo_path)}")
    print(f"🌐 Server: http://0.0.0.0:{port}")
    uvicorn.run(app, host='0.0.0.0', port=port, log_level="info")

if __name__ == '__main__':
    run_web_server()
