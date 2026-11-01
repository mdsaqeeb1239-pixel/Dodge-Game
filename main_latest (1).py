import pygame
import random
import sys
import os
import json
import math
import array
import copy

pygame.init()

try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1)
except pygame.error:
    pass

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge Game - Robot Edition")
clock = pygame.time.Clock()

# ---------- COLORS ----------
WHITE = (245, 245, 255)
BLACK = (10, 10, 22)
BLUE = (40, 150, 255)
GREEN = (0, 255, 130)
PURPLE = (180, 70, 255)
GOLD = (255, 195, 20)
PINK = (255, 50, 180)
RED = (255, 65, 75)
ORANGE = (255, 140, 30)
CYAN = (0, 240, 255)
DARK = (12, 20, 40)
METAL = (105, 130, 155)

FONT = pygame.font.Font(None, 28)
BIG = pygame.font.Font(None, 46)
HUGE = pygame.font.Font(None, 120)
SMALL = pygame.font.Font(None, 21)

# ---------- SAVE DATA ----------
SAVE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "dodge_save.json"
)

DEFAULT_SAVE = {
    "coins": 0,
    "best": 0,
    "skins": ["Classic Blue"],
    "backgrounds": ["Classic Neon Blue"],
    "selected_skin": "Classic Blue",
    "selected_background": "Classic Neon Blue"
}


def load_save():
    try:
        with open(SAVE_FILE, "r") as file:
            saved = json.load(file)

        if not isinstance(saved, dict):
            raise ValueError("bad save")

        for key, value in DEFAULT_SAVE.items():
            if key not in saved:
                saved[key] = copy.deepcopy(value)

        if not isinstance(saved["coins"], int):
            saved["coins"] = 0
        if not isinstance(saved["best"], int):
            saved["best"] = 0
        if not isinstance(saved["skins"], list):
            saved["skins"] = ["Classic Blue"]
        if not isinstance(saved["backgrounds"], list):
            saved["backgrounds"] = ["Classic Neon Blue"]

        if "Classic Blue" not in saved["skins"]:
            saved["skins"].append("Classic Blue")
        if "Classic Neon Blue" not in saved["backgrounds"]:
            saved["backgrounds"].append("Classic Neon Blue")

        if saved["selected_skin"] not in saved["skins"]:
            saved["selected_skin"] = "Classic Blue"
        if saved["selected_background"] not in saved["backgrounds"]:
            saved["selected_background"] = "Classic Neon Blue"

        return saved

    except (OSError, ValueError, TypeError):
        # deepcopy: shallow copy() would share the lists with DEFAULT_SAVE
        return copy.deepcopy(DEFAULT_SAVE)


data = load_save()


def save_game():
    try:
        with open(SAVE_FILE, "w") as file:
            json.dump(data, file)
    except OSError:
        pass


# ---------- SKINS ----------
SKINS = [
    ("Classic Blue", 0, BLUE),
    ("Toxic Green", 100, GREEN),
    ("Shadow Purple", 250, PURPLE),
    ("Legendary Gold", 500, GOLD),
    ("Neon Pink", 1000, PINK)
]

# ---------- BACKGROUNDS ----------
BACKGROUNDS = [
    ("Classic Neon Blue", 0),
    ("Shadow Galaxy", 200),
    ("Inferno", 500),
    ("Toxic Matrix", 1000),
    ("Cosmic Void", 2000)
]

BACKGROUND_STYLE = {
    "Classic Neon Blue": ((7, 12, 35), (20, 65, 145)),
    "Shadow Galaxy": ((19, 5, 38), (100, 45, 160)),
    "Inferno": ((43, 8, 12), (210, 60, 15)),
    "Toxic Matrix": ((2, 22, 13), (0, 170, 65)),
    "Cosmic Void": ((3, 2, 18), (80, 40, 180)),
}

# ---------- BUTTON RECTS (one place, used for drawing AND clicking) ----------
PLAY_BTN = pygame.Rect(75, 185, 250, 55)
SKINS_BTN = pygame.Rect(75, 255, 250, 48)
BG_BTN = pygame.Rect(75, 318, 250, 48)
SOUND_BTN = pygame.Rect(35, 395, 155, 43)
MUSIC_BTN = pygame.Rect(210, 395, 155, 43)

PAUSE_BTN = pygame.Rect(WIDTH - 48, 55, 38, 32)
RESUME_BTN = pygame.Rect(65, 250, 270, 50)
PAUSE_RESTART_BTN = pygame.Rect(65, 315, 270, 50)
PAUSE_MENU_BTN = pygame.Rect(65, 380, 270, 50)

OVER_RESTART_BTN = pygame.Rect(65, 380, 270, 52)
OVER_MENU_BTN = pygame.Rect(65, 448, 270, 52)

SHOP_BACK_BTN = pygame.Rect(125, HEIGHT - 52, 150, 38)

# ---------- SOUND ----------
sound_on = True
music_on = True
sounds_available = pygame.mixer.get_init() is not None
sounds = {}

music_channel = None
retro_music = None


def make_tone(frequency, duration, volume=0.18):
    if not sounds_available:
        return None

    sample_rate = 22050
    samples = array.array("h")
    count = int(sample_rate * duration)

    for i in range(count):
        fade = min(1.0, i / 250, (count - i) / 500)
        value = int(
            32767 * volume * fade *
            math.sin(2 * math.pi * frequency * i / sample_rate)
        )
        samples.append(value)

    try:
        return pygame.mixer.Sound(buffer=samples.tobytes())
    except pygame.error:
        return None


def make_retro_music():
    """Generate a short retro arcade melody in memory."""
    if not sounds_available:
        return None

    sample_rate = 22050
    beat = 0.18

    melody = [
        659, 784, 988, 784, 659, 523, 587, 659,
        784, 988, 1175, 988, 784, 659, 587, 523,
        659, 784, 988, 1318, 1175, 988, 784, 659,
        587, 659, 784, 587, 523, 587, 659, 523
    ]

    bass = [
        131, 131, 165, 165, 175, 175, 147, 147,
        131, 131, 165, 165, 196, 196, 165, 165,
        131, 131, 175, 175, 196, 196, 165, 165,
        147, 147, 165, 165, 131, 131, 131, 131
    ]

    samples = array.array("h")
    note_samples = int(sample_rate * beat)

    for index, frequency in enumerate(melody):
        bass_frequency = bass[index]

        for i in range(note_samples):
            t = i / sample_rate

            fade_in = min(1.0, i / 100)
            fade_out = min(1.0, (note_samples - i) / 250)
            envelope = min(fade_in, fade_out)

            lead = 0
            if frequency > 0:
                lead = 1 if math.sin(
                    2 * math.pi * frequency * t
                ) >= 0 else -1

            bass_wave = math.sin(2 * math.pi * bass_frequency * t)

            value = int(envelope * (lead * 4400 + bass_wave * 1800))
            samples.append(max(-32767, min(32767, value)))

    try:
        return pygame.mixer.Sound(buffer=samples.tobytes())
    except pygame.error:
        return None


if sounds_available:
    pygame.mixer.set_num_channels(8)
    music_channel = pygame.mixer.Channel(0)

    sounds["coin"] = make_tone(950, 0.09)
    sounds["power"] = make_tone(600, 0.16)
    sounds["hit"] = make_tone(150, 0.25)
    sounds["click"] = make_tone(450, 0.06)
    sounds["over"] = make_tone(110, 0.55)
    sounds["beep"] = make_tone(520, 0.08)
    sounds["go"] = make_tone(880, 0.18)

    retro_music = make_retro_music()


def play_sound(name):
    if sound_on and sounds_available:
        effect = sounds.get(name)
        if effect:
            effect.play()


def start_music():
    if (
        music_on
        and sounds_available
        and music_channel is not None
        and retro_music is not None
        and not music_channel.get_busy()
    ):
        music_channel.play(retro_music, loops=-1)


def stop_music():
    if music_channel is not None:
        music_channel.stop()


# ---------- HELPERS ----------
def draw_text(text, x, y, color=WHITE, font=FONT, align="center"):
    """align: 'center' (x,y is the middle), 'left' or 'right' (x is the edge)."""
    image = font.render(str(text), True, color)

    if align == "center":
        rect = image.get_rect(center=(x, y))
    elif align == "right":
        rect = image.get_rect(topright=(x, y))
    else:
        rect = image.get_rect(topleft=(x, y))

    screen.blit(image, rect)


def draw_button(text, rect, color=BLUE):
    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=12)
    draw_text(text, rect.centerx, rect.centery, WHITE, FONT)


def draw_heart(x, y, color):
    r = 4
    pygame.draw.circle(screen, color, (x - r, y), r)
    pygame.draw.circle(screen, color, (x + r, y), r)
    pygame.draw.polygon(
        screen, color,
        [(x - 2 * r, y + 1), (x + 2 * r, y + 1), (x, y + 3 * r)]
    )


# ---------- BACKGROUND ----------
# [x, y, radius] - stars drift downward so the world feels alive
stars = [
    [
        random.randrange(WIDTH),
        random.randrange(HEIGHT),
        random.choice([1, 2, 3])
    ]
    for _ in range(65)
]


def draw_background():
    base, color = BACKGROUND_STYLE.get(
        data["selected_background"],
        BACKGROUND_STYLE["Classic Neon Blue"]
    )

    screen.fill(base)

    for star in stars:
        star[1] += star[2] * 0.35

        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randrange(WIDTH)

        pygame.draw.circle(
            screen, color, (int(star[0]), int(star[1])), star[2]
        )

    scroll = (pygame.time.get_ticks() // 25) % 60

    for y in range(-60 + scroll, HEIGHT, 60):
        pygame.draw.line(screen, color, (0, y), (WIDTH, y), 1)


# ---------- GAME VARIABLES ----------
PLAYER_SIZE = 34

player = pygame.Rect(
    WIDTH // 2 - PLAYER_SIZE // 2,
    HEIGHT - 100,
    PLAYER_SIZE,
    PLAYER_SIZE
)

BUTTON_SIZE = 64

MOVE_BUTTONS = [
    ("left", pygame.Rect(18, HEIGHT - 82, BUTTON_SIZE, 58)),
    (
        "right",
        pygame.Rect(WIDTH - BUTTON_SIZE - 18, HEIGHT - 82,
                    BUTTON_SIZE, 58)
    )
]

active_direction = None


def direction_at(pos):
    for direction, rect in MOVE_BUTTONS:
        if rect.collidepoint(pos):
            return direction
    return None


def release_direction():
    global active_direction
    active_direction = None


def draw_direction_buttons():
    labels = {"left": "<", "right": ">"}

    for direction, rect in MOVE_BUTTONS:
        color = (
            (45, 125, 190)
            if active_direction == direction
            else (35, 55, 90)
        )

        pygame.draw.rect(screen, color, rect, border_radius=12)
        pygame.draw.rect(
            screen, (210, 235, 255), rect, 2, border_radius=12
        )
        draw_text(labels[direction], rect.centerx, rect.centery, WHITE, BIG)


# obstacle = {"rect": Rect, "y": float, "mult": float}
obstacles = []
coins_on_screen = []
powerups = []
particles = []

score = 0
lives = 3
game_speed = 4
spawn_timer = 0
coin_timer = 0
power_timer = 0
invincible = 0
shield = 0
coin_magnet = 0
flash = 0
shake = 0
run_coins = 0
run_start_best = 0
countdown_timer = 0

SHIELD_TIME = 400
MAGNET_TIME = 400

state = "menu"


def reset_game():
    global score, lives, game_speed, spawn_timer
    global coin_timer, power_timer, invincible, shield
    global coin_magnet, flash, shake, run_coins, run_start_best

    release_direction()

    player.x = WIDTH // 2 - PLAYER_SIZE // 2
    player.y = HEIGHT - 100

    obstacles.clear()
    coins_on_screen.clear()
    powerups.clear()
    particles.clear()

    score = 0
    lives = 3
    game_speed = 4
    spawn_timer = 0
    coin_timer = 0
    power_timer = 0
    invincible = 0
    shield = 0
    coin_magnet = 0
    flash = 0
    shake = 0
    run_coins = 0
    run_start_best = data["best"]


def start_run():
    """Fresh game with a 3-2-1 countdown."""
    global state, countdown_timer
    reset_game()
    countdown_timer = 90
    state = "countdown"
    play_sound("click")


def pause_game():
    global state
    release_direction()
    save_game()
    state = "paused"


def resume_game():
    global state, countdown_timer
    countdown_timer = 90
    state = "countdown"


def go_to_menu():
    global state
    release_direction()
    save_game()
    state = "menu"
    play_sound("click")


def end_run():
    global state
    data["best"] = max(data["best"], score)
    save_game()
    release_direction()
    state = "gameover"
    play_sound("over")


def add_particles(x, y, color, amount=12):
    for _ in range(amount):
        particles.append({
            "x": x,
            "y": y,
            "vx": random.uniform(-3, 3),
            "vy": random.uniform(-4, 2),
            "life": random.randint(15, 30),
            "color": color
        })


# ---------- FUTURISTIC ROBOT PLAYER ----------
def draw_player():
    skin_color = next(
        (
            item[2] for item in SKINS
            if item[0] == data["selected_skin"]
        ),
        BLUE
    )

    x, y = player.x, player.y
    cx, cy = player.center

    glow = 24 + int(math.sin(pygame.time.get_ticks() / 130) * 3)
    pygame.draw.circle(screen, skin_color, (cx, cy), glow, 2)

    # Antenna
    pygame.draw.line(screen, CYAN, (cx, y + 2), (cx, y - 7), 3)
    pygame.draw.circle(screen, CYAN, (cx, y - 9), 3)

    # Arms
    left_arm = pygame.Rect(x - 5, y + 12, 7, 15)
    right_arm = pygame.Rect(x + PLAYER_SIZE - 2, y + 12, 7, 15)
    pygame.draw.rect(screen, METAL, left_arm, border_radius=3)
    pygame.draw.rect(screen, METAL, right_arm, border_radius=3)

    # Head
    head = pygame.Rect(x + 4, y + 2, PLAYER_SIZE - 8, 17)
    pygame.draw.rect(screen, METAL, head, border_radius=5)
    pygame.draw.rect(screen, skin_color, head, 2, border_radius=5)

    # Eyes
    pygame.draw.circle(screen, CYAN, (cx - 6, y + 10), 3)
    pygame.draw.circle(screen, CYAN, (cx + 6, y + 10), 3)

    # Body
    body = pygame.Rect(x + 6, y + 20, PLAYER_SIZE - 12, 12)
    pygame.draw.rect(screen, skin_color, body, border_radius=3)
    pygame.draw.rect(screen, WHITE, body, 1, border_radius=3)

    # Chest light
    pygame.draw.circle(screen, WHITE, (cx, y + 26), 3)

    # Feet
    pygame.draw.line(screen, METAL, (x + 10, y + 32), (x + 8, y + 35), 3)
    pygame.draw.line(screen, METAL, (x + 24, y + 32), (x + 26, y + 35), 3)

    # Shield effect (blinks when about to run out)
    if shield > 0 and (shield > 90 or shield // 8 % 2 == 0):
        pygame.draw.circle(screen, CYAN, player.center, 29, 2)


# ---------- SHOP ----------
shop_scroll = 0
shop_message = ""
shop_message_timer = 0

SHOP_TOP = 95
SHOP_BOTTOM = HEIGHT - 62


def shop_item_rect(index):
    return pygame.Rect(20, 125 + index * 77 - shop_scroll, 360, 62)


def shop_visible(rect):
    return rect.top >= SHOP_TOP and rect.bottom <= SHOP_BOTTOM


def shop_max_scroll(background_shop):
    items = BACKGROUNDS if background_shop else SKINS
    content_bottom = 125 + len(items) * 77 - 15
    return max(0, content_bottom - SHOP_BOTTOM)


def draw_shop(background_shop=False):
    draw_background()

    title = "BACKGROUND SHOP" if background_shop else "SKIN SHOP"

    draw_text(title, WIDTH // 2, 43, CYAN, BIG)
    draw_text("Coins: " + str(data["coins"]), WIDTH // 2, 82, GOLD)

    items = BACKGROUNDS if background_shop else SKINS

    selected = (
        data["selected_background"]
        if background_shop else data["selected_skin"]
    )

    unlocked = data["backgrounds"] if background_shop else data["skins"]

    for index, item in enumerate(items):
        name, price = item[0], item[1]
        rect = shop_item_rect(index)

        if not shop_visible(rect):
            continue

        if background_shop:
            preview_color = BACKGROUND_STYLE[name][1]
        else:
            preview_color = item[2]

        pygame.draw.rect(screen, (23, 25, 48), rect, border_radius=10)
        pygame.draw.rect(screen, preview_color, rect, 2, border_radius=10)
        pygame.draw.circle(
            screen, preview_color, (44, rect.y + 31), 11
        )

        draw_text(name, 65, rect.y + 14, WHITE, SMALL, "left")

        if name in unlocked:
            draw_text("Owned", 65, rect.y + 37, GREEN, SMALL, "left")
        else:
            draw_text(
                str(price) + " coins", 65, rect.y + 37,
                GOLD, SMALL, "left"
            )

        if name == selected:
            status = "SELECTED"
        elif name in unlocked:
            status = "SELECT"
        else:
            status = "BUY"

        draw_text(status, 320, rect.y + 31, CYAN, SMALL)

    draw_button("BACK", SHOP_BACK_BTN, (45, 55, 90))

    if shop_message_timer > 0:
        draw_text(shop_message, WIDTH // 2, HEIGHT - 76, GOLD, SMALL)


def handle_shop_click(pos, background_shop=False):
    global shop_message, shop_message_timer

    if SHOP_BACK_BTN.collidepoint(pos):
        return "menu"

    items = BACKGROUNDS if background_shop else SKINS
    selected_key = (
        "selected_background" if background_shop else "selected_skin"
    )
    unlocked_key = "backgrounds" if background_shop else "skins"

    for index, item in enumerate(items):
        rect = shop_item_rect(index)

        if not shop_visible(rect) or not rect.collidepoint(pos):
            continue

        name, price = item[0], item[1]

        if name in data[unlocked_key]:
            data[selected_key] = name
            save_game()

            shop_message = "Selected: " + name
            shop_message_timer = 90
            play_sound("click")
            return None

        if data["coins"] >= price:
            data["coins"] -= price
            data[unlocked_key].append(name)
            data[selected_key] = name
            save_game()

            shop_message = "Unlocked: " + name
            shop_message_timer = 90
            play_sound("coin")

        else:
            shop_message = (
                "Need " + str(price - data["coins"]) + " more coins!"
            )
            shop_message_timer = 90
            play_sound("hit")

        return None

    return None


# ---------- MAIN MENU ----------
def draw_menu():
    draw_background()

    draw_text("DODGE GAME", WIDTH // 2, 90, CYAN, BIG)
    draw_text("Best Score: " + str(data["best"]), WIDTH // 2, 130, GOLD)
    draw_text("Coins: " + str(data["coins"]), WIDTH // 2, 155, GOLD, SMALL)

    draw_button("PLAY", PLAY_BTN, BLUE)
    draw_button("SKINS", SKINS_BTN, PURPLE)
    draw_button("BACKGROUNDS", BG_BTN, GREEN)

    draw_button(
        "Sound: " + ("ON" if sound_on else "OFF"),
        SOUND_BTN, (40, 75, 100)
    )
    draw_button(
        "Music: " + ("ON" if music_on else "OFF"),
        MUSIC_BTN, (40, 75, 100)
    )

    draw_text("Move: Arrows / A-D / on-screen buttons",
              WIDTH // 2, 470, WHITE, SMALL)
    draw_text("Pause: ESC or P", WIDTH // 2, 494, WHITE, SMALL)
    draw_text("Collect coins, dodge the blocks!",
              WIDTH // 2, 518, WHITE, SMALL)
    draw_text("S = Shield   M = Magnet   + = Extra life",
              WIDTH // 2, 548, CYAN, SMALL)


# ---------- GAME HUD ----------
def draw_bar(label, value, maximum, y, color):
    draw_text(label, 12, y, color, SMALL, "left")
    bar = pygame.Rect(62, y + 3, 70, 8)
    pygame.draw.rect(screen, (30, 40, 70), bar, border_radius=4)

    fill = bar.copy()
    fill.width = max(1, int(bar.width * value / maximum))
    pygame.draw.rect(screen, color, fill, border_radius=4)


def draw_hud():
    draw_text("Score: " + str(score), 12, 12, WHITE, SMALL, "left")
    draw_text("Coins: " + str(data["coins"]), 12, 34, GOLD, SMALL, "left")

    # Lives as hearts (top right)
    for i in range(lives):
        draw_heart(WIDTH - 22 - i * 22, 14, RED)

    draw_text("Best: " + str(data["best"]), WIDTH - 12, 34, CYAN,
              SMALL, "right")

    # Active power-up timers
    bar_y = 58
    if shield > 0:
        draw_bar("Shield", shield, SHIELD_TIME, bar_y, CYAN)
        bar_y += 18
    if coin_magnet > 0:
        draw_bar("Magnet", coin_magnet, MAGNET_TIME, bar_y, GREEN)

    draw_button("||", PAUSE_BTN, (55, 65, 95))


def draw_game_scene(ox=0, oy=0):
    """Everything in the play field. Reused for playing / countdown / pause."""
    draw_background()

    for ob in obstacles:
        rect = ob["rect"].move(ox, oy)
        color = ORANGE if ob["mult"] > 1 else RED

        pygame.draw.rect(screen, color, rect, border_radius=7)
        pygame.draw.rect(screen, WHITE, rect, 1, border_radius=7)

    pulse = 10 + int(abs(math.sin(pygame.time.get_ticks() / 150)) * 4)

    for coin in coins_on_screen:
        cx = int(coin[0] + ox)
        cy = int(coin[1] + oy)

        pygame.draw.circle(screen, GOLD, (cx, cy), pulse, 2)
        pygame.draw.circle(screen, GOLD, (cx, cy), 6)

    for power in powerups:
        color = (
            CYAN if power[2] == "shield"
            else GREEN if power[2] == "magnet"
            else PINK
        )
        label = (
            "S" if power[2] == "shield"
            else "M" if power[2] == "magnet"
            else "+"
        )
        px, py = int(power[0] + ox), int(power[1] + oy)

        pygame.draw.circle(screen, color, (px, py), 14, 3)
        draw_text(label, px, py, WHITE, SMALL)

    for particle in particles:
        pygame.draw.circle(
            screen,
            particle["color"],
            (int(particle["x"] + ox), int(particle["y"] + oy)),
            3
        )

    if invincible <= 0 or invincible // 5 % 2 == 0:
        draw_player()

    draw_hud()
    draw_direction_buttons()

    if flash > 0:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 0, 0, min(255, flash * 7)))
        screen.blit(overlay, (0, 0))


dim_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
dim_overlay.fill((0, 0, 0, 150))


# ---------- GAME OVER ----------
def draw_game_over():
    draw_background()

    draw_text("GAME OVER", WIDTH // 2, 130, RED, BIG)

    new_best = score > run_start_best and score > 0

    if new_best:
        draw_text("NEW BEST!", WIDTH // 2, 175, GOLD, BIG)

    draw_text("Score: " + str(score), WIDTH // 2, 230, WHITE, BIG)
    draw_text("Best: " + str(data["best"]), WIDTH // 2, 272, CYAN)
    draw_text("Coins earned: +" + str(run_coins), WIDTH // 2, 308, GOLD)
    draw_text("Total coins: " + str(data["coins"]), WIDTH // 2, 336,
              GOLD, SMALL)

    draw_button("RESTART", OVER_RESTART_BTN, BLUE)
    draw_button("MAIN MENU", OVER_MENU_BTN, PURPLE)


# ---------- GAME UPDATE ----------
def update_game():
    global score, lives, game_speed, spawn_timer, coin_timer, power_timer
    global invincible, shield, coin_magnet, flash, shake, run_coins

    keys = pygame.key.get_pressed()
    move_speed = 6

    move_x = 0
    move_y = 0

    if (active_direction == "left"
            or keys[pygame.K_LEFT] or keys[pygame.K_a]):
        move_x -= 1

    if (active_direction == "right"
            or keys[pygame.K_RIGHT] or keys[pygame.K_d]):
        move_x += 1

    if keys[pygame.K_UP] or keys[pygame.K_w]:
        move_y -= 1

    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        move_y += 1

    magnitude = math.hypot(move_x, move_y)

    if magnitude > 1:
        move_x /= magnitude
        move_y /= magnitude

    player.x += round(move_x * move_speed)
    player.y += round(move_y * move_speed)
    player.clamp_ip(screen.get_rect())

    spawn_timer += 1
    coin_timer += 1
    power_timer += 1

    if spawn_timer >= max(15, 48 - score // 5):
        spawn_timer = 0

        size = random.randint(25, 48)
        # after a few points some blocks fall faster (orange)
        mult = 1.35 if score >= 10 and random.random() < 0.2 else 1.0

        obstacles.append({
            "rect": pygame.Rect(
                random.randint(0, WIDTH - size), -size, size, size
            ),
            "y": float(-size),
            "mult": mult
        })

    if coin_timer >= 65:
        coin_timer = 0
        coins_on_screen.append([random.randint(18, WIDTH - 18), -15, 9])

    if power_timer >= 500:
        power_timer = 0
        powerups.append([
            random.randint(22, WIDTH - 22),
            -20,
            random.choice(["shield", "magnet", "life"])
        ])

    game_speed = min(11, 4 + score // 10)

    # Slightly smaller hitbox than the drawing = fairer game
    hitbox = player.inflate(-8, -6)

    for ob in obstacles[:]:
        ob["y"] += game_speed * ob["mult"]
        ob["rect"].y = int(ob["y"])

        if ob["rect"].top > HEIGHT:
            obstacles.remove(ob)
            score += 1
            continue

        if hitbox.colliderect(ob["rect"]) and invincible <= 0:
            obstacles.remove(ob)

            if shield > 0:
                shield = 0
                invincible = 30
                add_particles(player.centerx, player.centery, CYAN)
                play_sound("power")

            else:
                lives -= 1
                invincible = 75
                flash = 12
                shake = 10

                add_particles(player.centerx, player.centery, RED)
                play_sound("hit")

                if lives <= 0:
                    end_run()
                    return

    for coin in coins_on_screen[:]:
        coin[1] += game_speed

        if coin_magnet > 0:
            dx = player.centerx - coin[0]
            dy = player.centery - coin[1]
            distance = max(1, math.hypot(dx, dy))

            if distance < 150:
                coin[0] += dx / distance * 5
                coin[1] += dy / distance * 5

        coin_rect = pygame.Rect(coin[0] - 9, coin[1] - 9, 18, 18)

        if hitbox.colliderect(coin_rect):
            data["coins"] += 1
            run_coins += 1
            coins_on_screen.remove(coin)

            add_particles(coin[0], coin[1], GOLD, 7)
            play_sound("coin")

        elif coin[1] > HEIGHT + 15:
            coins_on_screen.remove(coin)

    for power in powerups[:]:
        power[1] += game_speed - 1

        power_rect = pygame.Rect(power[0] - 12, power[1] - 12, 24, 24)

        if hitbox.colliderect(power_rect):

            if power[2] == "shield":
                shield = SHIELD_TIME

            elif power[2] == "magnet":
                coin_magnet = MAGNET_TIME

            elif power[2] == "life":
                lives = min(5, lives + 1)

            powerups.remove(power)

            add_particles(power[0], power[1], CYAN)
            play_sound("power")

        elif power[1] > HEIGHT + 20:
            powerups.remove(power)

    for particle in particles[:]:
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["life"] -= 1

        if particle["life"] <= 0:
            particles.remove(particle)

    if invincible > 0:
        invincible -= 1
    if shield > 0:
        shield -= 1
    if coin_magnet > 0:
        coin_magnet -= 1
    if flash > 0:
        flash -= 1
    if shake > 0:
        shake -= 1

    data["best"] = max(data["best"], score)


# ---------- MAIN LOOP ----------
FOCUS_LOST = getattr(pygame, "WINDOWFOCUSLOST", -1)
running = True

while running:
    clock.tick(60)

    if shop_message_timer > 0:
        shop_message_timer -= 1

    # Music plays in menus, countdown and gameplay only.
    if music_on and state in (
        "menu", "shop_skins", "shop_bg", "playing", "countdown"
    ):
        start_music()
    else:
        stop_music()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            save_game()
            running = False

        elif event.type == FOCUS_LOST:
            # auto-pause when the window loses focus
            if state in ("playing", "countdown"):
                pause_game()

        elif event.type == pygame.MOUSEWHEEL:
            if state in ("shop_skins", "shop_bg"):
                limit = shop_max_scroll(state == "shop_bg")
                shop_scroll -= event.y * 45
                shop_scroll = max(0, min(shop_scroll, limit))

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos = event.pos

                if state == "menu":

                    if PLAY_BTN.collidepoint(pos):
                        start_run()

                    elif SKINS_BTN.collidepoint(pos):
                        shop_scroll = 0
                        state = "shop_skins"
                        play_sound("click")

                    elif BG_BTN.collidepoint(pos):
                        shop_scroll = 0
                        state = "shop_bg"
                        play_sound("click")

                    elif SOUND_BTN.collidepoint(pos):
                        sound_on = not sound_on
                        play_sound("click")

                    elif MUSIC_BTN.collidepoint(pos):
                        music_on = not music_on

                elif state == "shop_skins":
                    result = handle_shop_click(pos, False)
                    if result:
                        save_game()
                        state = result

                elif state == "shop_bg":
                    result = handle_shop_click(pos, True)
                    if result:
                        save_game()
                        state = result

                elif state == "playing":

                    if PAUSE_BTN.collidepoint(pos):
                        pause_game()
                    else:
                        active_direction = direction_at(pos)

                elif state == "paused":

                    if RESUME_BTN.collidepoint(pos):
                        resume_game()
                    elif PAUSE_RESTART_BTN.collidepoint(pos):
                        start_run()
                    elif PAUSE_MENU_BTN.collidepoint(pos):
                        go_to_menu()

                elif state == "gameover":

                    if OVER_RESTART_BTN.collidepoint(pos):
                        start_run()
                    elif OVER_MENU_BTN.collidepoint(pos):
                        go_to_menu()

        elif event.type == pygame.MOUSEMOTION:
            if state == "playing" and event.buttons[0]:
                active_direction = direction_at(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                release_direction()

        elif event.type == pygame.KEYDOWN:

            if event.key in (pygame.K_ESCAPE, pygame.K_p):

                if state in ("playing", "countdown"):
                    pause_game()

                elif state == "paused":
                    resume_game()

                elif state in ("shop_skins", "shop_bg", "gameover"):
                    go_to_menu()

            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):

                if state in ("menu", "gameover"):
                    start_run()

                elif state == "paused":
                    resume_game()

    # ---------- UPDATE ----------
    if state == "countdown":
        countdown_timer -= 1

        if countdown_timer % 30 == 29:
            play_sound("beep")

        if countdown_timer <= 0:
            play_sound("go")
            state = "playing"

    elif state == "playing":
        update_game()

    # ---------- DRAW ----------
    if state == "menu":
        draw_menu()

    elif state in ("shop_skins", "shop_bg"):
        draw_shop(state == "shop_bg")

    elif state == "playing":
        ox = random.randint(-shake, shake) if shake else 0
        oy = random.randint(-shake, shake) if shake else 0
        draw_game_scene(ox, oy)

    elif state == "countdown":
        draw_game_scene()
        screen.blit(dim_overlay, (0, 0))
        draw_text(str(countdown_timer // 30 + 1),
                  WIDTH // 2, HEIGHT // 2 - 40, CYAN, HUGE)
        draw_text("Get ready!", WIDTH // 2, HEIGHT // 2 + 30, WHITE)

    elif state == "paused":
        draw_game_scene()
        screen.blit(dim_overlay, (0, 0))

        draw_text("PAUSED", WIDTH // 2, 175, CYAN, BIG)
        draw_button("RESUME", RESUME_BTN, BLUE)
        draw_button("RESTART", PAUSE_RESTART_BTN, PURPLE)
        draw_button("MAIN MENU", PAUSE_MENU_BTN, GREEN)

    elif state == "gameover":
        draw_game_over()

    pygame.display.flip()

save_game()
stop_music()
pygame.quit()
sys.exit()
