import os
import pgzrun
import random
from pygame import Rect

# ----------------- CONFIG -----------------
WIDTH = 800
HEIGHT = 600

game_state = "menu"
music_on = True
score = 0
lives = 3
invincible_time = 0

buttons = {
    "start":     {"rect": Rect(300, 200, 200, 50), "text": "Start"},
    "sound_on":  {"rect": Rect(300, 300, 200, 50), "text": "Sound ON"},
    "sound_off": {"rect": Rect(300, 360, 200, 50), "text": "Sound OFF"},
    "exit":      {"rect": Rect(300, 420, 200, 50), "text": "Exit"},
}

# ----------------- MUSIC / SOUNDS -----------------
def play_music():
    if music_on:
        music.play("bgm")

def stop_music():
    music.stop()

def play_sfx(name):
    if music_on:
        getattr(sounds, name).play()

# ----------------- HERO -----------------
class Hero(Actor):
    def __init__(self, pos):
        super().__init__("hero1", pos)
        self.speed = 5
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_time = 0.1
        self.total_frames = 6

    def update(self, dt):
        moved = False
        if keyboard.left:
            self.x -= self.speed
            moved = True
        if keyboard.right:
            self.x += self.speed
            moved = True
        if keyboard.up:
            self.y -= self.speed
            moved = True
        if keyboard.down:
            self.y += self.speed
            moved = True

        self.x = max(0, min(WIDTH, self.x))
        self.y = max(0, min(HEIGHT, self.y))

        self.anim_timer += dt
        if self.anim_timer >= self.anim_time:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % self.total_frames
            self.image = f"hero{self.anim_frame + 1}"

# ----------------- ENEMIES -----------------
class Enemy(Actor):
    def __init__(self, image, pos, left_limit, right_limit):
        super().__init__(image, pos)
        self.left_limit = left_limit
        self.right_limit = right_limit
        self.direction = random.choice(["left", "right"])

    def update(self):
        if self.direction == "left":
            self.x -= enemy_speed
            if self.x <= self.left_limit:
                self.direction = "right"
        else:
            self.x += enemy_speed
            if self.x >= self.right_limit:
                self.direction = "left"

# ----------------- INIT HERO & ENEMIES -----------------
hero = Hero((400, 500))

enemies = [
    Enemy("bomb1", (200, 200), 150, 300),
    Enemy("bomb1", (500, 200), 450, 650),
    Enemy("bomb1", (700, 300), 650, 750),
    Enemy("bomb1", (400, 100), 350, 500),
]

enemy_speed = 2
enemy_anim_frame = 0
enemy_anim_time = 0.2
enemy_anim_timer = 0

# ----------------- FLIES -----------------
flies = []
fly_speed = 120
spawn_time = 0
spawn_interval = 2

def spawn_fly():
    x = random.randint(50, WIDTH - 50)
    fly = Actor("fly", (x, -30))
    flies.append(fly)

def update_flies(dt):
    global spawn_time, score
    spawn_time += dt
    if spawn_time >= spawn_interval:
        spawn_time = 0
        spawn_fly()

    for fly in flies[:]:
        fly.y += fly_speed * dt
        if fly.y > HEIGHT:
            flies.remove(fly)
        elif hero.colliderect(fly):
            score += 10
            play_sfx("catch")
            flies.remove(fly)

# ----------------- COLLISIONS -----------------
def check_collisions():
    global lives, game_state
    for enemy in enemies:
        if hero.colliderect(enemy):
            lives -= 1
            hero.x, hero.y = 400, 500
            play_sfx("hit")
            if lives <= 0:
                game_state = "gameover"
                stop_music()

# ----------------- DRAW -----------------
def draw_menu():
    screen.fill((50, 50, 100))
    for key, btn in buttons.items():
        screen.draw.filled_rect(btn["rect"], (200, 200, 200))
        screen.draw.text(btn["text"], center=btn["rect"].center, color="black", fontsize=40)

def draw_game():
    screen.fill((0, 150, 200))
    hero.draw()
    for enemy in enemies:
        enemy.draw()
    for fly in flies:
        fly.draw()
    screen.draw.text(f"Score: {score}", (10, 10), color="white", fontsize=30)
    screen.draw.text(f"Lives: {lives}", (10, 50), color="white", fontsize=30)

def draw_gameover():
    screen.fill((100, 0, 0))
    screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2 - 50), fontsize=60, color="white")
    screen.draw.text(f"Final Score: {score}", center=(WIDTH//2, HEIGHT//2 + 20), fontsize=40, color="yellow")
    screen.draw.text("Click to return to menu", center=(WIDTH//2, HEIGHT//2 + 100), fontsize=30, color="white")

def draw():
    screen.clear()
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        draw_game()
    elif game_state == "gameover":
        draw_gameover()

# ----------------- UPDATE -----------------
def update(dt):
    global game_state, invincible_time, enemy_anim_frame, enemy_anim_timer
    if game_state == "playing":
        if invincible_time > 0:
            invincible_time -= dt
        hero.update(dt)
        for enemy in enemies:
            enemy.update()
        update_flies(dt)
        if invincible_time <= 0:
            check_collisions()

        # animate enemies
        enemy_anim_timer += dt
        if enemy_anim_timer >= enemy_anim_time:
            enemy_anim_timer = 0
            enemy_anim_frame = (enemy_anim_frame + 1) % 2
            for enemy in enemies:
                enemy.image = f"bomb{enemy_anim_frame + 1}"

# ----------------- MOUSE -----------------
def on_mouse_down(pos):
    global game_state, music_on, score, lives, invincible_time, flies
    if game_state == "menu":
        if buttons["start"]["rect"].collidepoint(pos):
            game_state = "playing"
            score = 0
            lives = 3
            flies = []
            hero.x, hero.y = 400, 500
            invincible_time = 2
            play_music()
        elif buttons["sound_on"]["rect"].collidepoint(pos):
            music_on = True
            play_music()
        elif buttons["sound_off"]["rect"].collidepoint(pos):
            music_on = False
            stop_music()
        elif buttons["exit"]["rect"].collidepoint(pos):
            exit()
    elif game_state == "gameover":
        game_state = "menu"

pgzrun.go()
