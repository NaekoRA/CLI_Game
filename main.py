from engine.parser import parse_story
from engine.runner import run_game
from engine.save_system import SaveSystem
from engine.utils import show_save_slots, select_save_slot, input_no_empty,pause
from datetime import datetime
import sys

def main_menu():
    save_system = SaveSystem()
    
    while True:
        print("\n" + "="*50)
        print("🎮 GAME HORROR ADVENTURE")
        print("="*50)
        print("1. 🚀 Main Baru")
        print("2. 💾 Load Game") 
        print("3. 🗑️  Hapus Save")
        print("4. 🚪 Keluar")
        
        choice = input_no_empty("\nPilih (1-4): ").strip()
        
        if choice == "1":
            start_new_game(save_system)
        elif choice == "2":
            load_game(save_system)
        elif choice == "3":
            delete_save(save_system)
        elif choice == "4":
            print("Terima kasih telah bermain!")
            break
        else:
            print("Pilihan tidak valid!")

def start_new_game(save_system):
    # Data awal game
    initial_data = {
        "current_chapter": 1,
        "current_scene": "start", 
        "checkpoint": "start",
        "inventory": [],
        "choices_history": [],
        "player_stats": {
            "health": 100, 
            "sanity": 100, 
            "discovered_secrets": 0
        },
        "flags": {},
        "play_time": 0,
        "created_at": datetime.now().isoformat()
    }
    
    # Buat save otomatis
    slot_name = "new_game"
    if save_system.create_save(initial_data, slot_name):
        print(f"✅ Game baru dibuat!")
        start_game(save_system, initial_data, slot_name)
    else:
        print("❌ Gagal membuat game baru")

def load_game(save_system):
    save_files = show_save_slots(save_system)
    if save_files:
        selected_slot = select_save_slot(save_files)
        if selected_slot:
            game_data = save_system.load_save(selected_slot)
            if game_data:
                print(f"✅ Load berhasil: {selected_slot}")
                start_game(save_system, game_data, selected_slot)
            else:
                print("❌ Gagal load game")

def delete_save(save_system):
    save_files = show_save_slots(save_system)
    if save_files:
        selected_slot = select_save_slot(save_files)
        if selected_slot:
            if save_system.delete_save(selected_slot):
                print(f"✅ Save dihapus: {selected_slot}")
            else:
                print("❌ Gagal menghapus save")

def start_game(save_system, game_data, slot_name):
    print(f"\n🎯 Memulai Chapter {game_data['current_chapter']}...")
    
    scenes = parse_story("story/chapter1.story")
    
    # run_game bisa return game_data ATAU "game_over"
    result = run_game(scenes, game_data, save_system, slot_name)
    
    # CEK JIKA HASILNYA "game_over"
    if result == "game_over":
        print("💀 Game Over! Kembali ke menu utama...")
        pause("\nTekan Enter untuk kembali ke menu...")
        return  # Langsung kembali ke menu, tidak save
    
    # JIKA NORMAL, result adalah updated_game_data
    updated_game_data = result
    updated_game_data["play_time"] += 120  # Tambah play time
    
    # Auto-save progress
    if save_system.create_save(updated_game_data, slot_name):
        print("💾 Progress tersimpan!")
    
    pause("\nTekan Enter untuk kembali ke menu...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n[Game dihentikan oleh user]")
        sys.exit(0)  # Keluar dari program