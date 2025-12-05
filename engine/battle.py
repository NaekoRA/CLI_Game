# engine/battle.py
import random
import os
import inspect
import sys
from unittest.mock import patch
from engine.utils import slow_print, input_no_empty, console, progress_bar, pause

class BattleGame:
    def __init__(self, player_hp=100, enemy_hp=100, player_name="Player", enemy_name="Musuh"):
        self.player_health = player_hp
        self.enemy_health = enemy_hp
        self.player_max_health = player_hp
        self.enemy_max_health = enemy_hp
        self.player_name = player_name
        self.enemy_name = enemy_name
        self.player_charging = 0
        self.enemy_charging = 0
        self.turn_count = 0
        self.game_over = False
        self.player_defending = False

    def _clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def _display_ui(self):
        self._clear_screen()
        console.print("=" * 60, style="bold cyan")
        console.print("           ⚔️  PERTARUNGAN TURN-BASED ⚔️", style="bold yellow")
        console.print("=" * 60, style="bold cyan")

        # Player HP Bar
        player_hp_percent = max(0, self.player_health) / self.player_max_health
        player_bar = "█" * int(player_hp_percent * 30) + " " * (30 - int(player_hp_percent * 30))
        
        # Enemy HP Bar  
        enemy_hp_percent = max(0, self.enemy_health) / self.enemy_max_health
        enemy_bar = "█" * int(enemy_hp_percent * 30) + " " * (30 - int(enemy_hp_percent * 30))

        console.print(f"\n[{self.player_name}]:", style="bold green")
        console.print(f"HP: [{player_bar}] {self.player_health}/{self.player_max_health}")

        status_player = []
        if self.player_charging > 0:
            status_player.append(f"⚡ CHARGING ({self.player_charging}/2)")
        if self.player_defending:
            status_player.append("🛡️ BERTAHAN")
        if status_player:
            console.print("Status: " + " ".join(status_player))

        console.print(f"\n[{self.enemy_name}]:", style="bold red")
        console.print(f"HP: [{enemy_bar}] {self.enemy_health}/{self.enemy_max_health}")

        status_enemy = []
        if self.enemy_charging > 0:
            status_enemy.append(f"⚡ CHARGING ({self.enemy_charging}/2)")
        if status_enemy:
            console.print("Status: " + " ".join(status_enemy))

        console.print(f"\n🔄 Turn: {self.turn_count}", style="bold")
        console.print("-" * 60, style="dim")

    def _display_moves(self):
        console.print("\n🎯 PILIH AKSI:", style="bold yellow")
        
        if self.player_charging > 0:
            console.print("⚡ Anda sedang CHARGING serangan kuat!", style="bold cyan")
            if self.player_charging == 1:
                console.print("➤ CHARGING... (1/2) - Tekan Enter untuk melanjutkan")
            else:
                console.print("➤ CHARGING SELESAI! (2/2) - Tekan Enter untuk menyerang")
            console.print("\nTekan Enter untuk melanjutkan...", end="")
            return ["continue"]

        moves = []
        console.print("a. ⚔️  SERANG CEPAT (15-25 damage)")
        moves.append("a")

        console.print("b. ⚡ SERANG KUAT (20-60 damage, butuh 2 turn charging)")
        moves.append("b")

        console.print("c. 🛡️  BERTAHAN (kurangi damage 50% untuk 1 turn)")
        moves.append("c")

        console.print("d. ❤️  HEAL (pulihkan 15-25 HP)")
        moves.append("d")

        console.print("e. 🏳️  MENYERAH (langsung kalah)")
        moves.append("e")

        return moves

    def _player_attack_fast(self):
        damage = random.randint(15, 25)
        self.enemy_health -= damage
        return damage

    def _player_heal(self):
        heal_amount = random.randint(15, 25)
        self.player_health = min(self.player_max_health, self.player_health + heal_amount)
        return heal_amount

    def player_start_charge(self):
        if self.player_charging == 0:
            self.player_charging = 1
            return "Anda mulai CHARGING serangan kuat! (1/2)"
        return ""

    def player_continue_charge(self):
        if self.player_charging == 1:
            self.player_charging = 2
            return "Anda melanjutkan CHARGING! (2/2) - Siap menyerang turn depan!"
        elif self.player_charging == 2:
            damage = random.randint(20, 60)
            self.enemy_health -= damage
            self.player_charging = 0
            return damage, "Serangan kuat TERLEPAS! ⚡"
        return 0, "Charging belum selesai!"

    def player_defend(self):
        self.player_defending = True
        return "Anda dalam mode BERTAHAN! Damage dikurangi 50%"

    def enemy_ai(self):
        # Reset player defending status
        self.player_defending = False

        if self.enemy_charging > 0:
            self.enemy_charging += 1
            if self.enemy_charging >= 3:
                damage = random.randint(25, 40)
                self.player_health -= damage
                self.enemy_charging = 0
                return damage, f"{self.enemy_name} melepaskan serangan kuat! ⚡ {damage} damage!"
            return 0, f"{self.enemy_name} mengumpulkan kekuatan... ({self.enemy_charging}/2)"

        # AI Decision Making
        choice = random.random()
        
        if choice < 0.2 and self.enemy_health < self.enemy_max_health * 0.5:
            # Healing when low HP
            heal_amount = random.randint(10, 20)
            self.enemy_health = min(self.enemy_max_health, self.enemy_health + heal_amount)
            return 0, f"{self.enemy_name} memulihkan {heal_amount} HP! ❤️"
        
        elif choice < 0.3 and self.enemy_charging == 0:
            # Start charging
            self.enemy_charging = 1
            return 0, f"{self.enemy_name} mulai mengisi energi... (1/2)"
        
        else:
            # Normal attack
            damage = random.randint(12, 22)
            self.player_health -= damage
            return damage, f"{self.enemy_name} menyerang cepat! ⚔️ {damage} damage!"

    def process_turn(self, player_choice, available_moves):
        player_message = ""
        enemy_message = ""

        if self.player_charging > 0:
            if self.player_charging == 1:
                self.player_charging = 2
                player_message = "Anda melanjutkan CHARGING! (2/2) - Siap menyerang turn depan!"
            else:
                damage, msg = self.player_continue_charge()
                player_message = f"{msg} {damage} damage!"

        elif player_choice not in available_moves:
            player_message = "Pilihan tidak valid! Melewatkan turn."

        elif player_choice == "a":
            damage = self._player_attack_fast()
            player_message = f"Anda menyerang cepat! ⚔️ {damage} damage!"

        elif player_choice == "b":
            player_message = self.player_start_charge()

        elif player_choice == "c":
            player_message = self.player_defend()

        elif player_choice == "d":
            heal_amount = self._player_heal()
            player_message = f"Anda memulihkan {heal_amount} HP! ❤️"

        elif player_choice == "e":
            self.game_over = True
            return "MENYERAH", f"Anda menyerah! {self.enemy_name} menang."

        if not self.game_over:
            damage, enemy_msg = self.enemy_ai()

            # Apply defense reduction
            if self.player_defending and damage > 0:
                original_damage = damage
                damage = max(1, damage // 2)
                enemy_msg += f" (Dikurangi 50% karena bertahan → {damage} damage)"

            enemy_message = enemy_msg

        self.turn_count += 1
        return player_message, enemy_message

    def check_winner(self):
        if self.player_health <= 0 and self.enemy_health <= 0:
            return "DRAW"
        elif self.player_health <= 0:
            return "MUSUH"
        elif self.enemy_health <= 0:
            return "PLAYER"
        return None

    def show_battle_result(self, player_msg, enemy_msg):
        console.print(f"\n{'='*60}", style="bold cyan")
        console.print("📊 HASIL TURN:", style="bold yellow")
        
        if player_msg:
            console.print(f"➤ {self.player_name}: {player_msg}", style="green")
        if enemy_msg:
            console.print(f"➤ {self.enemy_name}: {enemy_msg}", style="red")
            
        console.print(f"{'='*60}", style="bold cyan")
        
        # Show updated health
        console.print(f"\n🔄 Update Health:")
        console.print(f"{self.player_name} HP: {max(0, self.player_health)}/{self.player_max_health}")
        console.print(f"{self.enemy_name} HP: {max(0, self.enemy_health)}/{self.enemy_max_health}")

        pause()

    def run(self):
        console.print(f"\n⚔️  {self.player_name} vs {self.enemy_name}!", style="bold red")
        
        while not self.game_over:
            self._display_ui()
            available_moves = self._display_moves()
            
            try:
                if available_moves == ["continue"]:
                    choice = "continue"
                    input()
                else:
                    choice = input_no_empty(f"\nPilih aksi ({'/'.join(available_moves)}): ").strip().lower()
            except KeyboardInterrupt:
                console.print("\n\n🛑 Pertarungan dihentikan!", style="red")
                return "INTERRUPT"

            player_msg, enemy_msg = self.process_turn(choice, available_moves)
            
            if choice != "e":
                self.show_battle_result(player_msg, enemy_msg)
            
            winner = self.check_winner()
            if winner:
                self.game_over = True
                self._display_ui()

                if winner == "PLAYER":
                    console.print(f"\n🎉 VICTORY! {self.player_name} menang dalam {self.turn_count} turn!", style="bold green")
                    progress_bar(2, "Merayakan kemenangan")
                    return {
                        "result": "WIN",
                        "turns": self.turn_count,
                        "player_remaining_hp": self.player_health,
                        "enemy_remaining_hp": self.enemy_health
                    }
                elif winner == "MUSUH":
                    console.print(f"\n💀 DEFEAT! {self.enemy_name} menang dalam {self.turn_count} turn!", style="bold red")
                    return {
                        "result": "LOSE", 
                        "turns": self.turn_count,
                        "player_remaining_hp": self.player_health,
                        "enemy_remaining_hp": self.enemy_health
                    }
                else:
                    console.print(f"\n🤝 DRAW! Keduanya kalah dalam {self.turn_count} turn!", style="bold yellow")
                    return {
                        "result": "DRAW",
                        "turns": self.turn_count,
                        "player_remaining_hp": self.player_health,
                        "enemy_remaining_hp": self.enemy_health
                    }
            
            if choice == "e":
                self._display_ui()
                console.print(f"\n🏳️  Anda menyerah! {self.enemy_name} menang!", style="red")
                return {
                    "result": "SURRENDER",
                    "turns": self.turn_count,
                    "player_remaining_hp": self.player_health,
                    "enemy_remaining_hp": self.enemy_health
                }

# Battle Manager untuk handle dari story
class BattleManager:
    @staticmethod
    def start_battle(config=None):
        if config is None:
            config = {}
        
        # Default configuration
        player_hp = config.get('player_hp', 100)
        enemy_hp = config.get('enemy_hp', 100)
        player_name = config.get('player_name', 'Player')
        enemy_name = config.get('enemy_name', 'Musuh')
        
        battle = BattleGame(player_hp, enemy_hp, player_name, enemy_name)
        result = battle.run()
        
        return result

# ==============================
# VALIDATOR FUNCTIONS
# ==============================

def validate_engine():
    """Validator utama - silent dan cepat"""
    import sys
    import os
    
    try:
        # Backup original functions
        import engine.utils as utils
        import engine.battle as battle_module
        
        # Simpan semua fungsi yang akan di-patch
        backup = {}
        funcs_to_patch = [
            ('slow_print', lambda x, **k: None),
            ('input_no_empty', lambda p="": "a"),
            ('clear', lambda: None),
            ('pause', lambda m=None: None),
            ('divider', lambda *a, **k: None),
            ('progress_bar', lambda *a, **k: None)
        ]
        
        # Patch utils
        for name, replacement in funcs_to_patch:
            if hasattr(utils, name):
                backup[name] = getattr(utils, name)
                setattr(utils, name, replacement)
        
        # Patch console.print
        if hasattr(utils, 'console'):
            backup['console_print'] = utils.console.print
            utils.console.print = lambda *a, **k: None
        
        # Patch di battle module
        for name, replacement in funcs_to_patch:
            if hasattr(battle_module, name):
                setattr(battle_module, name, replacement)
        
        # Patch os.system untuk clear_screen
        backup_system = os.system
        os.system = lambda c: None
        
        # Run battle
        result = BattleManager.start_battle({
            'player_hp': 30,
            'enemy_hp': 30,
            'player_name': 'Validator',
            'enemy_name': 'TestBot'
        })
        
        # Restore semua
        for name, func in backup.items():
            if name == 'console_print':
                utils.console.print = func
            else:
                setattr(utils, name, func)
        
        os.system = backup_system
        
        # Validasi hasil
        return {
            "module": "battle",
            "ok": isinstance(result, dict) and 'result' in result,
            "result": result.get('result') if isinstance(result, dict) else None
        }
            
    except Exception as e:
        return {
            "module": "battle",
            "ok": False,
            "error": f"{type(e).__name__}: {str(e)}"
        }
