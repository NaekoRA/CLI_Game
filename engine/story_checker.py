"""
Story DSL Error Checker
Digunakan untuk memeriksa semua file story sebelum game dijalankan
"""

import os
import re
from typing import Dict, List, Tuple, Set
from pathlib import Path

class StoryChecker:
    def __init__(self, story_dir: str = "story"):
        self.story_dir = story_dir
        self.errors = []
        self.warnings = []
        self.all_scenes = {}  # file: set(scenes)
        self.all_references = {}  # file: {scene: [(type, target, line)]}
    
    def check_all_files(self) -> Tuple[bool, List[str]]:
        """Check all .story files in directory"""
        if not os.path.exists(self.story_dir):
            self.errors.append(f"Story directory not found: {self.story_dir}")
            return False, self.errors
        
        story_files = list(Path(self.story_dir).glob("*.story"))
        if not story_files:
            self.errors.append(f"No .story files found in {self.story_dir}")
            return False, self.errors
        
        print(f"🔍 Checking {len(story_files)} story file(s)...")
        
        for story_file in story_files:
            self._check_file(str(story_file))
        
        # Cross-file scene reference check
        self._check_cross_file_references()
        
        # Summary
        if not self.errors:
            print(f"✅ All {len(story_files)} story files passed!")
            if self.warnings:
                print(f"⚠️  {len(self.warnings)} warning(s) found")
        else:
            print(f"❌ Found {len(self.errors)} error(s)")
        
        return len(self.errors) == 0, self.errors + self.warnings
    
    def _check_file(self, filepath: str):
        """Check a single story file"""
        filename = os.path.basename(filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='cp1252') as f:
                lines = f.readlines()
        except Exception as e:
            self.errors.append(f"File {filename}: Cannot read file - {e}")
            return
        
        self._check_syntax(filename, lines)
    
    def _check_syntax(self, filename: str, lines: List[str]):
        """Check syntax of a story file"""
        current_scene = None
        scenes_in_file = set()
        references_in_file = {}
        
        for i, line in enumerate(lines, 1):
            line = line.rstrip('\n')
            raw_line = line  # Keep original for error messages
            
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('//'):
                continue
            
            # Check scene declaration
            if line.startswith('\\scene'):
                parts = line.split()
                if len(parts) < 2:
                    self.errors.append(f"{filename}:{i} \\scene missing name")
                    self.errors.append(f"  Line: {raw_line}")
                else:
                    scene_name = parts[1]
                    if scene_name in scenes_in_file:
                        self.errors.append(f"{filename}:{i} Duplicate scene '{scene_name}'")
                        self.errors.append(f"  Line: {raw_line}")
                    scenes_in_file.add(scene_name)
                    current_scene = scene_name
                    
                    # Check valid scene name
                    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', scene_name):
                        self.warnings.append(f"{filename}:{i} Scene name '{scene_name}' contains special characters")
            
            # Check goto references
            elif line.startswith('\\goto'):
                parts = line.split()
                if len(parts) < 2:
                    self.errors.append(f"{filename}:{i} \\goto missing target")
                    self.errors.append(f"  Line: {raw_line}")
                elif current_scene:
                    target = parts[1]
                    if current_scene not in references_in_file:
                        references_in_file[current_scene] = []
                    references_in_file[current_scene].append(('goto', target, i, filename))
            
            # Check choice references
            elif line.startswith('\\choice'):
                if current_scene:
                    # Check for valid format
                    if '"' not in line:
                        self.errors.append(f"{filename}:{i} \\choice missing choice text in quotes")
                        self.errors.append(f"  Line: {raw_line}")
                    elif 'goto' not in line:
                        self.errors.append(f"{filename}:{i} \\choice missing 'goto' target")
                        self.errors.append(f"  Line: {raw_line}")
                    else:
                        # Extract goto target
                        match = re.search(r'goto\s+(\w+)', line)
                        if match:
                            target = match.group(1)
                            if current_scene not in references_in_file:
                                references_in_file[current_scene] = []
                            references_in_file[current_scene].append(('choice', target, i, filename))
            
            # Check battle command
            elif line.startswith('\\battle'):
                if current_scene:
                    # Check required parameters
                    if 'win=' not in line:
                        self.warnings.append(f"{filename}:{i} \\battle missing 'win=' parameter")
                        self.warnings.append(f"  Line: {raw_line}")
                    if 'lose=' not in line:
                        self.warnings.append(f"{filename}:{i} \\battle missing 'lose=' parameter")
                        self.warnings.append(f"  Line: {raw_line}")
                    
                    # Extract all branch targets
                    for match in re.finditer(r'(win|lose|draw|surrender)=(\w+)', line):
                        branch_type, target = match.groups()
                        if current_scene not in references_in_file:
                            references_in_file[current_scene] = []
                        references_in_file[current_scene].append((branch_type, target, i, filename))
            
            # Check maze command
            elif line.startswith('\\maze'):
                if current_scene:
                    # Check required parameters
                    if 'win=' not in line:
                        self.warnings.append(f"{filename}:{i} \\maze missing 'win=' parameter")
                        self.warnings.append(f"  Line: {raw_line}")
                    if 'lose=' not in line:
                        self.warnings.append(f"{filename}:{i} \\maze missing 'lose=' parameter")
                        self.warnings.append(f"  Line: {raw_line}")
                    
                    # Extract branch targets
                    for match in re.finditer(r'(win|lose)=(\w+)', line):
                        branch_type, target = match.groups()
                        if current_scene not in references_in_file:
                            references_in_file[current_scene] = []
                        references_in_file[current_scene].append((branch_type, target, i, filename))
            
            # Check for unclosed quotes
            quote_count = line.count('"')
            if quote_count % 2 != 0:
                self.errors.append(f"{filename}:{i} Unclosed quotes")
                self.errors.append(f"  Line: {raw_line}")
            
            # Check other commands
            elif line.startswith('\\'):
                # Check if command exists (basic validation)
                command = line.split()[0] if ' ' in line else line
                valid_commands = [
                    '\\scene', '\\clear', '\\divider', '\\pause', 
                    '\\progress', '\\loading', '\\choice', '\\goto', 
                    '\\bold', '\\battle', '\\maze', '\\battle_branch'
                ]
                
                if command not in valid_commands:
                    self.warnings.append(f"{filename}:{i} Unknown command: {command}")
        
        # Store file data
        self.all_scenes[filename] = scenes_in_file
        self.all_references[filename] = references_in_file
    
    def _check_cross_file_references(self):
        """Check if referenced scenes exist in any file"""
        # Collect all scenes across all files
        all_scenes_global = {}
        for filename, scenes in self.all_scenes.items():
            for scene in scenes:
                all_scenes_global[scene] = filename
        
        # Check all references
        for filename, references in self.all_references.items():
            for scene, refs in references.items():
                for ref_type, target, line_num, ref_filename in refs:
                    if target not in all_scenes_global:
                        self.errors.append(
                            f"{filename}:{line_num} {ref_type} references undefined scene '{target}'"
                        )
                        self.errors.append(f"  Referenced from scene: {scene}")
                    else:
                        # Optional: warn if cross-file reference
                        target_file = all_scenes_global[target]
                        if target_file != filename:
                            self.warnings.append(
                                f"{filename}:{line_num} Cross-file reference: "
                                f"'{target}' is defined in {target_file}"
                            )
    
    def print_summary(self):
        """Print detailed summary"""
        total_scenes = sum(len(scenes) for scenes in self.all_scenes.values())
        total_references = sum(len(refs) for refs in self.all_references.values())
        
        print("\n" + "="*60)
        print("📊 STORY CHECK SUMMARY")
        print("="*60)
        print(f"Files checked: {len(self.all_scenes)}")
        print(f"Total scenes: {total_scenes}")
        print(f"Total references: {total_references}")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        
        if self.all_scenes:
            print("\n📁 Files and scenes:")
            for filename, scenes in self.all_scenes.items():
                print(f"  {filename}: {len(scenes)} scene(s)")
                for scene in sorted(scenes):
                    # Count references for this scene
                    ref_count = len(self.all_references[filename].get(scene, []))
                    print(f"    - {scene} ({ref_count} references)")