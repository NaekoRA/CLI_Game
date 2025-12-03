import os
import sys
import time
import random
from collections import deque

if os.name == "nt":
    import msvcrt
from engine.utils import console

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

class MazeGame:
    def __init__(self, map_data):
        self.maze = [list(row) for row in map_data]
        self.original_maze = [list(row) for row in map_data]
        self.finish_points = {}
        self.player = None
        self.enemy = None
        
        # TAMBAHKAN: Mapping karakter ke finish_id
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
        }
        
        self.find_characters()
        self.steps = 0

        self.state = "ROAMING"
        self.last_seen_time = 0
        self.visited = {}

        self.last_output = ""
        self.screen_cleared = False

    def find_characters(self):
        for y, row in enumerate(self.original_maze):
            for x, c in enumerate(row):
                if c == "P":
                    self.player = [x, y]
                    print(f"[DEBUG] Player at: ({x}, {y})")
                if c == "S":
                    self.enemy = [x, y]
                    print(f"[DEBUG] Enemy at: ({x}, {y})")
                
                # PERBAIKI: Gunakan finish_mapping
                if c in self.finish_mapping:
                    finish_id = self.finish_mapping[c]
                    self.finish_points[finish_id] = [x, y]
                    print(f"[DEBUG] Finish point '{finish_id}' at: ({x}, {y})")

    def is_wall(self, x, y):
        return self.original_maze[y][x] == "█" 

    def is_finish(self, x, y):
        """Cek apakah posisi adalah finish point"""
        if y < 0 or y >= len(self.original_maze):
            return False
        if x < 0 or x >= len(self.original_maze[y]):
            return False
        cell = self.original_maze[y][x]
        return cell in self.finish_mapping  # PERBAIKI: gunakan mapping

    def get_finish_id(self, x, y):
        """Dapatkan ID finish point"""
        if y < 0 or y >= len(self.original_maze):
            return None
        if x < 0 or x >= len(self.original_maze[y]):
            return None
        cell = self.original_maze[y][x]
        return self.finish_mapping.get(cell, None)  # PERBAIKI: gunakan mapping
    
    def can_see_player(self):
        if not self.enemy:
            return False
        px, py = self.player
        ex, ey = self.enemy

        if px == ex:
            step = 1 if py > ey else -1
            for y in range(ey + step, py, step):
                if self.is_wall(ex, y):
                    return False
            return True

        if py == ey:
            step = 1 if px > ex else -1
            for x in range(ex + step, px, step):
                if self.is_wall(x, ey):
                    return False
            return True

        return False

    def bfs(self, start, goal):
        sx, sy = start
        gx, gy = goal
        queue = deque([(sx, sy)])
        visited = {(sx, sy): None}

        while queue:
            x, y = queue.popleft()
            if (x, y) == (gx, gy):
                path = []
                while (x, y) != (sx, sy):
                    path.append((x, y))
                    x, y = visited[(x, y)]
                path.reverse()
                return path

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
        if not self.enemy:
            return False
        
        path = self.bfs(tuple(self.enemy), tuple(self.player))
        if not path:
            return False
        nx, ny = path[0]
        ex, ey = self.enemy

        # PERBAIKI: Gunakan is_finish() bukan list hardcode
        if not self.is_finish(ex, ey) and [ex, ey] != self.player:
            self.maze[ey][ex] = " "
        
        if not self.is_finish(nx, ny) and [nx, ny] != self.player:
            self.maze[ny][nx] = "S"
        
        self.enemy[:] = [nx, ny]
        return True

    def get_visit(self, x, y):
        return self.visited.get((x, y), 0)

    def add_visit(self, x, y):
        self.visited[(x, y)] = self.get_visit(x, y) + 1

    def decay_visits(self):
        remove_keys = []
        for k in self.visited:
            self.visited[k] -= 0.02   
            if self.visited[k] <= 0:
                remove_keys.append(k)
        for k in remove_keys:
            del self.visited[k]

        
    def move_enemy_roaming(self):
        if not self.enemy:
            return False
        
        ex, ey = self.enemy
        
        dirs = [(1,0), (-1,0), (0,1), (0,-1)]
        candidates = []

        for dx, dy in dirs:
            nx, ny = ex + dx, ey + dy
            if (0 <= ny < len(self.original_maze) and
                0 <= nx < len(self.original_maze[ny]) and
                not self.is_wall(nx, ny)):

                visit_score = self.get_visit(nx, ny)
                candidates.append(((nx, ny), visit_score))

        if not candidates:
            return False

        min_visit = min(v for pos, v in candidates)
        best_moves = [pos for pos, v in candidates if v == min_visit]

        nx, ny = random.choice(best_moves)

        self.add_visit(nx, ny)
        self.decay_visits()

        ex, ey = self.enemy
        # PERBAIKI: Gunakan is_finish() bukan list hardcode
        if not self.is_finish(ex, ey) and [ex, ey] != self.player:
            self.maze[ey][ex] = " " 
        
        if not self.is_finish(nx, ny) and [nx, ny] != self.player:
            self.maze[ny][nx] = "S"
        
        self.enemy[:] = [nx, ny]
        return True


    def build_frame(self):
        lines = []
        lines.append("🧭" * 20)
        lines.append("           MAZE CHALLENGE")
        lines.append("🧭" * 20)
        lines.append("")

        for y, row in enumerate(self.maze):
            line = ""
            for x, c in enumerate(row):
                original_cell = self.original_maze[y][x]
                
                if c == "P": 
                    line += "😎"
                elif c == "S": 
                    if self.state=="ROAMING":
                        line += "👻"
                    else:
                        line +="👿"
                elif c == "█": 
                    line += "🧱"
                elif original_cell in self.finish_mapping:  # PERBAIKI: gunakan mapping
                    line += "🏁"
                else: 
                    line += "  "
            lines.append(line)

        lines.append("")
        lines.append("🎮 Controls: WASD or Arrow Keys")
        lines.append("🎯 Goal: Reach 🏁")
        lines.append(f"⚠️  Available exits: {', '.join(self.finish_points.keys())}")  # TAMBAHKAN INFO
        lines.append(f"👣 Steps: {self.steps}")
        lines.append(f"STATE: {self.state}")
        return "\n".join(lines)

    def render(self):
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
        enemy_delay = 0.35
        last_enemy_time = time.time()
        self.render()

        while True:
            now = time.time()
            moved = False

            # Player movement
            key = get_key()
            if key in ["w","up","s","down","a","left","d","right", "q"]:
                if key == "q":  # Quit key untuk testing
                    return "QUIT", None
                    
                dx = dy = 0
                if key in ["w","up"]: dy = -1
                if key in ["s","down"]: dy = 1
                if key in ["a","left"]: dx = -1
                if key in ["d","right"]: dx = 1

                px, py = self.player
                nx, ny = px + dx, py + dy

                if (0 <= ny < len(self.original_maze) and
                    0 <= nx < len(self.original_maze[ny]) and
                    not self.is_wall(nx, ny)):

                    self.steps += 1

                    if self.is_finish(nx, ny):
                        finish_id = self.get_finish_id(nx, ny)
                        self.maze[py][px] = " "
                        self.maze[ny][nx] = "P"
                        self.player[:] = [nx, ny]
                        self.render()
                        print(f"\n🎉 MAZE COMPLETED via {finish_id}! Steps: {self.steps}")
                        return "WIN", finish_id

                    if [px, py] != self.enemy:
                        self.maze[py][px] = " "
                    self.maze[ny][nx] = "P"
                    self.player[:] = [nx, ny]
                    moved = True

            # Enemy AI
            if self.enemy and now - last_enemy_time > enemy_delay:
                last_enemy_time = now

                if self.can_see_player():
                    self.state = "CHASING"
                    self.last_seen_time = time.time()
                else:
                    if self.state == "CHASING" and time.time() - self.last_seen_time > 5:
                        self.state = "ROAMING"

                if self.state == "CHASING":
                    moved = self.move_enemy_chasing() or moved
                else:
                    moved = self.move_enemy_roaming() or moved

            # Collision
            if self.enemy == self.player:
                self.render()
                print(f"\n💀 CAUGHT BY ENEMY! Steps: {self.steps}")
                return "LOSE", None

            if moved:
                self.render()

            time.sleep(0.016)
            

        
        
class MazeManager:
    
    @staticmethod
    def start_maze(map_data, description="Find your way through the maze!"):
        console.print(f"\n{description}", style="bold yellow")
        console.print("Loading maze...", style="dim")
        time.sleep(1)

        maze_game = MazeGame(map_data)
        
        # Debug: print finish points yang terdeteksi
        print(f"[DEBUG] Finish points found: {maze_game.finish_points}")
        
        result, finish_id = maze_game.start()
        
        # Debug: print return value
        print(f"[DEBUG] Maze result: {result}, finish_id: {finish_id}")
        
        return {
            "result": result,
            "finish_id": finish_id,
            "steps": maze_game.steps
        }
        
        
