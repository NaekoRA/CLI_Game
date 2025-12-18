# engine/story_validator.py
import os
import re
import sys
import argparse
from typing import Dict, List, Any

class StoryValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = {
            "total_scenes": 0,
            "total_choices": 0,
            "total_gotos": 0,
            "maze_commands": 0,
            "battle_commands": 0,
            "hangman_commands": 0
        }
    
    def validate_story_file(self, story_path: str) -> Dict[str, Any]:
        """Validasi file story lengkap"""
        if not os.path.exists(story_path):
            return {
                "ok": False,
                "errors": [f"File tidak ditemukan: {story_path}"],
                "warnings": [],
                "stats": self.stats
            }
        
        try:
            # Parse manual untuk analisis
            with open(story_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            scenes = self._parse_scenes(content)
            self.stats["total_scenes"] = len(scenes)
            
            # Analisis setiap scene
            for scene_name, lines in scenes.items():
                self._analyze_scene(scene_name, lines, scenes)
            
            # Validasi dependencies eksternal
            self._validate_external_dependencies(scenes)
            
            return {
                "ok": len(self.errors) == 0,
                "errors": self.errors,
                "warnings": self.warnings,
                "stats": self.stats
            }
            
        except Exception as e:
            return {
                "ok": False,
                "errors": [f"Error parsing story: {str(e)}"],
                "warnings": [],
                "stats": self.stats
            }
    
    def _parse_scenes(self, content: str) -> Dict[str, List[str]]:
        """Parse konten menjadi scene-scene"""
        scenes = {}
        current_scene = None
        current_lines = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line.startswith('\\scene'):
                # Save previous scene
                if current_scene:
                    scenes[current_scene] = current_lines
                
                # Start new scene
                parts = line.split()
                if len(parts) >= 2:
                    current_scene = parts[1]
                    current_lines = []
                else:
                    current_scene = "unknown"
                    current_lines = []
            elif current_scene and line:
                current_lines.append(line)
        
        # Add last scene
        if current_scene:
            scenes[current_scene] = current_lines
        
        return scenes
    
    def _analyze_scene(self, scene_name: str, lines: List[str], scenes: Dict):
        """Analisis satu scene"""
        for line in lines:
            # Count choices
            if line.startswith('\\choice'):
                self.stats["total_choices"] += 1
                
                # Extract target
                if 'goto' in line:
                    target_match = re.search(r'goto\s+(\w+)', line)
                    if target_match:
                        target = target_match.group(1)
                        if target not in scenes and target not in ['end', 'finish', 'credits']:
                            self.warnings.append(f"Scene '{scene_name}': Choice target '{target}' tidak ditemukan")
            
            # Count gotos
            elif line.startswith('\\goto'):
                self.stats["total_gotos"] += 1
                parts = line.split()
                if len(parts) >= 2:
                    target = parts[1]
                    if target not in scenes and target not in ['end', 'finish', 'credits']:
                        self.errors.append(f"Scene '{scene_name}': Goto target '{target}' tidak ditemukan")
            
            # Check maze commands
            elif line.startswith('\\maze'):
                self.stats["maze_commands"] += 1
                self._validate_maze_command(scene_name, line)
            
            # Check battle commands
            elif line.startswith('\\battle'):
                self.stats["battle_commands"] += 1
                self._validate_battle_command(scene_name, line)
            
            # Check hangman commands
            elif line.startswith('\\hangman'):
                self.stats["hangman_commands"] += 1
                self._validate_hangman_command(scene_name, line)
    
    def _validate_maze_command(self, scene_name: str, line: str):
        """Validasi perintah maze"""
        # Extract parameters
        params = {}
        
        # Cari map_name
        map_match = re.search(r'map_name\s*=\s*"([^"]+)"', line)
        if map_match:
            params['map_name'] = map_match.group(1)
        else:
            map_match = re.search(r'map_name\s*=\s*(\w+)', line)
            if map_match:
                params['map_name'] = map_match.group(1)
        
        if 'map_name' not in params:
            self.errors.append(f"Scene '{scene_name}': Maze command missing 'map_name'")
        else:
            # Check if maze map exists (akan dicek di validate_external_dependencies)
            pass
        
        # Check branches
        branch_types = ['win', 'lose', 'draw', 'default']
        for branch in branch_types:
            if branch in line:
                # Validasi ada di method lain
                pass
    
    def _validate_battle_command(self, scene_name: str, line: str):
        """Validasi perintah battle"""
        # Check for enemy name
        enemy_match = re.search(r'enemy\s*=\s*"([^"]+)"', line)
        if not enemy_match:
            enemy_match = re.search(r'enemy\s*=\s*(\w+)', line)
        
        if not enemy_match:
            self.warnings.append(f"Scene '{scene_name}': Battle command missing enemy name")
        
        # Check branches
        branch_types = ['win', 'lose', 'draw', 'surrender', 'default']
        for branch in branch_types:
            if branch in line:
                # Validasi ada di method lain
                pass
    
    def _validate_hangman_command(self, scene_name: str, line: str):
        """Validasi perintah hangman"""
        # Check if has words or category
        if 'words(' in line:
            # Validate words format
            pass
        elif 'category' in line:
            # Validate category
            pass
        else:
            self.warnings.append(f"Scene '{scene_name}': Hangman command missing 'words' or 'category'")
    
    def _validate_external_dependencies(self, scenes: Dict):
        """Validasi dependencies eksternal"""
        try:
            # Check maze maps
            from maze_maps import MAZE_MAPS
            
            # Collect all map names used
            map_names = set()
            for scene_name, lines in scenes.items():
                for line in lines:
                    if line.startswith('\\maze'):
                        map_match = re.search(r'map_name\s*=\s*"([^"]+)"', line)
                        if map_match:
                            map_names.add(map_match.group(1))
                        else:
                            map_match = re.search(r'map_name\s*=\s*(\w+)', line)
                            if map_match:
                                map_names.add(map_match.group(1))
            
            # Check each map exists
            for map_name in map_names:
                if map_name not in MAZE_MAPS:
                    self.errors.append(f"Maze map '{map_name}' tidak ditemukan di maze_maps.py")
            
        except ImportError:
            self.errors.append("File maze_maps.py tidak ditemukan")
        except Exception as e:
            self.errors.append(f"Error loading maze_maps: {str(e)}")

def validate_story(story_path: str):
    """Public interface untuk validasi story"""
    validator = StoryValidator()
    return validator.validate_story_file(story_path)

# CLI Interface
def main():
    parser = argparse.ArgumentParser(
        description='Story Structure Validator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m engine.story_validator story/test.story
  python -m engine.story_validator "path with spaces/story.story"
        """
    )
    
    parser.add_argument('story_file', help='Path ke file story (.story)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Tampilkan detail warnings')
    
    args = parser.parse_args()
    
    print("📖 STORY STRUCTURE VALIDATOR")
    print("="*50)
    
    result = validate_story(args.story_file)
    
    if not result["ok"]:
        print(f"❌ VALIDATION FAILED")
        print(f"\nFile: {os.path.basename(args.story_file)}")
        print(f"Scenes: {result['stats']['total_scenes']}")
        
        if result["errors"]:
            print(f"\n❌ ERRORS ({len(result['errors'])}):")
            for error in result["errors"]:
                print(f"  • {error}")
        
        if args.verbose and result["warnings"]:
            print(f"\n⚠️  WARNINGS ({len(result['warnings'])}):")
            for warning in result["warnings"]:
                print(f"  • {warning}")
        
        sys.exit(1)
    
    else:
        print(f"✅ VALIDATION PASSED")
        print(f"\nFile: {os.path.basename(args.story_file)}")
        print(f"Scenes: {result['stats']['total_scenes']}")
        print(f"Choices: {result['stats']['total_choices']}")
        print(f"Gotos: {result['stats']['total_gotos']}")
        print(f"Maze Commands: {result['stats']['maze_commands']}")
        print(f"Battle Commands: {result['stats']['battle_commands']}")
        print(f"Hangman Commands: {result['stats']['hangman_commands']}")
        
        if args.verbose and result["warnings"]:
            print(f"\n⚠️  WARNINGS ({len(result['warnings'])}):")
            for warning in result["warnings"]:
                print(f"  • {warning}")
        
        sys.exit(0)

if __name__ == "__main__":
    main()