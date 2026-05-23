from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color
import random

CELL = 24


class SnakeGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ui = None
        self.state = "menu"  # menu / play / gameover
        self.start_pos = None

        self.reset()
        Clock.schedule_interval(self.update, 1 / 12)

    def set_ui(self, ui):
        self.ui = ui

    # ---------------- RESET ----------------
    def reset(self):
        W, H = Window.size

        x = (W // 2) // CELL * CELL
        y = (H // 2) // CELL * CELL

        self.snake = [(x, y), (x - CELL, y), (x - 2 * CELL, y)]
        self.dx, self.dy = CELL, 0

        self.food = self.spawn_food()
        self.score = 0

        self.state = "menu"

    def spawn_food(self):
        W, H = Window.size
        return (
            random.randrange(0, W // CELL) * CELL,
            random.randrange(0, H // CELL) * CELL
        )

    # ---------------- TOUCH ----------------
    def on_touch_down(self, touch):
        # 🔥 ВАЖНО: и меню и gameover = РЕСТАРТ
        if self.state in ("menu", "gameover"):
            self.reset()
            self.start_game()
            return

        self.start_pos = touch.pos

    def on_touch_up(self, touch):
        if self.state != "play":
            return

        if not self.start_pos:
            return

        sx, sy = self.start_pos
        ex, ey = touch.pos

        dx = ex - sx
        dy = ey - sy

        if abs(dx) > abs(dy):
            if dx > 0 and self.dx != -CELL:
                self.dx, self.dy = CELL, 0
            elif dx < 0 and self.dx != CELL:
                self.dx, self.dy = -CELL, 0
        else:
            if dy > 0 and self.dy != -CELL:
                self.dx, self.dy = 0, CELL
            elif dy < 0 and self.dy != CELL:
                self.dx, self.dy = 0, -CELL

        self.start_pos = None

    # ---------------- START ----------------
    def start_game(self):
        self.state = "play"
        if self.ui:
            self.ui.hide_overlay()
            self.ui.set_score(0)

    # ---------------- LOOP ----------------
    def update(self, dt):
        if self.state != "play":
            self.draw()
            return

        hx, hy = self.snake[0]
        new = (hx + self.dx, hy + self.dy)

        W, H = Window.size

        if new in self.snake or new[0] < 0 or new[1] < 0 or new[0] >= W or new[1] >= H:
            self.state = "gameover"
            if self.ui:
                self.ui.show_overlay("GAME OVER\nTAP TO RESTART")
            return

        self.snake.insert(0, new)

        if new == self.food:
            self.score += 1
            self.food = self.spawn_food()
            if self.ui:
                self.ui.set_score(self.score)
        else:
            self.snake.pop()

        self.draw()

    # ---------------- DRAW ----------------
    def draw(self):
        self.canvas.clear()

        with self.canvas:
            Color(0, 0.08, 0)
            Rectangle(pos=(0, 0), size=Window.size)

            Color(0, 0.9, 0)
            Rectangle(pos=self.food, size=(CELL, CELL))

            Color(0, 0.5, 0)
            for s in self.snake:
                Rectangle(pos=s, size=(CELL, CELL))


# ---------------- UI ----------------
class UI(Widget):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)

        self.game = game
        self.game.set_ui(self)

        self.score_label = Label(
            text="Score: 0",
            pos=(20, Window.height - 60),
            size_hint=(None, None),
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.score_label)

        with self.canvas:
            self.dark_color = Color(0, 0, 0, 0.6)
            self.dark_rect = Rectangle(pos=(0, 0), size=Window.size)

        self.text = Label(
            text="TAP TO START\nMade by ha3py",
            font_size=40,
            center=(Window.width / 2, Window.height / 2),
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.text)

    def set_score(self, s):
        self.score_label.text = f"Score: {s}"

    def show_overlay(self, txt):
        self.dark_color.a = 0.75
        self.text.text = txt
        self.text.opacity = 1

    def hide_overlay(self):
        self.dark_color.a = 0
        self.text.opacity = 0

    def update(self):
        self.dark_rect.size = Window.size


# ---------------- APP ----------------
class SnakeApp(App):
    def build(self):
        root = Widget()

        self.game = SnakeGame()
        self.ui = UI(self.game)

        root.add_widget(self.game)
        root.add_widget(self.ui)

        Clock.schedule_interval(lambda dt: self.ui.update(), 1 / 30)

        return root


SnakeApp().run()