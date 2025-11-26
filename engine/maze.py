import os
import sys
import time
from collections import deque

if os.name == "nt":
    import msvcrt
from engine.utils import console

def get_key():
    """Get keyboard input for movement"""
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
        self.player = None
        self.enemy = None
        self.find_characters()
        self.steps = 0
        
        # Untuk smooth rendering
        self.last_output = ""
        self.screen_cleared = False

    def find_characters(self):
        """Find P and S in maze"""
        for y, row in enumerate(self.maze):
            for x, c in enumerate(row):
                if c == "P": 
                    self.player = [x, y]
                if c == "S": 
                    self.enemy = [x, y]

    def is_wall(self, x, y):
        return self.maze[y][x] == "█"

    def bfs(self, start, goal):
        """Enemy pathfinding"""
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

                if ny < 0 or ny >= len(self.maze): continue
                if nx < 0 or nx >= len(self.maze[ny]): continue
                if (nx, ny) in visited: continue
                if self.is_wall(nx, ny): continue

                visited[(nx, ny)] = (x, y)
                queue.append((nx, ny))
        return None

    def move_enemy(self):
        if not self.enemy:
            return False

        path = self.bfs(tuple(self.enemy), tuple(self.player))
        if not path:
            return False

        nx, ny = path[0]
        ex, ey = self.enemy

        if (nx, ny) != (ex, ey):
            # Clear old enemy position
            if [ex, ey] != self.player:
                self.maze[ey][ex] = " "
            
            # Set new enemy position
            if [nx, ny] != self.player:
                self.maze[ny][nx] = "S"
            
            self.enemy[:] = [nx, ny]
            return True
        return False

    def build_frame(self):
        """Build complete frame as string (FAST)"""
        lines = []
        
        # Header
        lines.append("🧭" * 20)
        lines.append("           MAZE CHALLENGE")
        lines.append("🧭" * 20)
        lines.append("")
        
        # Maze
        for row in self.maze:
            line = ""
            for c in row:
                if c == "P": line += "😎"
                elif c == "S": line += "👻" 
                elif c == "█": line += "🧱"
                elif c == "F": line += "🏁"
                elif c == " ": line += "  "
                else: line += "  "
            lines.append(line)
        
        # Footer
        lines.append("")
        lines.append("🎮 Controls: WASD or Arrow Keys")
        lines.append("🎯 Goal: Reach 🏁")
        lines.append("⚠️  Enemy: 👻")
        lines.append(f"👣 Steps: {self.steps}")
        
        return "\n".join(lines)

    def render(self):
        """Smart rendering dengan perbandingan frame"""
        new_output = self.build_frame()
        
        # Hanya render jika ada perubahan
        if new_output != self.last_output:
            # Clear screen hanya di render pertama
            if not self.screen_cleared:
                os.system('cls' if os.name == 'nt' else 'clear')
                self.screen_cleared = True
            else:
                # Move cursor ke atas untuk overwrite
                print(f"\033[{new_output.count(chr(10)) + 1}A", end="")
            
            print(new_output)
            self.last_output = new_output

    def start(self):
        enemy_delay = 0.35
        last_enemy_time = time.time()

        # Render pertama
        self.render()

        while True:
            now = time.time()
            moved = False

            # Player movement
            key = get_key()
            if key in ["w","up","s","down","a","left","d","right"]:
                dx = dy = 0
                if key in ["w","up"]: dy = -1
                if key in ["s","down"]: dy = 1
                if key in ["a","left"]: dx = -1
                if key in ["d","right"]: dx = 1

                px, py = self.player
                nx, ny = px + dx, py + dy

                if (0 <= ny < len(self.maze) and 
                    0 <= nx < len(self.maze[ny]) and 
                    not self.is_wall(nx, ny)):
                    
                    self.steps += 1

                    # Check for finish
                    if self.maze[ny][nx] == "F":
                        self.maze[py][px] = " "
                        self.maze[ny][nx] = "P"  
                        self.player[:] = [nx, ny]
                        self.render()
                        print(f"\n🎉 MAZE COMPLETED! Steps: {self.steps}")
                        return "WIN"

                    # Normal move
                    if [px, py] != self.enemy:
                        self.maze[py][px] = " "
                    
                    self.maze[ny][nx] = "P"
                    self.player[:] = [nx, ny]
                    moved = True

            # Enemy movement
            if now - last_enemy_time > enemy_delay:
                last_enemy_time = now
                if self.move_enemy():
                    moved = True

            # Check collision
            if self.enemy and self.enemy == self.player:
                self.render()
                print(f"\n💀 CAUGHT BY ENEMY! Steps: {self.steps}")
                return "LOSE"

            # Re-render hanya jika ada perubahan
            if moved:
                self.render()

            time.sleep(0.016)  # ~60 FPS


class MazeManager:  
    @staticmethod
    def start_maze(map_data, description="Find your way through the maze!"):
        """Start a maze game with given map data"""
        console.print(f"\n{description}", style="bold yellow")
        console.print("Loading maze...", style="dim")
        time.sleep(1)
        
        maze_game = MazeGame(map_data)
        result = maze_game.start()
        
        return result