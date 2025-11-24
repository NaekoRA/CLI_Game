import os
import sys
import time
import random
import msvcrt
from rich.console import Console
from rich.text import Text
from rich.table import Table
from datetime import datetime

console = Console()

def show_save_slots(save_system):
    save_files = save_system.get_save_files()
    
    if not save_files:
        console.print("[yellow]Tidak ada save game yang tersedia.[/yellow]")
        return []
    
    table = Table(title="💾 Save Games", show_header=True, header_style="bold magenta")
    table.add_column("No", style="cyan", width=5)
    table.add_column("Slot Name", style="green")
    table.add_column("Timestamp", style="yellow")
    
    for i, save_file in enumerate(save_files, 1):
        slot_name = save_file.replace('.json', '')
        info = save_system.get_save_info(slot_name)
        if info:
            timestamp = datetime.fromisoformat(info['timestamp']).strftime("%d/%m/%Y %H:%M")
            table.add_row(str(i), info['slot_name'], timestamp)
    
    console.print(table)
    return save_files

def select_save_slot(save_files):
    if not save_files:
        return None
    
    while True:
        try:
            choice = input("\nPilih save slot (1-{} atau 0 untuk batal): ".format(len(save_files))).strip()
            if choice == '0':
                return None
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(save_files):
                return save_files[choice_idx].replace('.json', '')
            else:
                console.print("[red]Pilihan tidak valid![/red]")
        except ValueError:
            console.print("[red]Masukkan angka![/red]")
        except KeyboardInterrupt:
            return None

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def slow_print(text, delay=0.03, newline=True):
    i = 0
    while i < len(text):
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b"\r":
                console.print(text[i:], end="")
                break
        console.print(text[i], end="")
        time.sleep(delay)
        i += 1
    if newline:
        print()

def type_effect_dialog(speaker, text, delay=0.03):
    console.print(f"{speaker}: ", end="")
    slow_print(text, delay=delay)


def divider(symbol="=", length=50):
    print(symbol * length)


def pause(message="\nTekan Enter untuk melanjutkan..."):
    input(message)


def random_choice(options):
    return random.choice(options)


def coin_flip():
    return random.choice(["Head", "Tail"])


def dice_roll(sides=6):
    return random.randint(1, sides)


def hompimpa(players):
    slow_print("Hompimpa alaium gambreng!\n")
    time.sleep(0.5)
    hasil = {p: random.choice(["kiri", "kanan"]) for p in players}
    for p, h in hasil.items():
        print(f"{p}: {h}")
        time.sleep(0.3)
    same = all(h == list(hasil.values())[0] for h in hasil.values())
    if same:
        slow_print("\nSeri! Ulangi lagi...\n")
        time.sleep(1)
        return hompimpa(players)
    else:
        winner = random_choice(players)
        slow_print(f"\n🎉 Pemenang hompimpa adalah {winner}!\n")
        return winner


def rock_paper_scissors():
    choices = ["batu", "gunting", "kertas"]
    slow_print("Pilih: batu / gunting / kertas")
    player = input("> ").strip().lower()
    enemy = random_choice(choices)

    slow_print(f"Komputer memilih: {enemy}")
    if player == enemy:
        return "draw"
    elif (
        (player == "batu" and enemy == "gunting")
        or (player == "gunting" and enemy == "kertas")
        or (player == "kertas" and enemy == "batu")
    ):
        return "win"
    else:
        return "lose"


def type_effect_dialog(speaker, text, delay=0.03):
    slow_print(f"{speaker}: ", delay=0.02, newline=False)
    slow_print(text, delay=delay)


def progress_bar(duration=2, label="Memproses"):
    sys.stdout.write(f"{label}: [")
    sys.stdout.flush()
    for _ in range(30):
        time.sleep(duration / 30)
        sys.stdout.write("█")
        sys.stdout.flush()
    sys.stdout.write("]\n")


def random_delay_text(texts):
    for t in texts:
        slow_print(t)
        time.sleep(random.uniform(0.5, 1.5))


def input_no_empty(prompt):
    buffer = ""
    sys.stdout.write(prompt)
    sys.stdout.flush()

    while True:
            key = msvcrt.getch()
            
            # Handle Ctrl+C (KeyboardInterrupt)
            if key == b'\x03':
                raise KeyboardInterrupt()
            
            if key == b"\r":
                if buffer.strip() == "":
                    continue
                else:
                    print()
                    return buffer.strip()

            elif key == b"\x08":  # Backspace
                if len(buffer) > 0:
                    buffer = buffer[:-1]
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()

            elif key.isalnum() or key in b" ,.-_=+!?:":
                buffer += key.decode()
                sys.stdout.write(key.decode())
                sys.stdout.flush()

        