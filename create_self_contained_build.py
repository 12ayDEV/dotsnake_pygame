"""
Self-Contained Web Build Script for Pygame-Web

This script:
1. Downloads all CDN dependencies locally
2. Modifies index.html to use local paths
3. Creates a deployable web bundle
"""

import os
import shutil
import urllib.request
import re

# Paths
BUILD_DIR = "build/web"
CACHE_DIR = "build/web-cache"
CDN_BASE = "https://pygame-web.github.io/archives/0.8/"

def copy_cached_files():
    """Copy all cached CDN files to web directory with proper structure"""
    # The cache files are hashed, we need to identify them by content-type
    # For now, we'll download fresh copies with correct names
    
    os.makedirs(f"{BUILD_DIR}/archives/0.8", exist_ok=True)
    
    # Files to download
    files = [
        "pythons.js",
        "browserfs.min.js", 
        "vt.js",
        "vtx.css",
        "pglite.css",
    ]
    
    for f in files:
        url = CDN_BASE + f
        local_path = f"{BUILD_DIR}/archives/0.8/{f}"
        try:
            print(f"Downloading {f}...")
            urllib.request.urlretrieve(url, local_path)
        except Exception as e:
            print(f"  Skip: {e}")

def modify_index_html():
    """Modify index.html to use local paths instead of CDN"""
    index_path = f"{BUILD_DIR}/index.html"
    
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace CDN URL with relative path
    # From: src="https://pygame-web.github.io/archives/0.8/pythons.js"
    # To: src="archives/0.8/pythons.js"
    content = content.replace(
        'src="https://pygame-web.github.io/archives/0.8/',
        'src="archives/0.8/'
    )
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Modified index.html to use local paths")

def main():
    print("Creating self-contained web build...")
    copy_cached_files()
    modify_index_html()
    print(f"\nDone! Deploy contents of {BUILD_DIR} to your web server.")

if __name__ == "__main__":
    main()
