from fastapi import APIRouter, Request, HTTPException, Body
from typing import Optional, List
import os

from githydra.src.utils.git_helper import get_repo, get_branch_list, get_commit_history, get_staged_files

git_ops_bp = APIRouter()

@git_ops_bp.get('/status')
async def status(request: Request):
    try:
        repo = get_repo(request.app.state.repo_path)
        if not repo:
            raise HTTPException(status_code=400, detail='Not a git repository')

        return {
            'success': True,
            'data': {
                'branch': repo.active_branch.name if not repo.head.is_detached else 'HEAD detached',
                'staged': get_staged_files(repo),
                'unstaged': [item.a_path for item in repo.index.diff(None)],
                'untracked': repo.untracked_files
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'error': str(e)}

@git_ops_bp.get('/branches')
async def branches(request: Request):
    try:
        repo = get_repo(request.app.state.repo_path)
        if not repo:
            raise HTTPException(status_code=400, detail='Not a git repository')

        branches_list = get_branch_list(repo)
        current_branch = repo.active_branch.name if not repo.head.is_detached else None

        return {
            'success': True,
            'data': {
                'current': current_branch,
                'branches': [{'name': b[0], 'current': b[1]} for b in branches_list]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'error': str(e)}

@git_ops_bp.post('/branches/create')
async def create_branch(request: Request, data: dict = Body(...)):
    try:
        repo = get_repo(request.app.state.repo_path)
        if not repo:
            raise HTTPException(status_code=400, detail='Not a git repository')

        branch_name = data.get('name')
        checkout = data.get('checkout', False)

        new_branch = repo.create_head(branch_name)
        if checkout:
            new_branch.checkout()

        return {'success': True, 'message': f'Branch {branch_name} created successfully'}
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'error': str(e)}

@git_ops_bp.post('/branches/switch')
async def switch_branch(request: Request, data: dict = Body(...)):
    try:
        repo = get_repo(request.app.state.repo_path)
        if not repo:
            raise HTTPException(status_code=400, detail='Not a git repository')

        branch_name = data.get('name')

        repo.heads[branch_name].checkout()

        return {'success': True, 'message': f'Switched to branch {branch_name}'}
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'error': str(e)}

@git_ops_bp.post('/branches/delete')
async def delete_branch(request: Request, data: dict = Body(...)):
    try:
        repo = get_repo(request.app.state.repo_path)
        if not repo:
            raise HTTPException(status_code=400, detail='Not a git repository')

        branch_name = data.get('name')
        force = data.get('force', False)

        repo.delete_head(branch_name, force=force)

        return {'success': True, 'message': f'Branch {branch_name} deleted successfully'}
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'error': str(e)}

@git_ops_bp.get('/commits')
async def commits(request: Request, limit: int = 20):
    try:
        repo = get_repo(request.app.state.repo_path)
        if not repo:
            raise HTTPException(status_code=400, detail='Not a git repository')

        commits_data = get_commit_history(repo, limit)

        return {'success': True, 'data': commits_data}
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'error': str(e)}

@git_ops_bp.post('/commit')
async def commit(request: Request, data: dict = Body(...)):
    try:
        repo = get_repo(request.app.state.repo_path)
        if not repo:
            raise HTTPException(status_code=400, detail='Not a git repository')

        message = data.get('message')

        if not message:
            return {'success': False, 'error': 'Commit message is required'}

        repo.index.commit(message)

        return {'success': True, 'message': 'Changes committed successfully'}
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'error': str(e)}

@git_ops_bp.get('/stage/files')
async def stage_files(request: Request):
    try:
        repo = get_repo(request.app.state.repo_path)
        if not repo:
            raise HTTPException(status_code=400, detail='Not a git repository')

        staged = get_staged_files(repo)
        unstaged = [item.a_path for item in repo.index.diff(None)]
        untracked = repo.untracked_files

        return {
            'success': True,
            'data': {
                'staged': staged,
                'unstaged': unstaged,
                'untracked': untracked
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'error': str(e)}

@git_ops_bp.post('/stage/add')
async def stage_add(request: Request, data: dict = Body(...)):
    try:
        repo = get_repo(request.app.state.repo_path)
        if not repo:
            raise HTTPException(status_code=400, detail='Not a git repository')

        files = data.get('files', [])

        if not files:
            repo.git.add(A=True)
        else:
            repo.index.add(files)

        return {'success': True, 'message': 'Files staged successfully'}
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'error': str(e)}

@git_ops_bp.post('/stage/reset')
async def stage_reset(request: Request, data: dict = Body(...)):
    try:
        repo = get_repo(request.app.state.repo_path)
        if not repo:
            raise HTTPException(status_code=400, detail='Not a git repository')

        files = data.get('files', [])

        if not files:
            repo.index.reset()
        else:
            repo.index.reset(paths=files)

        return {'success': True, 'message': 'Files unstaged successfully'}
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'error': str(e)}

@git_ops_bp.get('/stash')
async def stash_list(request: Request):
    try:
        repo = get_repo(request.app.state.repo_path)
        if not repo:
            raise HTTPException(status_code=400, detail='Not a git repository')

        stash_output = repo.git.stash('list')
        stashes = []

        if stash_output:
            for i, line in enumerate(stash_output.split('\n')):
                if line.strip():
                    parts = line.split(':', 2)
                    if len(parts) >= 3:
                        stashes.append({
                            'index': i,
                            'message': parts[2].strip(),
                            'date': ''
                        })
                    else:
                        stashes.append({
                            'index': i,
                            'message': line.strip(),
                            'date': ''
                        })

        return {'success': True, 'data': stashes}
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'error': str(e)}

@git_ops_bp.post('/stash/save')
async def stash_save(request: Request, data: dict = Body(...)):
    try:
        repo = get_repo(request.app.state.repo_path)
        if not repo:
            raise HTTPException(status_code=400, detail='Not a git repository')

        message = data.get('message', 'WIP')

        repo.git.stash('save', message)

        return {'success': True, 'message': 'Changes stashed successfully'}
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'error': str(e)}

@git_ops_bp.get('/remotes')
async def remotes(request: Request):
    try:
        repo = get_repo(request.app.state.repo_path)
        if not repo:
            raise HTTPException(status_code=400, detail='Not a git repository')

        remotes_list = [{
            'name': remote.name,
            'url': list(remote.urls)[0] if remote.urls else ''
        } for remote in repo.remotes]

        return {'success': True, 'data': remotes_list}
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'error': str(e)}

@git_ops_bp.get('/tags')
async def tags(request: Request):
    try:
        repo = get_repo(request.app.state.repo_path)
        if not repo:
            raise HTTPException(status_code=400, detail='Not a git repository')

        tags_list = [{'name': tag.name, 'commit': tag.commit.hexsha[:7]} for tag in repo.tags]

        return {'success': True, 'data': tags_list}
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'error': str(e)}
