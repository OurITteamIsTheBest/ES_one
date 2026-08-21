"""Vercel serverless entry — exposes the FastAPI `app` object."""
import sys
import os
from pathlib import Path

# Ensure project root is on sys.path so `backend` package is importable
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Point data_json at the file that ships with the deployment
os.environ.setdefault('DATA_JSON', str(ROOT / 'data' / 'dashboard_data.json'))

from backend.main import app  # noqa: E402,F401  (Vercel imports `app` from here)

# Debug catch-all: temporary, helps diagnose routing on Vercel
@app.get('/__debug/path')
def _debug_path(request):  # type: ignore
    return {'scope_path': request.scope.get('path'), 'root_path': request.scope.get('root_path'), 'raw_path': request.scope.get('raw_path', b'').decode(errors='ignore')}

