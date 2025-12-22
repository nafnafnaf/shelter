# Version is set at build time by reading git commit
# Fallback if not available
VERSION = "unknown"

try:
    import os
    version_file = os.path.join(os.path.dirname(__file__), '.version')
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            VERSION = f.read().strip()
except:
    pass

def get_version():
    return VERSION