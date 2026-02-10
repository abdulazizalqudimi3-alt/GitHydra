from fastapi import APIRouter, Request, HTTPException, Body
import os

from githydra.src.utils.git_helper import get_repo
from githydra.src.ai_service import generate_commit_message, review_code, detect_bugs

ai_bp = APIRouter()

@ai_bp.post('/commit-message')
async def commit_message(request: Request):
    try:
        repo = get_repo(request.app.state.repo_path)
        if not repo:
            raise HTTPException(status_code=400, detail='Not a git repository')

        diff = repo.git.diff('--cached')
        if not diff:
            return {'success': False, 'error': 'No staged changes'}

        message = generate_commit_message(diff)

        return {'success': True, 'data': {'message': message}}
    except HTTPException:
        raise
    except Exception as e:
        return {'success': False, 'error': str(e)}

@ai_bp.post('/review-code')
async def review_code_api(request: Request, data: dict = Body(...)):
    try:
        code = data.get('code', '')

        if not code:
            return {'success': False, 'error': 'No code provided'}

        review = review_code(code)

        return {'success': True, 'data': review}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@ai_bp.post('/detect-bugs')
async def detect_bugs_api(request: Request, data: dict = Body(...)):
    try:
        code = data.get('code', '')

        if not code:
            return {'success': False, 'error': 'No code provided'}

        bugs = detect_bugs(code)

        return {'success': True, 'data': bugs}
    except Exception as e:
        return {'success': False, 'error': str(e)}
