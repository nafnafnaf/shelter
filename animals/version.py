import subprocess
import os

def get_version():
    """Get the current git commit hash"""
    try:
        # Try to get git commit hash
        commit = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stderr=subprocess.DEVNULL
        ).decode('ascii').strip()
        return f"v2.0 ({commit})"
    except:
        # Fallback if git is not available
        return "v2.0"