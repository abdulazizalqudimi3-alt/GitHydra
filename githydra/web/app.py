from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import uvicorn

from githydra.web.blueprints.core import core_bp
from githydra.web.blueprints.git_ops import git_ops_bp
from githydra.web.blueprints.analytics import analytics_bp
from githydra.web.blueprints.ai import ai_bp
from githydra.src.commands.config import load_config

def create_app(repo_path='.', config_path=None):
    app = FastAPI(title="GitHydra Web Dashboard")

    # Store repo_path and config in app state
    app.state.repo_path = repo_path

    if config_path:
        import yaml
        with open(config_path, 'r') as f:
            app.state.config = yaml.safe_load(f) or {}
    else:
        app.state.config = load_config()

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

def run_web_server(repo_path='.', port=5000, mode='prod', config_path=None):
    # In FastAPI, debug is handled by log_level and reload in uvicorn
    app = create_app(repo_path, config_path)

    reload = True if mode == 'dev' else False
    log_level = "debug" if mode == 'dev' else "info"

    print(f"🚀 GitHydra Web Dashboard starting in {mode} mode...")
    print(f"📁 Repository: {os.path.abspath(repo_path)}")
    print(f"🌐 Server: http://0.0.0.0:{port}")

    uvicorn.run(app, host='0.0.0.0', port=port, log_level=log_level, reload=reload)

if __name__ == '__main__':
    run_web_server()
