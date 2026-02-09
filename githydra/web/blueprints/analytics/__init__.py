from fastapi import APIRouter, Request, HTTPException
import os
from datetime import datetime, timedelta

from githydra.src.utils.git_helper import get_repo

analytics_bp = APIRouter()

@analytics_bp.get('/weekly-report')
async def weekly_report(request: Request, weeks: int = 1):
    try:
        repo = get_repo(request.app.state.repo_path)
        if not repo:
            raise HTTPException(status_code=400, detail='Not a git repository')
        
        since_date = datetime.now() - timedelta(weeks=weeks)
        
        commits = list(repo.iter_commits(since=since_date.isoformat()))
        
        total_commits = len(commits)
        authors = {}
        total_additions = 0
        total_deletions = 0
        
        for commit in commits:
            author = commit.author.name
            authors[author] = authors.get(author, 0) + 1
            total_additions += commit.stats.total.get('insertions', 0)
            total_deletions += commit.stats.total.get('deletions', 0)
        
        return {
            'success': True,
            'data': {
                'total_commits': total_commits,
                'total_additions': total_additions,
                'total_deletions': total_deletions,
                'authors': authors,
                'period': f'{weeks} week(s)'
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'error': str(e)}

@analytics_bp.get('/code-insights')
async def code_insights(request: Request):
    try:
        repo = get_repo(request.app.state.repo_path)
        if not repo:
            raise HTTPException(status_code=400, detail='Not a git repository')
        
        file_stats = {}
        for item in repo.tree().traverse():
            if item.type == 'blob':
                ext = os.path.splitext(item.name)[1] or 'no-ext'
                file_stats[ext] = file_stats.get(ext, 0) + 1
        
        return {
            'success': True,
            'data': {
                'file_types': file_stats,
                'total_files': sum(file_stats.values())
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'error': str(e)}

@analytics_bp.get('/team-analytics')
async def team_analytics(request: Request):
    try:
        repo = get_repo(request.app.state.repo_path)
        if not repo:
            raise HTTPException(status_code=400, detail='Not a git repository')
        
        commits = list(repo.iter_commits(max_count=100))
        
        contributors = {}
        for commit in commits:
            author = commit.author.name
            if author not in contributors:
                contributors[author] = {
                    'commits': 0,
                    'additions': 0,
                    'deletions': 0,
                    'email': commit.author.email
                }
            contributors[author]['commits'] += 1
            contributors[author]['additions'] += commit.stats.total.get('insertions', 0)
            contributors[author]['deletions'] += commit.stats.total.get('deletions', 0)
        
        return {
            'success': True,
            'data': contributors
        }
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'error': str(e)}
