from .utils import slow_print, console, input_no_empty ,clear, divider, pause,progress_bar
from engine.battle import BattleManager
from rich.text import Text
from rich.panel import Panel
from engine.maze import MazeManager
from maze_maps import MAZE_MAPS


def run_game(scenes, game_data=None, save_system=None, slot_name=None):
    if game_data is None:
        game_data = {
            "current_chapter": 1,
            "current_scene": "start",
            "checkpoint": "start", 
            "inventory": [],
            "choices_history": [],
            "player_stats": {"health": 100, "sanity": 100, "discovered_secrets": 0},
            "flags": {},
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
                    game_data["player_stats"]["sanity"] = max(0, game_data["player_stats"]["sanity"] - 15)
                
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
                result = MazeManager.start_maze(maze_map, description)
                
                # Update game state based on maze result
                game_data["flags"]["last_maze"] = map_name
                game_data["flags"]["last_maze_result"] = result
                
                if result == "WIN":
                    game_data["player_stats"]["mazes_completed"] = game_data["player_stats"].get("mazes_completed", 0) + 1
                    slow_print("🎉 Kamu berhasil menyelesaikan maze!")
                elif result == "LOSE":
                    game_data["player_stats"]["sanity"] = max(0, game_data["player_stats"]["sanity"] - 10)
                    slow_print("💀 Kamu gagal dalam maze...")
                
                # BRANCHING LOGIC - HANYA win dan lose
                outcome = result.lower()  # "win" atau "lose"
                
                # Cari branch target berdasarkan outcome
                target_scene = branches.get(outcome)
                
                if target_scene:
                    # Jika ada branch target, pindah scene
                    next_scene = target_scene
                    break
                else:
                    # Jika tidak ada branch, lanjut scene berikutnya
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
    game_data["player_stats"]["sanity"] = max(0, game_data["player_stats"]["sanity"] - 5)