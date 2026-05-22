import random
import sys
import tkinter as tk

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 25
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT
INITIAL_TICK_MS = 200
SPEED_STEP_MS = 10
MIN_TICK_MS = 50

BG = "#0a0a0a"
GRID_COLOR = "#282828"
SNAKE_HEAD = "#22c55e"
SNAKE_BODY = "#16a34a"
FOOD_COLOR = "#ef4444"
TEXT_COLOR = "#ffffff"
MUTED = "#9ca3af"


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        cx, cy = GRID_WIDTH // 2, GRID_HEIGHT // 2
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.grow_pending = 0

    def head(self):
        return self.body[0]

    def set_direction(self, new_dir):
        opposite = (-self.direction[0], -self.direction[1])
        if new_dir != opposite:
            self.direction = new_dir

    def move(self):
        hx, hy = self.head()
        dx, dy = self.direction
        self.body.insert(0, (hx + dx, hy + dy))
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self):
        self.grow_pending += 1

    def collided(self):
        x, y = self.head()
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return True
        return self.head() in self.body[1:]

class SnakeGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Snake Game")
        self.root.resizable(False, False)
        self.root.bind("<KeyPress>", self.on_key)

        self.canvas = tk.Canvas(
            self.root,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            bg=BG,
            highlightthickness=0,
        )
        self.canvas.pack()

        self.status = tk.Label(
            self.root,
            text="Score: 0  |  High: 0  |  Arrow keys or WASD  |  P pause  |  Esc quit",
            fg=TEXT_COLOR,
            bg=BG,
            font=("Segoe UI", 10),
            pady=6,
        )
        self.status.pack(fill="x")

        self.snake = Snake()
        self.food = self.spawn_food()
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.paused = False
        self.tick_id = None
        self.tick_ms = INITIAL_TICK_MS
        self.foods_eaten = 0

        self.draw()
        self.schedule_tick()

    def spawn_food(self):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in self.snake.body:
                return pos

    def on_key(self, event):
        key = event.keysym.lower()
        if key == "escape":
            self.root.destroy()
            return
        if self.game_over:
            if key in ("space", "return"):
                self.restart()
            return
        if key == "p":
            self.paused = not self.paused
            self.update_status()
            return
        if self.paused:
            return
        moves = {
            "up": (0, -1),
            "w": (0, -1),
            "down": (0, 1),
            "s": (0, 1),
            "left": (-1, 0),
            "a": (-1, 0),
            "right": (1, 0),
            "d": (1, 0),
        }
        if key in moves:
            self.snake.set_direction(moves[key])

    def restart(self):
        if self.tick_id is not None:
            self.root.after_cancel(self.tick_id)
            self.tick_id = None
        self.snake.reset()
        self.food = self.spawn_food()
        self.score = 0
        self.foods_eaten = 0
        self.tick_ms = INITIAL_TICK_MS
        self.game_over = False
        self.paused = False
        self.update_status()
        self.draw()
        self.schedule_tick()

    def speed_up(self):
        self.foods_eaten += 1
        self.tick_ms = max(MIN_TICK_MS, self.tick_ms - SPEED_STEP_MS)

    def update_status(self):
        state = ""
        if self.game_over:
            state = " — GAME OVER (Space to restart)"
        elif self.paused:
            state = " — PAUSED"
        self.status.config(
            text=(
                f"Score: {self.score}  |  High: {self.high_score}  |  "
                f"Speed: {self.tick_ms}ms{state}  |  Arrow keys or WASD  |  P pause  |  Esc quit"
            )
        )

    def tick(self):
        if not self.game_over and not self.paused:
            self.snake.move()
            if self.snake.head() == self.food:
                self.snake.grow()
                self.score += 10
                self.speed_up()
                self.food = self.spawn_food()
            if self.snake.collided():
                self.game_over = True
                self.high_score = max(self.high_score, self.score)
            self.draw()
            self.update_status()
        self.schedule_tick()

    def schedule_tick(self):
        self.tick_id = self.root.after(self.tick_ms, self.tick)

    def cell_rect(self, gx, gy, pad=1):
        x1 = gx * CELL_SIZE + pad
        y1 = gy * CELL_SIZE + pad
        x2 = (gx + 1) * CELL_SIZE - pad
        y2 = (gy + 1) * CELL_SIZE - pad
        return x1, y1, x2, y2

    def draw(self):
        self.canvas.delete("all")
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            self.canvas.create_line(x, 0, x, SCREEN_HEIGHT, fill=GRID_COLOR)
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            self.canvas.create_line(0, y, SCREEN_WIDTH, y, fill=GRID_COLOR)

        fx, fy = self.food
        self.canvas.create_oval(
            *self.cell_rect(fx, fy, 2),
            fill=FOOD_COLOR,
            outline=FOOD_COLOR,
        )

        for i, (gx, gy) in enumerate(self.snake.body):
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            self.canvas.create_rectangle(
                *self.cell_rect(gx, gy, 2),
                fill=color,
                outline=color,
            )

        if self.game_over:
            self.canvas.create_rectangle(
                0,
                0,
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
                fill="#000000",
                stipple="gray50",
            )
            cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
            self.canvas.create_text(
                cx,
                cy - 40,
                text="GAME OVER",
                fill=TEXT_COLOR,
                font=("Segoe UI", 28, "bold"),
            )
            self.canvas.create_text(
                cx,
                cy,
                text=f"Score: {self.score}",
                fill=SNAKE_HEAD,
                font=("Segoe UI", 20),
            )
            self.canvas.create_text(
                cx,
                cy + 50,
                text="Press SPACE to restart",
                fill=MUTED,
                font=("Segoe UI", 12),
            )

    def run(self):
        self.root.mainloop()


def main():
    print("Snake Game")
    print("Controls: Arrow keys or WASD | P pause | Esc quit | Space restart after game over")
    SnakeGame().run()


if __name__ == "__main__":
    main()
    sys.exit(0)
