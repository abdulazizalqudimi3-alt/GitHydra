#!/usr/bin/env python3
"""
Web Dashboard Command for GitHydra
"""

import click
import sys
import os
import webbrowser
import threading
import time

@click.command('web', help='Launch GitHydra web dashboard')
@click.argument('path', default='.', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--port', '-p', default=5000, help='Port to run the web server on')
@click.option('--no-browser', is_flag=True, help='Don\'t open browser automatically')
@click.option('--mode', type=click.Choice(['dev', 'prod']), default='prod', help='Run in development or production mode')
@click.option('--config', 'config_path', type=click.Path(exists=True), help='Path to a custom configuration file')
def web_cmd(path, port, no_browser, mode, config_path):
    """Launch the GitHydra web dashboard"""
    from rich.console import Console
    from rich.panel import Panel
    
    console = Console()
    
    try:
        # Import and run the FastAPI app
        from githydra.web.app import run_web_server
        
        console.print(Panel.fit(
            "[bold cyan]🚀 GitHydra Web Dashboard[/bold cyan]\n"
            f"[yellow]Starting server on port {port}...[/yellow]\n"
            f"[yellow]Project path: {os.path.abspath(path)}[/yellow]",
            border_style="cyan"
        ))
        
        # Open browser after a delay
        if not no_browser:
            def open_browser():
                time.sleep(1.5)
                webbrowser.open(f'http://localhost:{port}')
            
            threading.Thread(target=open_browser, daemon=True).start()
        
        # Run the web server
        run_web_server(repo_path=path, port=port, mode=mode, config_path=config_path)
        
    except ImportError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}", style="red")
        console.print("[yellow]Tip:[/yellow] Make sure FastAPI and Uvicorn are installed: pip install fastapi uvicorn", style="yellow")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error starting web server:[/bold red] {str(e)}", style="red")
        sys.exit(1)
