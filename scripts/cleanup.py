#!/usr/bin/env python3
"""
Cleanup script to remove unnecessary files and organize project structure.

This script:
1. Moves documentation files to docs/
2. Moves utility scripts to scripts/
3. Removes temporary and redundant files
4. Creates a clean project structure
"""

import os
import shutil
from pathlib import Path

# Files to delete (temporary, redundant, or development-only)
FILES_TO_DELETE = [
    'check_backend_status.md',
    'CURRENT_STATUS.md',
    'diagnose_connection.md',
    'LAYOUT_FIXES.md',
    'STATISTICS_FEATURE.md',
    'test_backend_connection.py',
    'urban_mission_planning.log',
    'SUBMISSION_CHECKLIST.txt',
    'SUBMISSION_SUMMARY.md',
    'submission.json',
    'README.txt',  # Redundant with README.md
    'main.py',  # Duplicate of run_server.py
]

# Files to move to docs/
DOCS_FILES = {
    'README_FULLSTACK.md': 'docs/FULLSTACK.md',
    'README_SERVER.md': 'docs/SERVER.md',
    'QUICK_START.md': 'docs/GETTING_STARTED.md',  # Already created, will skip
    'FRONTEND_INTEGRATION_GUIDE.md': 'docs/FRONTEND.md',
    'SYSTEM_OVERVIEW.md': 'docs/ARCHITECTURE.md',
    'TROUBLESHOOTING.md': 'docs/TROUBLESHOOTING.md',
}

# Files to move to scripts/
SCRIPT_FILES = {
    'start_full_stack.sh': 'scripts/start.sh',
    'start_full_stack.bat': 'scripts/start.bat',
}

# Directories to clean
DIRS_TO_CLEAN = [
    '.hypothesis',  # Test artifacts
    '.pytest_cache',  # Test cache
    '__pycache__',  # Python cache
]


def main():
    """Execute cleanup operations."""
    root = Path('.')
    
    print("=" * 60)
    print("Project Cleanup and Reorganization")
    print("=" * 60)
    print()
    
    # Create directories if they don't exist
    print("Creating directory structure...")
    (root / 'docs').mkdir(exist_ok=True)
    (root / 'scripts').mkdir(exist_ok=True)
    print("✓ Directories created")
    print()
    
    # Delete unnecessary files
    print("Removing unnecessary files...")
    deleted_count = 0
    for file in FILES_TO_DELETE:
        file_path = root / file
        if file_path.exists():
            file_path.unlink()
            print(f"  ✓ Deleted: {file}")
            deleted_count += 1
    print(f"✓ Removed {deleted_count} files")
    print()
    
    # Move documentation files
    print("Organizing documentation...")
    moved_docs = 0
    for src, dst in DOCS_FILES.items():
        src_path = root / src
        dst_path = root / dst
        if src_path.exists() and not dst_path.exists():
            shutil.move(str(src_path), str(dst_path))
            print(f"  ✓ Moved: {src} → {dst}")
            moved_docs += 1
        elif src_path.exists():
            print(f"  ⊘ Skipped: {dst} already exists")
    print(f"✓ Organized {moved_docs} documentation files")
    print()
    
    # Move script files
    print("Organizing scripts...")
    moved_scripts = 0
    for src, dst in SCRIPT_FILES.items():
        src_path = root / src
        dst_path = root / dst
        if src_path.exists():
            shutil.move(str(src_path), str(dst_path))
            # Make executable on Unix
            if dst.endswith('.sh'):
                os.chmod(dst_path, 0o755)
            print(f"  ✓ Moved: {src} → {dst}")
            moved_scripts += 1
    print(f"✓ Organized {moved_scripts} script files")
    print()
    
    # Clean directories
    print("Cleaning temporary directories...")
    cleaned_dirs = 0
    for dir_name in DIRS_TO_CLEAN:
        for dir_path in root.rglob(dir_name):
            if dir_path.is_dir():
                shutil.rmtree(dir_path)
                print(f"  ✓ Removed: {dir_path}")
                cleaned_dirs += 1
    print(f"✓ Cleaned {cleaned_dirs} directories")
    print()
    
    print("=" * 60)
    print("Cleanup Complete!")
    print("=" * 60)
    print()
    print("Project structure is now organized and production-ready.")
    print()
    print("Next steps:")
    print("  1. Review docs/ for documentation")
    print("  2. Use scripts/start.sh or scripts/start.bat to run")
    print("  3. Commit changes to version control")
    print()


if __name__ == '__main__':
    main()
