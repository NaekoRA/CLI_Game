import os
import sys
import time
import random
from collections import deque

# Simulasi console jika engine.utils tidak ada
try:
    from engine.utils import console
except ImportError:
    class DummyConsole:
        def print(self, *args, **kwargs):
            print(*args, **kwargs)
    console = DummyConsole()

# Handle keyboard input untuk Windows
if os.name == "nt":
    import msvcrt
    
    def get_key():
        if not msvcrt.kbhit():
            return None
        key = msvcrt.getch()
        if key == b"\xe0":
            key2 = msvcrt.getch()
            if key2 == b"H": return "up"
            if key2 == b"P": return "down"
            if key2 == b"K": return "left"
            if key2 == b"M": return "right"
            return None
        try:
            return key.decode("utf-8").lower()
        except:
            return None
else:
    # Untuk non-Windows, kita buat sederhana
    import tty
    import termios
    
    def get_key():
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                if ch == '\x1b':  # arrow key
                    ch2 = sys.stdin.read(1)
                    ch3 = sys.stdin.read(1)
                    if ch2 == '[':
                        if ch3 == 'A': return "up"
                        if ch3 == 'B': return "down"
                        if ch3 == 'C': return "right"
                        if ch3 == 'D': return "left"
                return ch.lower()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except:
            return None

class MazeGame:
    def __init__(self, map_data):
        self.maze = [list(row) for row in map_data]
        self.original_maze = [list(row) for row in map_data]
        self.finish_points = {}
        self.player = None
        self.enemy = None
        
        # Mapping karakter ke finish_id
        self.finish_mapping = {
            'F': 'F',    # Finish standar
            '1': 'F1',   # Finish 1
            '2': 'F2',   # Finish 2
            '3': 'F3',   # Finish 3
            '4': 'F4',   # Finish 4
            '5': 'F5',   # Finish 5
            'a': 'FA',   # Finish A
            'b': 'FB',   # Finish B
            'c': 'FC',   # Finish C
            'd': 'FD',   # Finish D
            'e': 'FE',   # Finish E
        }
        
        self.find_characters()
        self.steps = 0

        self.state = "ROAMING"
        self.last_seen_time = 0
        self.visited = {}

        self.last_output = ""
        self.screen_cleared = False

    def find_characters(self):
        """Temukan semua karakter di maze termasuk multiple finish points"""
        for y, row in enumerate(self.original_maze):
            for x, c in enumerate(row):
                if c == "P":
                    self.player = [x, y]
                    print(f"[DEBUG] Player ditemukan di ({x}, {y})")
                
                if c == "S":
                    self.enemy = [x, y]
                    print(f"[DEBUG] Enemy ditemukan di ({x}, {y})")
                
                # Cek apakah karakter adalah finish point
                if c in self.finish_mapping:
                    finish_id = self.finish_mapping[c]
                    self.finish_points[finish_id] = [x, y]
                    print(f"[DEBUG] Finish point '{finish_id}' ditemukan di ({x}, {y})")
    
    def is_wall(self, x, y):
        """Cek apakah posisi (x,y) adalah wall"""
        if y < 0 or y >= len(self.original_maze):
            return True
        if x < 0 or x >= len(self.original_maze[y]):
            return True
        return self.original_maze[y][x] == "█"

    def is_finish(self, x, y):
        """Cek apakah posisi adalah finish point"""
        if y < 0 or y >= len(self.original_maze):
            return False
        if x < 0 or x >= len(self.original_maze[y]):
            return False
        c = self.original_maze[y][x]
        return c in self.finish_mapping

    def get_finish_id(self, x, y):
        """Dapatkan ID finish point"""
        if y < 0 or y >= len(self.original_maze):
            return None
        if x < 0 or x >= len(self.original_maze[y]):
            return None
        c = self.original_maze[y][x]
        return self.finish_mapping.get(c, None)
    
    def can_see_player(self):
        """Cek apakah enemy bisa melihat player (line of sight)"""
        if not self.enemy:
            return False
        px, py = self.player
        ex, ey = self.enemy

        # Cek vertical line of sight
        if px == ex:
            step = 1 if py > ey else -1
            for y in range(ey + step, py, step):
                if self.is_wall(ex, y):
                    return False
            return True

        # Cek horizontal line of sight
        if py == ey:
            step = 1 if px > ex else -1
            for x in range(ex + step, px, step):
                if self.is_wall(x, ey):
                    return False
            return True

        return False

    def bfs(self, start, goal):
        """Breadth-First Search untuk mencari path terpendek"""
        sx, sy = start
        gx, gy = goal
        queue = deque([(sx, sy)])
        visited = {(sx, sy): None}

        while queue:
            x, y = queue.popleft()
            if (x, y) == (gx, gy):
                # Rekonstruksi path
                path = []
                while (x, y) != (sx, sy):
                    path.append((x, y))
                    x, y = visited[(x, y)]
                path.reverse()
                return path

            # Cek 4 arah
            for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                nx, ny = x + dx, y + dy

                if ny < 0 or ny >= len(self.original_maze): continue
                if nx < 0 or nx >= len(self.original_maze[ny]): continue
                if (nx, ny) in visited: continue
                if self.is_wall(nx, ny): continue

                visited[(nx, ny)] = (x, y)
                queue.append((nx, ny))
        return None

    def move_enemy_chasing(self):
        """Gerakkan enemy saat mode chasing"""
        if not self.enemy:
            return False
        
        path = self.bfs(tuple(self.enemy), tuple(self.player))
        if not path:
            return False
        
        nx, ny = path[0]  # Langkah pertama di path
        ex, ey = self.enemy

        # Kosongkan posisi enemy lama jika bukan finish point
        if not self.is_finish(ex, ey) and [ex, ey] != self.player:
            self.maze[ey][ex] = " "
        
        # Tempatkan enemy di posisi baru jika bukan finish point
        if not self.is_finish(nx, ny) and [nx, ny] != self.player:
            self.maze[ny][nx] = "S"
        
        self.enemy[:] = [nx, ny]
        return True

    def get_visit(self, x, y):
        """Dapatkan jumlah kunjungan ke posisi (x,y)"""
        return self.visited.get((x, y), 0)

    def add_visit(self, x, y):
        """Tambah counter kunjungan ke posisi (x,y)"""
        self.visited[(x, y)] = self.get_visit(x, y) + 1

    def decay_visits(self):
        """Kurangi counter kunjungan secara bertahap"""
        remove_keys = []
        for k in self.visited:
            self.visited[k] -= 0.02   
            if self.visited[k] <= 0:
                remove_keys.append(k)
        for k in remove_keys:
            del self.visited[k]
        
    def move_enemy_roaming(self):
        """Gerakkan enemy saat mode roaming"""
        if not self.enemy:
            return False
        
        ex, ey = self.enemy
        
        # Semua arah yang mungkin
        dirs = [(1,0), (-1,0), (0,1), (0,-1)]
        candidates = []

        for dx, dy in dirs:
            nx, ny = ex + dx, ey + dy
            
            # Cek apakah langkah valid
            if (0 <= ny < len(self.original_maze) and
                0 <= nx < len(self.original_maze[ny]) and
                not self.is_wall(nx, ny)):

                # Prioritaskan tempat yang jarang dikunjungi
                visit_score = self.get_visit(nx, ny)
                candidates.append(((nx, ny), visit_score))

        if not candidates:
            return False

        # Pilih tempat dengan kunjungan paling sedikit
        min_visit = min(v for pos, v in candidates)
        best_moves = [pos for pos, v in candidates if v == min_visit]

        nx, ny = random.choice(best_moves)

        # Update visit counters
        self.add_visit(nx, ny)
        self.decay_visits()

        # Update posisi enemy di visual maze
        ex, ey = self.enemy
        if not self.is_finish(ex, ey) and [ex, ey] != self.player:
            self.maze[ey][ex] = " "
        
        if not self.is_finish(nx, ny) and [nx, ny] != self.player:
            self.maze[ny][nx] = "S"
        
        self.enemy[:] = [nx, ny]
        return True

    def build_frame(self):
        """Buat frame untuk ditampilkan"""
        lines = []
        lines.append("🧭" * 20)
        lines.append("           MAZE CHALLENGE")
        lines.append("🧭" * 20)
        lines.append("")

        for y, row in enumerate(self.maze):
            line = ""
            for x, c in enumerate(row):
                original_cell = self.original_maze[y][x]
                
                # Render karakter
                if c == "P": 
                    line += "😎"
                elif c == "S": 
                    line += "👻"
                elif c == "█": 
                    line += "🧱"
                elif original_cell in self.finish_mapping:
                    # Semua finish point ditampilkan sebagai 🏁
                    line += "🏁"
                else: 
                    line += "  "
            lines.append(line)

        # Info panel
        lines.append("")
        lines.append("🎮 Controls: WASD/Arrow Keys | Q: Quit")
        lines.append("🎯 Goal: Reach 🏁 (Available: " + ", ".join(self.finish_points.keys()) + ")")
        lines.append("⚠️ Enemy: 👻")
        lines.append(f"👣 Steps: {self.steps}")
        lines.append(f"STATE: {self.state}")
        
        return "\n".join(lines)

    def render(self):
        """Render maze ke screen"""
        new_output = self.build_frame()
        if new_output != self.last_output:
            if not self.screen_cleared:
                os.system('cls' if os.name == 'nt' else 'clear')
                self.screen_cleared = True
            else:
                print(f"\033[{new_output.count(chr(10)) + 1}A", end="")
            print(new_output)
            self.last_output = new_output

    def start(self):
        """Main game loop"""
        enemy_delay = 0.35
        last_enemy_time = time.time()
        self.render()

        while True:
            now = time.time()
            moved = False

            # Player movement
            key = get_key()
            if key in ["w","up","s","down","a","left","d","right", "q"]:
                if key == "q":  # Quit key
                    return "QUIT", None
                    
                dx = dy = 0
                if key in ["w","up"]: dy = -1
                if key in ["s","down"]: dy = 1
                if key in ["a","left"]: dx = -1
                if key in ["d","right"]: dx = 1

                px, py = self.player
                nx, ny = px + dx, py + dy

                # Validasi pergerakan
                if (0 <= ny < len(self.original_maze) and
                    0 <= nx < len(self.original_maze[ny]) and
                    not self.is_wall(nx, ny)):

                    self.steps += 1

                    # Cek apakah mencapai finish point
                    if self.is_finish(nx, ny):
                        finish_id = self.get_finish_id(nx, ny)
                        self.maze[py][px] = " "
                        self.maze[ny][nx] = "P"
                        self.player[:] = [nx, ny]
                        self.render()
                        print(f"\n🎉 MAZE COMPLETED via {finish_id}! Steps: {self.steps}")
                        return "WIN", finish_id

                    # Pergerakan normal
                    if [px, py] != self.enemy:
                        self.maze[py][px] = " "
                    self.maze[ny][nx] = "P"
                    self.player[:] = [nx, ny]
                    moved = True

            # Enemy AI
            if self.enemy and now - last_enemy_time > enemy_delay:
                last_enemy_time = now

                # Update state berdasarkan line of sight
                if self.can_see_player():
                    self.state = "CHASING"
                    self.last_seen_time = time.time()
                else:
                    if self.state == "CHASING" and time.time() - self.last_seen_time > 5:
                        self.state = "ROAMING"

                # Gerakkan enemy berdasarkan state
                if self.state == "CHASING":
                    moved = self.move_enemy_chasing() or moved
                else:
                    moved = self.move_enemy_roaming() or moved

            # Cek collision dengan enemy
            if self.enemy == self.player:
                self.render()
                print(f"\n💀 CAUGHT BY ENEMY! Steps: {self.steps}")
                return "LOSE", None

            # Render jika ada perubahan
            if moved:
                self.render()

            time.sleep(0.016)

class MazeManager:
    @staticmethod
    def start_maze(map_data, description="Find your way through the maze!"):
        """Start maze game dan return result dictionary"""
        console.print(f"\n{description}", style="bold yellow")
        console.print("Loading maze...", style="dim")
        time.sleep(1)

        maze_game = MazeGame(map_data)
        
        # Jalankan game dan dapatkan result
        result, finish_id = maze_game.start()
        
        # Return dictionary dengan semua data
        return {
            "result": result,
            "finish_id": finish_id,
            "steps": maze_game.steps
        }

# ==================== TEST CODE ====================
if __name__ == "__main__":
    print("=== MAZE.PY STANDALONE TEST ===")
    print("Testing multiple finish points system...")
    
    # Test mazes dengan format yang BENAR
    TEST_MAZES = {
        "single": [
            "████████",
            "█P     █",
            "█ ████ █",
            "█      █",
            "█████F██",
            "█      █",
            "████████",
        ],
        "double": [
            "██████████",
            "█P       █",
            "█ ██████ █",
            "█ █    █ █",
            "█ █ 1  █ █",  # '1' untuk F1
            "█ ██████ █",
            "█        █",
            "█ ██████ █",
            "█    2   █",  # '2' untuk F2
            "██████████",
        ],
        "triple": [
            "████████████",
            "█P         █",
            "█ ███ ███ ██",
            "█ █ 1 █   ██",  # '1' untuk F1
            "█ ███████ ██",
            "█         ██",
            "█ ███ ███ ██",
            "█   █   █ ██",
            "███ █ █ █ ██",
            "█     █ 2 ██",  # '2' untuk F2
            "█ ██████████",
            "█     3    █",  # '3' untuk F3
            "████████████",
        ]
    }
    
    print("\nPilih maze untuk test:")
    print("1. Single finish (F)")
    print("2. Double finish (F1, F2)")  
    print("3. Triple finish (F1, F2, F3)")
    
    try:
        choice = input("Pilihan (1-3): ").strip()
    except:
        choice = "1"
    
    if choice == "1":
        maze_data = TEST_MAZES["single"]
        maze_name = "single_finish"
    elif choice == "2":
        maze_data = TEST_MAZES["double"]
        maze_name = "double_finish"
    elif choice == "3":
        maze_data = TEST_MAZES["triple"]
        maze_name = "triple_finish"
    else:
        print("Pilihan tidak valid, menggunakan maze 1")
        maze_data = TEST_MAZES["single"]
        maze_name = "single_finish"
    
    print(f"\n{'='*50}")
    print(f"Memulai maze: {maze_name}")
    print(f"{'='*50}")
    print("Kontrol: WASD atau Arrow Keys")
    print("Goal: Capai 🏁 finish point")
    print("Tekan Q untuk quit")
    print("-" * 40)
    
    # Tunggu sebelum mulai
    time.sleep(1)
    
    # Buat instance game
    game = MazeGame(maze_data)
    
    # Jalankan game
    print("\nStarting game in 2 seconds...")
    time.sleep(2)
    
    result, finish_id = game.start()
    
    print(f"\n{'='*50}")
    print("FINAL RESULT:")
    print(f"  Result: {result}")
    print(f"  Finish ID: {finish_id}")
    print(f"  Steps: {game.steps}")
    print(f"{'='*50}")
    
    # Test branching logic
    print("\nBRANCHING SIMULATION:")
    
    # Contoh branches
    test_branches = {
        "F": "scene_normal",
        "F1": "scene_treasure",
        "F2": "scene_secret",
        "F3": "scene_dark",
        "FA": "scene_magic",
        "FB": "scene_beast",
        "win": "scene_generic_win",
        "lose": "scene_game_over",
        "default": "scene_main"
    }
    
    print(f"Available branches: {test_branches}")
    
    if result == "WIN" and finish_id:
        if finish_id in test_branches:
            print(f"✓ Player akan pergi ke: {test_branches[finish_id]} (via {finish_id})")
        elif "win" in test_branches:
            print(f"✓ Player akan pergi ke: {test_branches['win']} (via 'win' fallback)")
        elif "default" in test_branches:
            print(f"✓ Player akan pergi ke: {test_branches['default']} (via 'default' fallback)")
        else:
            print("✗ Tidak ada branch yang cocok!")
    elif result == "LOSE":
        if "lose" in test_branches:
            print(f"✗ Player akan pergi ke: {test_branches['lose']} (via 'lose')")
        elif "default" in test_branches:
            print(f"✗ Player akan pergi ke: {test_branches['default']} (via 'default' fallback)")
        else:
            print("✗ Tidak ada branch untuk kekalahan!")
    elif result == "QUIT":
        print("↩ Player quit game")
    
    print(f"\n{'='*50}")
    print("TEST COMPLETE!")
    print("="*50)
    
    try:
        input("\nPress Enter to exit...")
    except:
        pass