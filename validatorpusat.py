# validatorpusat.py
import sys
import os
import importlib
import tempfile
import signal
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List

class GameValidator:
    """Validator untuk mengecek semua engine berfungsi dengan benar"""
    
    def __init__(self):
        self.original_functions = {}
        self.validation_results = {
            "files": [],
            "functions": [],
            "scenes": [],
            "errors": []
        }
    
    def backup_and_mock_output(self):
        """Backup dan mock semua fungsi output untuk dry-run"""
        try:
            import engine.utils
            # Backup
            self.original_functions["slow_print"] = engine.utils.slow_print
            self.original_functions["console"] = engine.utils.console
            self.original_functions["input_no_empty"] = engine.utils.input_no_empty
            self.original_functions["clear"] = engine.utils.clear
            self.original_functions["pause"] = engine.utils.pause
            self.original_functions["divider"] = engine.utils.divider
            self.original_functions["progress_bar"] = engine.utils.progress_bar
            
            # Mock
            engine.utils.slow_print = lambda x, **kwargs: None
            engine.utils.console.print = lambda x, **kwargs: None
            engine.utils.input_no_empty = lambda prompt="": "a"
            engine.utils.clear = lambda: None
            engine.utils.pause = lambda msg=None: None
            engine.utils.divider = lambda sym="=", length=50: None
            engine.utils.progress_bar = lambda d=2, l="Memproses": None
            
        except ImportError as e:
            print(f"[!] Tidak bisa import engine.utils: {e}")
            # Buat mock minimal
            self.original_functions["utils_missing"] = True
        
        try:
            import engine.maze
            self.original_functions["maze_render"] = engine.maze.MazeGame.render
            engine.maze.MazeGame.render = lambda self: None
        except:
            pass
        
        try:
            import engine.battle
            if hasattr(engine.battle.BattleManager, 'display_battle'):
                self.original_functions["battle_display"] = engine.battle.BattleManager.display_battle
                engine.battle.BattleManager.display_battle = lambda: None
        except:
            pass
    
    def restore_original_functions(self):
        """Restore semua fungsi ke original"""
        try:
            import engine.utils
            if "slow_print" in self.original_functions:
                engine.utils.slow_print = self.original_functions["slow_print"]
            if "console" in self.original_functions:
                engine.utils.console = self.original_functions["console"]
            if "input_no_empty" in self.original_functions:
                engine.utils.input_no_empty = self.original_functions["input_no_empty"]
            if "clear" in self.original_functions:
                engine.utils.clear = self.original_functions["clear"]
            if "pause" in self.original_functions:
                engine.utils.pause = self.original_functions["pause"]
            if "divider" in self.original_functions:
                engine.utils.divider = self.original_functions["divider"]
            if "progress_bar" in self.original_functions:
                engine.utils.progress_bar = self.original_functions["progress_bar"]
        except:
            pass
        
        try:
            import engine.maze
            if "maze_render" in self.original_functions:
                engine.maze.MazeGame.render = self.original_functions["maze_render"]
        except:
            pass
        
        try:
            import engine.battle
            if "battle_display" in self.original_functions:
                engine.battle.BattleManager.display_battle = self.original_functions["battle_display"]
        except:
            pass
    
    def validate_file_structure(self) -> bool:
        """Validasi apakah semua file engine ada"""
        print("\n" + "="*50)
        print("VALIDASI FILE STRUCTURE")
        print("="*50)
        
        required_files = [
            "engine/__init__.py",
            "engine/maze.py",
            "engine/runner.py",
            "engine/parser.py",
            "engine/utils.py"
        ]
        
        all_ok = True
        for file in required_files:
            if os.path.exists(file):
                print(f"[✓] {file}")
                self.validation_results["files"].append((file, True))
            else:
                print(f"[✗] {file}")
                self.validation_results["files"].append((file, False))
                self.validation_results["errors"].append(f"File {file} tidak ditemukan")
                all_ok = False
        
        optional_files = ["engine/battle.py", "engine/hangman.py", "maze_maps.py"]
        for file in optional_files:
            if os.path.exists(file):
                print(f"[✓] {file} (optional)")
            else:
                print(f"[!] {file} (optional) - tidak ditemukan")
        
        return all_ok
    
    def validate_function_signatures(self) -> bool:
        """Validasi signature fungsi utama"""
        print("\n" + "="*50)
        print("VALIDASI FUNCTION SIGNATURES")
        print("="*50)
        
        required_functions = [
            ("engine.runner", "run_game"),
            ("engine.parser", "parse_story"),
            ("engine.maze", "MazeManager"),
        ]
        
        all_ok = True
        
        for module_name, func_name in required_functions:
            try:
                module = importlib.import_module(module_name)
                obj = getattr(module, func_name)
                
                if func_name == "MazeManager":
                    if hasattr(obj, "start_maze"):
                        print(f"[✓] {module_name}.{func_name}.start_maze()")
                        self.validation_results["functions"].append((f"{module_name}.{func_name}", True))
                    else:
                        print(f"[✗] {module_name}.{func_name}.start_maze() - method tidak ditemukan")
                        self.validation_results["functions"].append((f"{module_name}.{func_name}", False))
                        all_ok = False
                else:
                    if callable(obj):
                        print(f"[✓] {module_name}.{func_name}()")
                        self.validation_results["functions"].append((f"{module_name}.{func_name}", True))
                    else:
                        print(f"[✗] {module_name}.{func_name}() - tidak callable")
                        self.validation_results["functions"].append((f"{module_name}.{func_name}", False))
                        all_ok = False
                        
            except Exception as e:
                print(f"[✗] {module_name}.{func_name}() - ERROR: {e}")
                self.validation_results["functions"].append((f"{module_name}.{func_name}", False))
                self.validation_results["errors"].append(f"Import {module_name}.{func_name} error: {e}")
                all_ok = False
        
        return all_ok
    
    def create_sample_story(self) -> str:
        """Buat sample story untuk testing"""
        return """\\scene start
$cyan === TES VALIDATOR ===
Ini adalah tes dry-run validator.

\\choice "Test Maze" goto test_maze
\\choice "Test Goto" goto test_goto
\\choice "Selesai" goto end

\\scene test_maze
\\maze map_name="test" description="Test maze" win=success lose=fail

\\scene test_goto
Ini test perintah goto.
\\goto success

\\scene success
$green ✅ SUKSES!
Semua sistem bekerja.

\\scene fail  
$red ❌ GAGAL!

\\scene end
$yellow 🏁 TES SELESAI
"""
    
    def validate_dry_run(self) -> bool:
        """Validasi dengan dry-run sample story"""
        print("\n" + "="*50)
        print("VALIDASI DRY-RUN")
        print("="*50)
        
        try:
            from engine.parser import parse_story
            
            # Buat file temporary
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(self.create_sample_story())
                temp_file = f.name
            
            try:
                # Parse story
                scenes = parse_story(temp_file)
                print(f"[✓] Story parsed: {len(scenes)} scene(s)")
                
                # Mock maze_maps jika tidak ada
                if not os.path.exists("maze_maps.py"):
                    mock_maps = {"test": ["████", "█P █", "█ F█", "████"]}
                    sys.modules['maze_maps'] = MagicMock(MAZE_MAPS=mock_maps)
                
                from engine.runner import run_game
                
                # Mock mini games
                with patch('engine.maze.MazeManager.start_maze') as mock_maze:
                    mock_maze.return_value = {"result": "WIN", "finish_id": "F1", "steps": 5}
                    
                    try:
                        from engine import battle
                        with patch('engine.battle.BattleManager.start_battle') as mock_battle:
                            mock_battle.return_value = {"result": "WIN", "turns": 3}
                            result = self._run_with_timeout(scenes)
                    except ImportError:
                        # Battle module tidak ada, skip mocking
                        result = self._run_with_timeout(scenes)
                
                if result["success"]:
                    print("[✓] Dry-run completed successfully")
                    self.validation_results["scenes"].append(("dry_run", True))
                    return True
                else:
                    print(f"[✗] Dry-run failed: {result['error']}")
                    self.validation_results["errors"].append(f"Dry-run: {result['error']}")
                    return False
                    
            finally:
                # Cleanup
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    
        except Exception as e:
            print(f"[✗] Dry-run setup error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self.validation_results["errors"].append(f"Dry-run setup: {e}")
            return False
    
    def _run_with_timeout(self, scenes: Dict) -> Dict[str, Any]:
        """Run game dengan timeout protection (Windows compatible)"""
        from engine.runner import run_game
        
        try:
            # Untuk Windows, gunakan threading Timer
            from threading import Thread, Event
            import queue
            
            timeout_event = Event()
            result_queue = queue.Queue(maxsize=1)
            
            def run_game_wrapper():
                try:
                    game_data = {
                        "current_scene": "start",
                        "current_chapter": 1,
                        "checkpoint": "start",
                        "inventory": [],
                        "choices_history": [],
                        "flags": {},
                        "play_time": 0,
                        "player_stats": {
                            "discovered_secrets": 0,
                            "battles_won": 0,
                            "mazes_completed": 0,
                            "games_won": 0,
                            "battles_lost": 0
                        }
                    }
                    
                    result = run_game(
                        scenes=scenes,
                        game_data=game_data,
                        save_system=None,
                        slot_name=None
                    )
                    
                    if not timeout_event.is_set():
                        result_queue.put({"success": True, "data": result})
                        
                except Exception as e:
                    if not timeout_event.is_set():
                        result_queue.put({"success": False, "error": f"{type(e).__name__}: {e}"})
            
            # Start game thread
            game_thread = Thread(target=run_game_wrapper)
            game_thread.daemon = True
            game_thread.start()
            
            # Wait dengan timeout 15 detik
            game_thread.join(timeout=15)
            
            if game_thread.is_alive():
                # Timeout terjadi
                timeout_event.set()
                return {"success": False, "error": "Game stuck in infinite loop (timeout)"}
            else:
                # Game selesai
                try:
                    return result_queue.get_nowait()
                except queue.Empty:
                    return {"success": False, "error": "Game exited without result"}
                    
        except Exception as e:
            return {"success": False, "error": f"Timeout setup error: {type(e).__name__}: {e}"}
        
    def validate_story_file(self, story_path: str) -> bool:
        """Validasi file story lengkap"""
        print("\n" + "="*50)
        print(f"VALIDASI STORY FILE: {os.path.basename(story_path)}")
        print("="*50)
        
        if not os.path.exists(story_path):
            print(f"[✗] File tidak ditemukan")
            self.validation_results["errors"].append(f"Story file {story_path} tidak ditemukan")
            return False
        
        try:
            from engine.parser import parse_story
            scenes = parse_story(story_path)
            
            # Cek statistik
            total_choices = sum(1 for cmds in scenes.values() 
                              for cmd in cmds if cmd.get("type") == "choice")
            total_gotos = sum(1 for cmds in scenes.values() 
                            for cmd in cmds if cmd.get("type") == "goto")
            
            print(f"[✓] Parsed {len(scenes)} scenes")
            print(f"[✓] Found {total_choices} choices, {total_gotos} gotos")
            
            # Cek scene references
            missing_refs = []
            for scene_name, commands in scenes.items():
                for cmd in commands:
                    if cmd.get("type") in ["goto", "choice"]:
                        target = cmd.get("target")
                        if target and target not in scenes and target not in ["end", "finish"]:
                            missing_refs.append(f"{scene_name} -> {target}")
            
            if missing_refs:
                print(f"[!] {len(missing_refs)} missing scene references")
                for ref in missing_refs[:3]:  # Tampilkan 3 pertama
                    print(f"    • {ref}")
                if len(missing_refs) > 3:
                    print(f"    ... dan {len(missing_refs)-3} lainnya")
            
            return True
            
        except Exception as e:
            print(f"[✗] Parse error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self.validation_results["errors"].append(f"Parse story: {e}")
            return False
    
    def generate_report(self) -> bool:
        """Generate validation report"""
        print("\n" + "="*50)
        print("VALIDATION REPORT")
        print("="*50)
        
        # Summary
        total_files = len(self.validation_results["files"])
        passed_files = sum(1 for _, ok in self.validation_results["files"] if ok)
        
        total_funcs = len(self.validation_results["functions"])
        passed_funcs = sum(1 for _, ok in self.validation_results["functions"] if ok)
        
        print(f"📁 Files: {passed_files}/{total_files} passed")
        print(f"🔧 Functions: {passed_funcs}/{total_funcs} passed")
        print(f"🎮 Scenes tested: {len(self.validation_results['scenes'])}")
        
        # Errors
        if self.validation_results["errors"]:
            print(f"\n❌ ERRORS FOUND ({len(self.validation_results['errors'])}):")
            for i, error in enumerate(self.validation_results["errors"], 1):
                print(f"  {i}. {error}")
            print(f"\n[✗] VALIDATION FAILED")
            return False
        else:
            print(f"\n[✓] VALIDATION PASSED - Engine siap digunakan!")
            return True
    
    def run_validation(self, story_path: str = None, quick: bool = False):
        """Jalankan validasi"""
        print("🚀 GAME ENGINE VALIDATOR")
        print("="*50)
        
        try:
            # Backup dan mock
            self.backup_and_mock_output()
            
            # Jalankan validasi
            results = []
            
            # 1. File structure
            print("\n▶️  Validating file structure...")
            results.append(self.validate_file_structure())
            
            # 2. Function signatures
            print("\n▶️  Validating function signatures...")
            results.append(self.validate_function_signatures())
            
            # 3. Dry-run (kecuali quick mode)
            if not quick:
                print("\n▶️  Running dry-run test...")
                results.append(self.validate_dry_run())
            
            # 4. Story file validation (jika ada)
            if story_path:
                print("\n▶️  Validating story file...")
                results.append(self.validate_story_file(story_path))
            
            # 5. Report
            final_result = all(results) and self.generate_report()
            
            return final_result
            
        except Exception as e:
            print(f"\n[✗] CRITICAL ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Restore functions
            self.restore_original_functions()


def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Game Engine Validator - Dry-run test tanpa menjalankan game',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Validasi lengkap
  %(prog)s --quick            # Validasi cepat (file & fungsi saja)
  %(prog)s --story chapter1.txt  # Validasi dengan story file
        """
    )
    
    parser.add_argument('--story', help='Path ke file story (.txt)')
    parser.add_argument('--quick', action='store_true', 
                       help='Hanya validasi file & fungsi (skip dry-run)')
    
    args = parser.parse_args()
    
    validator = GameValidator()
    
    if args.quick:
        print("⚡ QUICK MODE: File & function validation only\n")
    
    success = validator.run_validation(
        story_path=args.story,
        quick=args.quick
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()