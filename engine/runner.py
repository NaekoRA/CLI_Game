from .utils import slow_print, console, input_no_empty ,clear, divider, pause,progress_bar
from engine.battle import BattleManager
from rich.text import Text
from rich.panel import Panel
from engine.maze import MazeManager
from maze_maps import MAZE_MAPS
from engine.hangman import HangmanManager

def run_game(scenes, game_data=None, save_system=None, slot_name=None):
    if game_data is None:
        game_data = {
            "current_chapter": 1,
            "current_scene": "start",
            "checkpoint": "start", 
            "inventory": [],
            "choices_history": [],            "flags": {},
            "play_time": 0
        }
    
    current = game_data["current_scene"]
    choices_made = game_data["choices_history"].copy()

    while True:
        if current not in scenes:
            slow_print(f"[Scene '{current}' tidak ditemukan]")
            return game_data

        commands = scenes[current]
        next_scene = None
        choices = []

        # UPDATE CHECKPOINT
        game_data["current_scene"] = current
        game_data["checkpoint"] = current

        for cmd in commands:

            if cmd["type"] == "text":
                slow_print(cmd["text"])
            
            elif cmd["type"] == "bold":
                text = Text(cmd["text"].upper(), style="bold")
                console.print(text)
            
            elif cmd["type"] == "color":
                text = Text(cmd["text"], style=cmd["color"])
                console.print(text)
            
            elif cmd["type"] == "goto":
                next_scene = cmd["target"]
                break
            
            elif cmd["type"] == "choice":
                choices.append(cmd)

            # CLEAR SCREEN - HANDLE BARU
            elif cmd["type"] == "clear":
                clear()
            
            # DIVIDER - HANDLE BARU
            elif cmd["type"] == "divider":
                divider(cmd.get("symbol", "="))
            
            # PAUSE - HANDLE BARU
            elif cmd["type"] == "pause":
                pause(cmd.get("message", "\nTekan Enter untuk melanjutkan..."))
            
            # PROGRESS BAR - HANDLE BARU
            elif cmd["type"] == "progress":
                progress_bar(
                    cmd.get("duration", 2), 
                    cmd.get("label", "Memproses")
                )
            
            # Battle handler
            elif cmd["type"] == "battle":
                console.print("\n" + "⚔️" * 20, style="bold red")
                console.print("          PERTARUNGAN DIMULAI!", style="bold red")
                console.print("⚔️" * 20, style="bold red")
                
                battle_result = BattleManager.start_battle(cmd.get("config", {}))
                outcome = battle_result["result"].lower()
                
                # Update game state
                game_data["flags"]["last_battle"] = outcome
                game_data["flags"]["last_battle_turns"] = battle_result["turns"]
                
                if outcome == "win":
                    game_data["player_stats"]["battles_won"] = game_data["player_stats"].get("battles_won", 0) + 1
                elif outcome == "lose":
                    game_data["player_stats"]["battles_lost"] = game_data["player_stats"].get("battles_lost", 0) + 1                
                # Cari branch target berdasarkan outcome
                target_scene = cmd["branches"].get(outcome)
                
                if target_scene:
                    # Jika ada branch target, pindah scene
                    next_scene = target_scene
                    break
                else:
                    # Jika tidak ada branch, lanjut scene berikutnya
                    pause()
                    continue
                
            #maze handler
            # Dalam run_game function, update maze handler:
            elif cmd["type"] == "maze":
                console.print("\n" + "🧭" * 25, style="bold green")
                console.print("        MAZE CHALLENGE START!", style="bold green")
                console.print("🧭" * 25, style="bold green")
                
                config = cmd.get("config", {})
                branches = cmd.get("branches", {})
                
                map_name = config.get("map_name", "tutorial")
                description = config.get("description", "Find your way through the maze!")
                
                # Get the maze map
                maze_map = MAZE_MAPS.get(map_name, MAZE_MAPS["tutorial"])
                
                # Start the maze game
                maze_result = MazeManager.start_maze(maze_map, description)
                
                # Extract data dari dictionary
                result = maze_result["result"]  # "WIN" atau "LOSE"
                finish_id = maze_result["finish_id"]  # "F", "F1", "F2", None
                steps = maze_result["steps"]
                
                # Update game state
                game_data["flags"]["last_maze"] = map_name
                game_data["flags"]["last_maze_result"] = result
                game_data["flags"]["last_maze_steps"] = steps
                game_data["flags"]["last_finish_id"] = finish_id
                
                if result == "WIN":
                    game_data["player_stats"]["mazes_completed"] = game_data["player_stats"].get("mazes_completed", 0) + 1

                # BRANCHING LOGIC
                target_scene = None
                
                # 1. Cari berdasarkan finish_id
                if finish_id and finish_id in branches:
                    target_scene = branches[finish_id]
                
                # 2. Fallback ke result (win/lose)
                elif result.lower() in branches:
                    target_scene = branches[result.lower()]
                
                # 3. Fallback ke default
                elif "default" in branches:
                    target_scene = branches["default"]
                
                # Jika tidak ada branch sama sekali
                else:
                    console.print("[red]✗ Tidak ada branch target yang ditemukan[/red]")
                
                if target_scene:
                    next_scene = target_scene
                    break
                else:
                    pause("[cyan]Tekan Enter untuk melanjutkan...[/cyan]")
                    continue
                
            # Update hangman handler:
            elif cmd["type"] == "hangman":
                console.print("\n" + "🎯" * 20, style="bold magenta")
                console.print("       HANGMAN CHALLENGE", style="bold magenta")
                console.print("🎯" * 20, style="bold magenta")
                
                branches = cmd.get("branches", {})
                config = cmd.get("config", {})
                
                # Start the hangman game
                result = HangmanManager.start_hangman(config)
                
                # Update game state
                game_data["flags"]["last_hangman"] = result
                game_data["flags"]["hangman_played"] = game_data["flags"].get("hangman_played", 0) + 1
                
                if result == "WIN":
                    game_data["player_stats"]["games_won"] = game_data["player_stats"].get("games_won", 0) + 1                
                # BRANCHING LOGIC
                outcome = result.lower()  # "win" atau "lose"
                target_scene = branches.get(outcome)
                
                if target_scene:
                    next_scene = target_scene
                    break
                else:
                    pause()
                    continue
        # AUTO-SAVE SETIAP SCENE BERUBAH
        if save_system and slot_name:
            save_system.create_save(game_data, slot_name)

        # Handle choices
        if choices and not next_scene:
            console.print("\n" + "═" * 50)
            console.print("[bold yellow]Apa yang ingin kamu lakukan?[/bold yellow]")
            
            choice_letters = [chr(97 + i) for i in range(len(choices))]
            choice_map = {}
            
            for i, choice in enumerate(choices):
                letter = choice_letters[i]
                choice_map[letter] = choice
                console.print(f"[bold cyan]{letter}.[/bold cyan] {choice['text']}")
            
            while True:
                try:
                    selection = input_no_empty(f"\nPilih ({'/'.join(choice_letters)}): ").strip().lower()
                    
                    if selection in choice_map:
                        selected_choice = choice_map[selection]
                        choice_record = {
                            "scene": current,
                            "choice": selected_choice["text"],
                            "target": selected_choice["target"]
                        }
                        choices_made.append(choice_record)
                        game_data["choices_history"] = choices_made
                        next_scene = selected_choice["target"]
                        
                        # ADD ITEMS BERDASARKAN SCENE
                        add_items_based_on_scene(current, game_data)
                        break
                    else:
                        console.print(f"[red]Pilih {', '.join(choice_letters)} saja![/red]")
                except KeyboardInterrupt:
                    return game_data

        if next_scene:
            current = next_scene
            continue
            
        break

    return game_data

def add_items_based_on_scene(scene_name, game_data):
    """Tambahkan item ke inventory berdasarkan scene"""
    item_rewards = {
        "cari_senter": "Senter",
        "explore_dengan_senter": "Peta sekolah", 
        "periksa_eksperimen": "Jurnal lab",
        "cari_baterai": "Baterai AA",
        "lihat_album": "Album foto misterius"
    }
    
    if scene_name in item_rewards:
        item = item_rewards[scene_name]
        if item not in game_data["inventory"]:
            game_data["inventory"].append(item)
            slow_print(f"🎒 Kamu mendapatkan: {item}")
    
    # Update player stats
    game_data["player_stats"]["discovered_secrets"] += 1
    

# ==============================
# VALIDATOR FUNCTIONS
# ==============================

def validate_engine():
    """Validator untuk runner.py"""
    import sys
    import os
    import builtins
    
    try:
        # SUPPRESS ALL OUTPUT
        import io
        from contextlib import redirect_stdout, redirect_stderr
        
        with open(os.devnull, 'w') as fnull, \
             redirect_stdout(fnull), \
             redirect_stderr(fnull):
            
            # MOCK BUILTINS INPUT
            original_input = builtins.input
            builtins.input = lambda prompt="": "a"
            
            # IMPORT ENGINE MODULES
            import engine.utils as utils
            import engine.runner as runner_module
            import engine.battle
            import engine.maze
            import engine.hangman
            
            # Backup
            backups = {}
            
            # 1. PATCH UTILS FUNCTIONS - INCLUDING DIRECT REFERENCE
            io_funcs = ['slow_print', 'input_no_empty', 'clear', 'pause', 'divider', 'progress_bar']
            for func in io_funcs:
                if hasattr(utils, func):
                    backups[func] = getattr(utils, func)
                    # GANTI SEMUA dengan lambda yang return 'a'
                    setattr(utils, func, lambda *a, **k: None)
            
            # OVERRIDE input_no_empty KHUSUS
            backups['input_no_empty_special'] = utils.input_no_empty
            utils.input_no_empty = lambda prompt="": "a"
            
            # Juga patch di runner module jika ada reference langsung
            if hasattr(runner_module, 'input_no_empty'):
                backups['runner_input'] = runner_module.input_no_empty
                runner_module.input_no_empty = lambda prompt="": "a"
            
            # Patch console
            if hasattr(utils, 'console'):
                backups['console'] = utils.console.print
                utils.console.print = lambda *a, **k: None
            
            # 2. PATCH DEPENDENCIES
            backups['battle_start'] = engine.battle.BattleManager.start_battle
            engine.battle.BattleManager.start_battle = lambda config=None: {
                "result": "WIN",
                "turns": 3
            }
            
            backups['maze_start'] = engine.maze.MazeManager.start_maze
            engine.maze.MazeManager.start_maze = lambda map_data, desc=None: {
                "result": "WIN",
                "finish_id": "F",
                "steps": 10
            }
            
            backups['hangman_start'] = engine.hangman.HangmanManager.start_hangman
            engine.hangman.HangmanManager.start_hangman = lambda config=None: "WIN"
            
            if hasattr(runner_module, 'MAZE_MAPS'):
                backups['maze_maps'] = runner_module.MAZE_MAPS
                runner_module.MAZE_MAPS = {
                    "tutorial": ["████", "█P █", "█ F█", "████"]
                }
            
            # Patch os.system
            backups['system'] = os.system
            os.system = lambda c: None
            
            # 3. CREATE TEST SCENES TANPA CHOICES (skip input)
            test_scenes = {
                "start": [
                    {"type": "text", "text": "Test scene 1"},
                    {"type": "goto", "target": "end"}  # Langsung goto, skip choices
                ],
                "end": [
                    {"type": "text", "text": "Test completed"}
                ]
            }
            
            # 4. TEST RUN_GAME
            game_data = {
                "current_chapter": 1,
                "current_scene": "start",
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
            
            result = runner_module.run_game(test_scenes, game_data)
            
            # 5. VALIDASI
            ok = isinstance(result, dict) and "current_scene" in result
            
            # 6. RESTORE
            builtins.input = original_input
            
            # Restore battle
            if 'battle_start' in backups:
                engine.battle.BattleManager.start_battle = backups['battle_start']
            
            if 'maze_start' in backups:
                engine.maze.MazeManager.start_maze = backups['maze_start']
            
            if 'hangman_start' in backups:
                engine.hangman.HangmanManager.start_hangman = backups['hangman_start']
            
            if 'maze_maps' in backups:
                runner_module.MAZE_MAPS = backups['maze_maps']
            
            if 'runner_input' in backups:
                runner_module.input_no_empty = backups['runner_input']
            
            # Restore utils
            for name, func in backups.items():
                if name == 'console':
                    utils.console.print = func
                elif name == 'system':
                    os.system = func
                elif name == 'input_no_empty_special':
                    utils.input_no_empty = func
                elif name in io_funcs and hasattr(utils, name):
                    setattr(utils, name, func)
            
            return {
                "module": "runner",
                "ok": ok,
                "result": result.get("current_scene") if ok else None
            }
    
    except Exception as e:
        # Restore input jika error
        if 'original_input' in locals():
            builtins.input = original_input
        return {
            "module": "runner",
            "ok": False,
            "error": f"{type(e).__name__}: {str(e)[:100]}"
        }
        