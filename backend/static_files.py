"""
Production static file serving.
Serves the React build from FastAPI so everything runs on one Azure App Service.
"""

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os


def setup_static_files(app):
    """
    Mount the React build output at /static and serve index.html for all
    non-API routes (SPA client-side routing support).
    
    Call this AFTER all routers are registered in main.py.
    Only activates if the build output exists.
    """
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    
    if not os.path.isdir(static_dir):
        print("⚠️  No static/ directory found. Run 'npm run build' in frontend/ first.")
        return

    # Serve built assets
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

    # Catch-all: serve index.html for SPA routing
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        index = os.path.join(static_dir, "index.html")
        if os.path.exists(index):
            return FileResponse(index)
        return {"error": "Frontend not built"}

    print("✅ React SPA served from /static")
