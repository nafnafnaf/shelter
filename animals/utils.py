"""Utility functions for the animals app"""
import subprocess
import os

def get_git_version():
    """Get current git version (tag + short commit hash)"""
    try:
        # Get latest tag
        tag = subprocess.check_output(
            ['git', 'describe', '--tags', '--abbrev=0'],
            stderr=subprocess.DEVNULL,
            cwd=os.path.dirname(__file__)
        ).decode('utf-8').strip()
        
        # Get short commit hash
        commit = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL,
            cwd=os.path.dirname(__file__)
        ).decode('utf-8').strip()
        
        return f"{tag} ({commit})"
    except:
        return "unknown"
