#!/usr/bin/env python3
"""
Story Checker - Main Entry Point
Run: python check_stories.py
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("🎮 HORROR ADVENTURE - STORY CHECKER")
    print("="*60)
    
    try:
        # Try to import from engine folder
        from engine.story_checker import StoryChecker
    except ImportError:
        try:
            # Try to import from current directory
            from engine.story_checker import StoryChecker
        except ImportError:
            print("❌ Cannot import StoryChecker")
            print("Make sure story_checker.py is in engine/ or current directory")
            sys.exit(1)
    
    # Check all story files
    checker = StoryChecker(story_dir="story")
    ok, messages = checker.check_all_files()
    
    # Print all messages
    if messages:
        print("\n" + "="*60)
        print("📝 ALL MESSAGES:")
        print("="*60)
        
        errors = [m for m in messages if m.startswith("❌") or "error" in m.lower()]
        warnings = [m for m in messages if m not in errors]
        
        if errors:
            print("\n❌ ERRORS:")
            for error in errors:
                print(f"  {error}")
        
        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"  {warning}")
    
    # Print summary
    checker.print_summary()
    
    # Exit code
    if ok:
        print("\n✅ STORY CHECK PASSED - Game can be run safely")
        sys.exit(0)
    else:
        print("\n❌ STORY CHECK FAILED - Fix errors before running game")
        sys.exit(1)

if __name__ == "__main__":
    main()