"""App entry point for Railway deployment.

This file creates the proper import structure for Railway's Railpack,
which deploys files flat without the `backend` package structure.
"""
import os
import sys

# Add current directory to path so 'backend' imports work
# when files are deployed flat
current_dir = os.path.dirname(os.path.abspath(__file__))

# Create backend package structure dynamically
backend_init = os.path.join(current_dir, "backend", "__init__.py")
if not os.path.exists(backend_init):
    os.makedirs(os.path.join(current_dir, "backend"), exist_ok=True)
    # Create symlinks or copy files
    for item in os.listdir(current_dir):
        if item != "backend" and not item.startswith("."):
            src = os.path.join(current_dir, item)
            dst = os.path.join(current_dir, "backend", item)
            if not os.path.exists(dst):
                try:
                    if os.path.isdir(src):
                        os.symlink(src, dst)
                    else:
                        os.symlink(src, dst)
                except OSError:
                    pass

sys.path.insert(0, current_dir)

# Now import the actual app
from main import app  # noqa: E402

# Re-export for uvicorn
__all__ = ["app"]
