import json
import os
from datetime import datetime

class SaveSystem:
    def __init__(self, save_dir="saves"):
        self.save_dir = save_dir
        self.ensure_save_dir()
    
    def ensure_save_dir(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def get_save_files(self):
        saves = []
        if os.path.exists(self.save_dir):
            for file in os.listdir(self.save_dir):
                if file.endswith('.json'):
                    saves.append(file)
        return sorted(saves)
    
    def create_save(self, game_data, slot_name=None):
        if slot_name is None:
            slot_name = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        save_path = os.path.join(self.save_dir, f"{slot_name}.json")
        
        save_data = {
            "metadata": {
                "slot_name": slot_name,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0"
            },
            "game_data": game_data
        }
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_save(self, slot_name):
        save_path = os.path.join(self.save_dir, f"{slot_name}.json")
        
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            return save_data["game_data"]
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    def delete_save(self, slot_name):
        save_path = os.path.join(self.save_dir, f"{slot_name}.json")
        try:
            if os.path.exists(save_path):
                os.remove(save_path)
                return True
        except Exception as e:
            print(f"Error deleting save: {e}")
        return False
    
    def get_save_info(self, slot_name):
        save_path = os.path.join(self.save_dir, f"{slot_name}.json")
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            return save_data["metadata"]
        except:
            return None