from .utils import slow_print, console, input_no_empty ,clear, divider, pause,progress_bar
from engine.battle import BattleManager
from rich.text import Text
from rich.panel import Panel

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
            
            elif cmd["type"] == "battle":
                console.print("\n" + "⚔️" * 20, style="bold red")
                console.print("          PERTARUNGAN DIMULAI!", style="bold red")
                console.print("⚔️" * 20, style="bold red")
                
                result = BattleManager.start_battle(cmd.get("config", {}))
                
                if result == "WIN":
                    slow_print("🎉 Kamu memenangkan pertarungan!")
                    # Tambah item atau flag untuk kemenangan
                    if "kemenangan_pertarungan" not in game_data["flags"]:
                        game_data["flags"]["kemenangan_pertarungan"] = True
                elif result == "LOSE":
                    slow_print("💀 Kamu kalah dalam pertarungan...")
                    return "game_over"  # ← INI MASIH RETURN STRING!
                elif result == "DRAW":
                    slow_print("🤝 Pertarungan berakhir seri!")
                elif result == "SURRENDER":
                    slow_print("🏳️ Kamu menyerah dalam pertarungan...")
                    return "game_over"  # ← INI JUGA
                
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