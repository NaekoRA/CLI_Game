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
        self.player = None
        self.enemy = None
        self.find_characters()
        self.steps = 0

        self.state = "ROAMING"
        self.last_seen_time = 0
        self.visited = {}

        self.last_output = ""
        self.screen_cleared = False

    def find_characters(self):
        for y, row in enumerate(self.maze):
            for x, c in enumerate(row):
                if c == "P":
                    self.player = [x, y]
                if c == "S":
                    self.enemy = [x, y]

    def is_wall(self, x, y):
        return self.maze[y][x] == "█"

    def can_see_player(self):
        if not self.enemy:
            return False
        px, py = self.player
        ex, ey = self.enemy

        if px == ex:
            step = 1 if py > ey else -1
            for y in range(ey + step, py, step):
                if self.maze[y][ex] == "█":
                    return False
            return True

        if py == ey:
            step = 1 if px > ex else -1
            for x in range(ex + step, px, step):
                if self.maze[py][x] == "█":
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

                if ny < 0 or ny >= len(self.maze): continue
                if nx < 0 or nx >= len(self.maze[ny]): continue
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

        if self.maze[ey][ex] not in ["F", "P"]:
            self.maze[ey][ex] = " "
        if self.maze[ny][nx] != "F" and [nx, ny] != self.player:
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
            if (0 <= ny < len(self.maze) and
                0 <= nx < len(self.maze[ny]) and
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
        if self.maze[ey][ex] not in ["F", "P"]:
            self.maze[ey][ex] = " " 
        if self.maze[ny][nx] != "F" and [nx, ny] != self.player:
            self.maze[ny][nx] = "S"
        self.enemy[:] = [nx, ny]

        return True


    def build_frame(self):
        lines = []
        lines.append("🧭" * 20)
        lines.append("           MAZE CHALLENGE")
        lines.append("🧭" * 20)
        lines.append("")

        for row in self.maze:
            line = ""
            for c in row:
                if c == "P": line += "😎"
                elif c == "S": line += "👻"
                elif c == "█": line += "🧱"
                elif c == "F": line += "🏁"
                else: line += "  "
            lines.append(line)

        lines.append("")
        lines.append("🎮 Controls: WASD or Arrow Keys")
        lines.append("🎯 Goal: Reach 🏁")
        lines.append("⚠️ Enemy: 👻")
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

                    if self.maze[ny][nx] == "F":
                        self.maze[py][px] = " "
                        self.maze[ny][nx] = "P"
                        self.player[:] = [nx, ny]
                        self.render()
                        print(f"\n🎉 MAZE COMPLETED! Steps: {self.steps}")
                        return "WIN"

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
                    moved = self.move_enemy_chasing()
                else:
                    moved = self.move_enemy_roaming()

            # Collision
            if self.enemy == self.player:
                self.render()
                print(f"\n💀 CAUGHT BY ENEMY! Steps: {self.steps}")
                return "LOSE"

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
        result = maze_game.start()

        return result
