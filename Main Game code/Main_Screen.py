import pygame
import os
import random
from Betting import BettingSystem
from Upgrades import UpgradeManager

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1200, 800

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

pygame.display.set_mode((1200, 800), pygame.RESIZABLE)
pygame.display.set_caption("Roulette Game")

clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# ---------------- IMAGES ----------------
menu_bg = pygame.image.load(os.path.join(BASE_DIR, "Resources", "Images", "Background", "Roulette main screen.png"))
game_over_bg = pygame.image.load(os.path.join(BASE_DIR, "Resources", "Images", "Background", "GameOver.png"))
victory_bg = pygame.image.load(os.path.join(BASE_DIR, "Resources", "Images", "Background", "Victory Screen.png"))

# ---------------- MUSIC ----------------
menu_music = os.path.join(BASE_DIR, "Resources", "Music", "Background Music.wav")
game_music = os.path.join(BASE_DIR, "Resources", "Music", "Game music.wav")
game_over_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "Resources", "Music", "GameOver.wav"))
victory_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "Resources", "Music", "Victory.wav"))

pygame.mixer.music.load(menu_music)
pygame.mixer.music.play(-1)

current_music = "menu"

# ---------------- SPIN ----------------
spin_frames = []
spin_index = 0
spinning = False
spin_start_time = 0
spin_duration = 4200

spin_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "Resources", "Music", "Spinning effect.wav"))

final_frame_locked = 0

for i in range(1, 27):
    img_path = os.path.join(BASE_DIR, "Resources", "Images", "Spinning", f"sprite_{str(i).zfill(2)}.png")
    spin_frames.append(pygame.image.load(img_path).convert_alpha())

# ---------------- CHIPS ----------------
chip_values = [1, 5, 10, 25, 100, 500, 1000, 5000]
chips = {}

dragging_chip = False
drag_chip_img = None
drag_chip_value = None

placed_chips = []
chip_grid = []


for value in chip_values:
    path = os.path.join(BASE_DIR, "Resources", "Images", "Casino chips", f"{value}.png")
    chips[value] = pygame.image.load(path).convert_alpha()

def get_chip_bar_positions():
    chip_size = 60
    spacing = 10

    total_width = len(chip_values) * chip_size + (len(chip_values) - 1) * spacing
    start_x = max(20, WIDTH - total_width - 20)
    y = HEIGHT - 90

    rects = []
    for i, value in enumerate(chip_values):
        rect = pygame.Rect(start_x + i * (chip_size + spacing), y, chip_size, chip_size)
        rects.append((rect, value))
    return rects
# ---------------- COLORS ----------------
WHITE = (245, 255, 255)
BLACK_COLOR = (20, 20, 20)

GOLD = (255, 215, 0)

RED_COLOR = (200, 30, 30)

GREEN = (0, 200, 0)

GRAY = (180, 180, 180)
DARK_GRAY = (60, 60, 60)

SELECTED = (255, 255, 0)
# ---------------- FONTS ----------------
font = pygame.font.SysFont("arialblack", 24)
title_font = pygame.font.SysFont("arialblack", 52)
button_font = pygame.font.SysFont("arialblack", 30)

# ---------------- STATES ----------------
MAIN = "main"
RULES = "rules"
CREDITS = "credits"
GAME = "game"
GAME_OVER = "game_over"
VICTORY = "victory"
UPGRADES = "upgrades"

state = MAIN

# ---------------- CONTENT ----------------
rules_text = [
    "Player starts with $600",
    "Place bet before spinning",
    "Red / Black = x2 payout",
    "0 - 13 = x4 payout",
    "14 - 25 = x4 + $15",
    "Reach $8,000 for a suprise",
    "Lose everything = game over",
    "Use Upgrades to improve your chances",
    "Press C to clear Board",
    "Esc button to leave the game"
]

credits_text = [
    "Game Developer: Henry",
    "Designer: Henry",
    "High Roller's Club - TEKKEN Project",
    "Blinding Lights - The Weeknd",
    "Sound Diary - Roulette SFX",
    "Super Mario GameOver - SuperMarioBros"
]

# ---------------- BUTTONS ----------------
button_height = 50

buttons_main = {
    "Start": pygame.Rect(10, 10, 140, button_height),
    "Rules": pygame.Rect(160, 10, 140, button_height),
    "Credits": pygame.Rect(310, 10, 140, button_height),
}

return_button = pygame.Rect(10, 640, 160, button_height)
spin_button = pygame.Rect(WIDTH // 2 - 380, HEIGHT // 2 + 40, 180, 50)

def get_top_right_buttons():
    button_width = 160
    button_height = 50
    spacing = 10

    # Total width of both buttons together
    total_width = button_width * 2 + spacing

    # Start position from right side
    start_x = WIDTH - total_width - 20

    payout_button = pygame.Rect(
        start_x,
        10,
        button_width,
        button_height
    )

    upgrade_button = pygame.Rect(
        start_x + button_width + spacing,
        10,
        button_width,
        button_height
    )

    return payout_button, upgrade_button
# ---------------- UI ----------------
def draw_text_box(text, x, y, width=600, height=40):
    box_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    box_surface.fill((0, 0, 0, 160))

    pygame.draw.rect(box_surface, (255, 215, 0), box_surface.get_rect(), 2, border_radius=8)

    txt = font.render(text, True, (255, 255, 255))
    box_surface.blit(txt, ((width - txt.get_width()) // 2, (height - txt.get_height()) // 2))

    screen.blit(box_surface, (x, y))


def draw_button(text, rect, hover=False):
    green = (0, 180, 0)
    dark_green = (0, 120, 0)
    gold = (255, 215, 0)

    color = dark_green if hover else green

    pygame.draw.rect(screen, gold, rect.inflate(6, 6), border_radius=10)
    pygame.draw.rect(screen, color, rect, border_radius=10)

    label = button_font.render(text, True, (255, 255, 255))
    screen.blit(label, (
        rect.x + (rect.width - label.get_width()) // 2,
        rect.y + (rect.height - label.get_height()) // 2
    ))


def draw_balance_box(amount):
    rect = pygame.Rect(20, 20, 180, 50)

    pygame.draw.rect(screen, (255, 215, 0), rect.inflate(6, 6), border_radius=10)
    pygame.draw.rect(screen, (0, 180, 0), rect, border_radius=10)

    label = button_font.render(f"${amount}", True, (255, 255, 255))
    screen.blit(label, (
        rect.x + (rect.width - label.get_width()) // 2,
        rect.y + (rect.height - label.get_height()) // 2
    ))

def draw_result_box(result_text, x, y):
    rect = pygame.Rect(x, y, 300, 50)

    pygame.draw.rect(screen, (255, 215, 0), rect.inflate(6, 6), border_radius=10)
    pygame.draw.rect(screen, (0, 180, 0), rect, border_radius=10)

    screen.blit(button_font.render(result_text, True, (255, 255, 255)), (x + 10, y + 10))

def get_bottom_button():
    width = 320
    height = 70

    x = (WIDTH - width) // 2
    y = HEIGHT - height - 30  # always 30px from bottom edge

    return pygame.Rect(x, y, width, height)

def draw_won_box(won_text, x, y):
    rect = pygame.Rect(x, y, 180, 50)

    pygame.draw.rect(screen, (255, 215, 0), rect.inflate(6, 6), border_radius=10)
    pygame.draw.rect(screen, (0, 180, 0), rect, border_radius=10)

    screen.blit(button_font.render(won_text, True, (255, 255, 255)), (x + 10, y + 10))


def get_bet_menu_layout():
    menu_width = 900
    menu_height = 760

    menu_rect = pygame.Rect(
        (WIDTH - menu_width) // 2,
        (HEIGHT - menu_height) // 2,
        menu_width,
        menu_height
    )

    close_rect = pygame.Rect(
        menu_rect.right - 60,
        menu_rect.top + 20,
        30,
        30
    )

    # TOP BET BUTTONS
    red_rect = pygame.Rect(
        menu_rect.left + 70,
        menu_rect.top + 120,
        150,
        55
    )

    zero_rect = pygame.Rect(
        menu_rect.centerx - 40,
        menu_rect.top + 120,
        80,
        55
    )

    black_rect = pygame.Rect(
        menu_rect.right - 220,
        menu_rect.top + 120,
        150,
        55
    )

    # NUMBER GRID
    number_rects = []

    grid_columns = 5
    start_x = menu_rect.centerx - 170
    start_y = menu_rect.top + 220

    for i in range(1, 26):
        index = i - 1

        x = start_x + (index % grid_columns) * 70
        y = start_y + (index // grid_columns) * 62

        number_rects.append((
            str(i),
            pygame.Rect(x, y, 58, 48)
        ))

    # BET COUNT
    count_input_rect = pygame.Rect(
        menu_rect.left + 70,
        menu_rect.bottom - 180,
        180,
        55
    )

    count_button_rects = []

    for i in range(5):
        rect = pygame.Rect(
            menu_rect.left + 270 + i * 110,
            menu_rect.bottom - 180,
            100,
            55
        )

        count_button_rects.append((str(i + 1), rect))

    # BET AMOUNT
    input_rect = pygame.Rect(
        menu_rect.left + 70,
        menu_rect.bottom - 95,
        380,
        55
    )

    # CONFIRM BUTTON
    confirm_rect = pygame.Rect(
        input_rect.right + 25,
        menu_rect.bottom - 95,
        240,
        55
    )

    return {
        "menu_rect": menu_rect,
        "close_rect": close_rect,
        "red_rect": red_rect,
        "zero_rect": zero_rect,
        "black_rect": black_rect,
        "number_rects": number_rects,
        "count_input_rect": count_input_rect,
        "count_button_rects": count_button_rects,
        "input_rect": input_rect,
        "confirm_rect": confirm_rect,
    }

def get_upgrade_menu_layout():
    menu_width = 820
    menu_height = 620
    menu_rect = pygame.Rect((WIDTH - menu_width) // 2, (HEIGHT - menu_height) // 2, menu_width, menu_height)

    close_rect = pygame.Rect(menu_rect.right - 70, menu_rect.top + 20, 30, 30)

    options = []
    categories = ["bonus", "refund", "luck"]
    for row, category in enumerate(categories):
        label_y = menu_rect.top + 150 + row * 140
        current_level = getattr(upgrades, f"{category}_level", 0)
        next_level = min(current_level + 1, 3)
        button_rect = pygame.Rect(menu_rect.right - 420, label_y, 360, 70)
        options.append((category, current_level, next_level, button_rect))

    return {
        "menu_rect": menu_rect,
        "close_rect": close_rect,
        "options": options,
    }


def get_bet_chance_text(bet_type):
    if not bet_type:
        return ""
    chance = upgrades.get_effective_chance(bet_type)
    return f"Win chance: {int(chance * 100)}%"


def get_spin_result(bet_type, luck_rate):
    if bet_type and random.random() < luck_rate:
        if bet_type == "red":
            return random.choice(tuple(RED))
        if bet_type == "black":
            return random.choice(tuple(BLACK))
        if bet_type.isdigit():
            return int(bet_type)
    return random.randint(0, 25)

# ---------------- BETTING SYSTEM ----------------
betting = BettingSystem()
upgrades = UpgradeManager()


def reset_game():
    global last_result, last_win, last_bet_type, pending_state, pending_state_start, spinning
    global bet_menu, selected_bet_type, selected_bet_amount, bet_amount_input, bet_quantity_input, typing_amount, typing_quantity

    betting.reset()
    upgrades.reset()
    last_result = None
    last_win = 0
    last_bet_type = None
    pending_state = None
    pending_state_start = 0
    spinning = False
    spin_sound.stop()
    placed_chips.clear()
    bet_menu = False
    selected_bet_type = None
    selected_bet_amount = 0
    bet_amount_input = ""
    bet_quantity_input = "1"
    typing_amount = False
    typing_quantity = False

bet_menu = False
upgrade_menu = False
payout_menu = False
selected_bet_type = None
selected_bet_amount = 0

def confirm_bet():
    global bet_menu, spinning, spin_start_time, final_frame_locked
    global bet_quantity_input, typing_amount, typing_quantity
    global selected_bet_type, selected_bet_amount, bet_amount_input

    total_bets = int(bet_quantity_input) if bet_quantity_input in ["1", "2", "3", "4", "5"] else 1

    placed_amount_by_type = {}
    unique_areas = []
    for chip in placed_chips:
        bet_type = chip.get("bet_type")
        if bet_type is None:
            continue
        if bet_type not in unique_areas:
            unique_areas.append(bet_type)
        placed_amount_by_type[bet_type] = placed_amount_by_type.get(bet_type, 0) + int(chip.get("value") or 0)

    typed_amt = 0
    if bet_amount_input != "":
        try:
            typed_amt = int(bet_amount_input)
        except ValueError:
            typed_amt = 0

    # If the player has placed chips but hasn't explicitly selected an area,
    # auto-select the single placed area so the confirm logic can proceed.
    if selected_bet_type is None and placed_amount_by_type:
        if len(placed_amount_by_type) == 1:
            # pick the only placed area
            selected_bet_type = next(iter(placed_amount_by_type.keys()))
        else:
            # multiple placed areas exist; require explicit selection
            bet_amount_input = ""
            typing_amount = True
            return

    placed_amt_for_selected = placed_amount_by_type.get(selected_bet_type, 0)
    # If typed amount is larger than the chips placed on the selected area,
    # pre-fill the input with the placed amount and keep typing focus so the
    # player can quickly confirm or edit the value without re-placing chips.
    if typed_amt > 0 and placed_amt_for_selected > 0 and typed_amt > placed_amt_for_selected:
        bet_amount_input = str(placed_amt_for_selected)
        typing_amount = True
        return

    # Refund any chips that were dropped outside a valid bet area.
    unassigned_chips = [c for c in placed_chips if c.get("bet_type") is None]
    if unassigned_chips:
        refund_amount = sum(int(c.get("value") or 0) for c in unassigned_chips)
        betting.balance += refund_amount
        placed_chips[:] = [c for c in placed_chips if c.get("bet_type") is not None]

    bets_to_place = []
    refund_amounts = {}
    for bet_type in unique_areas:
        if len(bets_to_place) >= total_bets:
            break
        placed_amount = placed_amount_by_type.get(bet_type, 0)
        if placed_amount <= 0:
            continue

        if bet_type == selected_bet_type and typed_amt > 0:
            if typed_amt <= placed_amount:
                bets_to_place.append((bet_type, typed_amt, True))
                refund_amounts[bet_type] = placed_amount - typed_amt
            else:
                bets_to_place.append((bet_type, placed_amount, True))
        else:
            bets_to_place.append((bet_type, placed_amount, True))

    if len(bets_to_place) < total_bets and selected_bet_type and bet_amount_input != "":
        selected_has_placed_chips = placed_amount_by_type.get(selected_bet_type, 0) > 0
        if (
            not selected_has_placed_chips
            and typed_amt > 0
            and typed_amt <= betting.balance
            and selected_bet_type not in [bt for bt, _, _ in bets_to_place]
        ):
            bets_to_place.append((selected_bet_type, typed_amt, False))

    placed_area_keys = set()
    for bet_type, amount, has_placed in bets_to_place:
        if amount <= 0:
            continue
        if has_placed:
            success = betting.set_bet(bet_type, amount, deduct=False)
            if success:
                placed_area_keys.add(bet_type)
                if refund_amounts.get(bet_type, 0) > 0:
                    betting.balance += refund_amounts[bet_type]
        else:
            success = betting.set_bet(bet_type, amount, deduct=True)
        if success and has_placed:
            placed_area_keys.add(bet_type)

    if placed_area_keys:
        placed_chips[:] = [c for c in placed_chips if c.get("bet_type") not in placed_area_keys]

    if len(betting.bets) >= total_bets and len(betting.bets) > 0:
        bet_menu = False
        spinning = True
        spin_start_time = pygame.time.get_ticks()
        spin_sound.play()
        final_frame_locked = get_spin_result(betting.bets[-1]["type"] if betting.bets else None, upgrades.get_luck_rate())
        bet_quantity_input = "1"
        typing_quantity = False
        selected_bet_type = None
        selected_bet_amount = 0
        bet_amount_input = ""
        typing_amount = False
    else:
        selected_bet_type = None
        selected_bet_amount = 0
        bet_amount_input = ""
        typing_amount = False
        typing_quantity = False

bet_amount_input = ""
bet_quantity_input = "1"
typing_amount = False
typing_quantity = False

last_result = None
last_win = 0
last_bet_type = None
pending_state = None
pending_state_start = 0
end_screen_delay = 1500  # milliseconds delay before showing game over/victory screen

RED = {1,3,5,7,9,11,13,15,17,19,21,23,25}
BLACK = {2,4,6,8,10,12,14,16,18,20,22,24}

# ---------------- LOOP ----------------
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    chip_bar = get_chip_bar_positions()

    payout_button, upgrade_button = get_top_right_buttons()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ESC RESET
        if event.type == pygame.KEYDOWN:
            if typing_amount:
                if event.key == pygame.K_BACKSPACE:
                    bet_amount_input = bet_amount_input[:-1]
                elif event.unicode.isdigit():
                    bet_amount_input += event.unicode

            if typing_quantity:
                if event.key == pygame.K_BACKSPACE:
                    bet_quantity_input = bet_quantity_input[:-1]
                elif event.unicode in "12345":
                    bet_quantity_input = event.unicode

            if event.key == pygame.K_ESCAPE:
                state = MAIN

                if current_music != "menu":
                    pygame.mixer.music.load(menu_music)
                    pygame.mixer.music.play(-1)
                    current_music = "menu"

                reset_game()

            if event.key == pygame.K_c:
                if placed_chips:
                    refund_amount = sum(int(chip.get("value") or 0) for chip in placed_chips)
                    betting.balance += refund_amount
                    placed_chips.clear()
                selected_bet_type = None
                selected_bet_amount = 0
                bet_amount_input = ""
                typing_amount = False

            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and bet_menu:
                confirm_bet()

        if event.type == pygame.VIDEORESIZE:
            WIDTH = max(1000, event.w)
            HEIGHT = max(700, event.h)
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            spin_button = pygame.Rect(WIDTH // 2 - 480, HEIGHT // 2 + 40, 180, 50)
        
        # CLICK
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:

                if state == MAIN:
                    if buttons_main["Start"].collidepoint(mouse_pos):
                        reset_game()
                        state = GAME

                        if current_music != "game":
                            pygame.mixer.music.load(game_music)
                            pygame.mixer.music.play(-1)
                            current_music = "game"

                    elif buttons_main["Rules"].collidepoint(mouse_pos):
                        state = RULES

                    elif buttons_main["Credits"].collidepoint(mouse_pos):
                        state = CREDITS

                elif state in [RULES, CREDITS]:
                    if return_button.collidepoint(mouse_pos):
                        state = MAIN

                elif state == GAME:
                    if pending_state is None:
                        if upgrade_menu:
                            layout = get_upgrade_menu_layout()
                            close_rect = layout["close_rect"]

                            if close_rect.collidepoint(mouse_pos):
                                upgrade_menu = False
                            else:
                                for category, current_level, next_level, rect in layout["options"]:
                                    if rect.collidepoint(mouse_pos) and current_level < 3:
                                        if upgrades.can_purchase(category, next_level, betting.balance):
                                            betting.balance = upgrades.purchase(category, next_level, betting.balance)
                        elif bet_menu:
                            layout = get_bet_menu_layout()
                            red_rect = layout["red_rect"]
                            zero_rect = layout["zero_rect"]
                            black_rect = layout["black_rect"]
                            input_rect = layout["input_rect"]
                            confirm_rect = layout["confirm_rect"]
                            close_rect = layout["close_rect"]

                            if close_rect.collidepoint(mouse_pos):
                                # Refund any already-placed confirmed bets
                                for bet in betting.bets:
                                    betting.balance += bet["amount"]
                                betting.bets.clear()
                                # Refund any chips currently placed on the board
                                if placed_chips:
                                    refund_amount = sum(int(ch.get("value") or 0) for ch in placed_chips)
                                    betting.balance += refund_amount
                                    placed_chips.clear()
                                bet_menu = False
                                selected_bet_type = None
                                selected_bet_amount = 0
                                bet_amount_input = ""
                                bet_quantity_input = "1"
                                typing_amount = False
                                typing_quantity = False
        
                            elif red_rect.collidepoint(mouse_pos):
                                selected_bet_type = "red"

                            elif black_rect.collidepoint(mouse_pos):
                                selected_bet_type = "black"

                            elif zero_rect.collidepoint(mouse_pos):
                                selected_bet_type = "0"

                            else:
                                for number, rect in layout["number_rects"]:
                                    if rect.collidepoint(mouse_pos):
                                        selected_bet_type = number
                                        break

                            if layout["count_input_rect"].collidepoint(mouse_pos):
                                typing_quantity = True
                                typing_amount = False
                            elif input_rect.collidepoint(mouse_pos):
                                typing_amount = True
                                typing_quantity = False
                            else:
                                typing_amount = False
                                typing_quantity = False

                            for count_number, count_rect in layout["count_button_rects"]:
                                if count_rect.collidepoint(mouse_pos):
                                    bet_quantity_input = count_number
                                    break

                            if confirm_rect.collidepoint(mouse_pos):
                                confirm_bet()

                        else:
                            if spin_button.collidepoint(mouse_pos) and not spinning:
                                bet_menu = True
                            elif upgrade_button.collidepoint(mouse_pos):
                                upgrade_menu = True
                            elif payout_button.collidepoint(mouse_pos):
                                payout_menu = not payout_menu
                            if payout_menu:
                                payout_rect = pygame.Rect(
                                    WIDTH // 2 - 350,
                                    HEIGHT // 2 - 250,
                                    800,
                                    550
                                    )
                                payout_close_rect = pygame.Rect(
                                    payout_rect.right - 50,
                                    payout_rect.top + 20,
                                    30,
                                    30
                                    )
                                if payout_close_rect.collidepoint(mouse_pos):
                                    payout_menu = False

                            # CHIP PICKUP: only pick up a new chip when not already dragging one
                            if not dragging_chip:
                                for rect, value in chip_bar:
                                    if rect.collidepoint(mouse_pos):
                                        if betting.balance >= value:
                                            dragging_chip = True
                                            drag_chip_img = chips[value]
                                            drag_chip_value = value
                                            betting.balance -= value
                                        break

                elif state in [RULES, CREDITS]:
                    if return_button.collidepoint(mouse_pos):
                        state = MAIN

                        if current_music != "menu":
                            pygame.mixer.music.load(menu_music)
                            pygame.mixer.music.play(-1)
                            current_music = "menu"

                        reset_game()

                elif state == GAME_OVER:
                    if get_bottom_button().collidepoint(mouse_pos):
                        # Stop any end-screen music/sounds
                        pygame.mixer.music.stop()
                        spin_sound.stop()
                        try:
                            game_over_sound.stop()
                        except NameError:
                            pass
                        try:
                            victory_sound.stop()
                        except NameError:
                            pass

                        state = MAIN

                        if current_music != "menu":
                            pygame.mixer.music.load(menu_music)
                            pygame.mixer.music.play(-1)
                            current_music = "menu"

                        reset_game()

                elif state == VICTORY:
                    if get_bottom_button().collidepoint(mouse_pos):
                        # Stop any end-screen music/sounds
                        pygame.mixer.music.stop()
                        spin_sound.stop()
                        try:
                            victory_sound.stop()
                        except NameError:
                            pass
                        try:
                            game_over_sound.stop()
                        except NameError:
                            pass

                        state = MAIN

                        if current_music != "menu":
                            pygame.mixer.music.load(menu_music)
                            pygame.mixer.music.play(-1)
                            current_music = "menu"

                        reset_game()

        # CHIP DROP
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if dragging_chip and drag_chip_img is not None:
                    # If bet menu is open, snap chip to the bet area under the cursor and tag with bet_type
                    if bet_menu:
                        layout = get_bet_menu_layout()
                        target = None
                        target_rect = None
                        if layout["red_rect"].collidepoint(mouse_pos):
                            target = "red"
                            target_rect = layout["red_rect"]
                        elif layout["black_rect"].collidepoint(mouse_pos):
                            target = "black"
                            target_rect = layout["black_rect"]
                        elif layout["zero_rect"].collidepoint(mouse_pos):
                            target = "0"
                            target_rect = layout["zero_rect"]
                        else:
                            for number, rect in layout["number_rects"]:
                                if rect.collidepoint(mouse_pos):
                                    target = number
                                    target_rect = rect
                                    break

                        if target and target_rect is not None:
                            # Stack chips neatly on the area
                            same_area = [c for c in placed_chips if c.get("bet_type") == target]
                            idx = len(same_area)
                            offset_x = (idx % 5) * 12 - (min(len(same_area)+1,5)-1) * 6
                            offset_y = (idx // 5) * 10
                            pos = (target_rect.centerx - 30 + offset_x, target_rect.centery - 30 + offset_y)
                            placed_chips.append({
                                "img": drag_chip_img,
                                "pos": pos,
                                "value": drag_chip_value,
                                "bet_type": target
                            })
                            # auto-select the area
                            selected_bet_type = target
                        else:
                            # Refund chips dropped outside a valid area when the bet menu is open.
                            betting.balance += drag_chip_value
                    else:
                        placed_chips.append({
                            "img": drag_chip_img,
                            "pos": (mouse_pos[0] - 30, mouse_pos[1] - 30),
                            "value": drag_chip_value,
                            "bet_type": None
                        })
                dragging_chip = False
                drag_chip_img = None
                drag_chip_value = None

    # ---------------- DRAW ----------------
    screen.blit(pygame.transform.scale(menu_bg, (WIDTH, HEIGHT)), (0, 0))

    if state == MAIN:
        for name, rect in buttons_main.items():
            draw_button(name, rect, rect.collidepoint(mouse_pos))

    elif state == RULES:
        draw_button("Return", return_button, return_button.collidepoint(mouse_pos))
        title = title_font.render("RULES", True, (255, 215, 0))
        screen.blit(title, ((WIDTH - title.get_width()) // 2, 40))

        y = 140
        for line in rules_text:
            draw_text_box(line, (WIDTH - 600) // 2, y)
            y += 60

    elif state == CREDITS:
        draw_button("Return", return_button, return_button.collidepoint(mouse_pos))
        title = title_font.render("CREDITS", True, (255, 215, 0))
        screen.blit(title, ((WIDTH - title.get_width()) // 2, 40))

        y = 140
        for line in credits_text:
            draw_text_box(line, (WIDTH - 600) // 2, y)
            y += 60

    elif state == GAME:
        if bet_menu:
            pass

        if spinning:
            now = pygame.time.get_ticks()
            progress = min((now - spin_start_time) / 4000, 1)

            spin_index = int(progress * len(spin_frames)) % len(spin_frames)

            if progress >= 1:
                spinning = False
                spin_sound.stop()
                spin_index = final_frame_locked

                last_result = final_frame_locked
                last_bet_type = betting.bet["type"] if betting.bet else None
                last_win = betting.resolve(
                    final_frame_locked,
                    refund_rate=upgrades.get_refund_rate(),
                    bonus_amount=upgrades.get_bonus_amount()
                )
                placed_chips.clear()
                selected_bet_type = None
                bet_amount_input = ""

                if betting.balance >= 8000:
                        pending_state = VICTORY
                        pending_state_start = now
                        pygame.mixer.music.stop()
                        victory_sound.play()
                elif betting.balance == 0:
                    pending_state = GAME_OVER
                    pending_state_start = now
                    pygame.mixer.music.stop()
                    game_over_sound.play()

        else:
            spin_index = final_frame_locked

        if pending_state is not None and not spinning:
            now = pygame.time.get_ticks()
            if now - pending_state_start >= end_screen_delay:
                state = pending_state
                pending_state = None

        frame = pygame.transform.scale(spin_frames[spin_index], (WIDTH, HEIGHT))
        screen.blit(frame, (0, 0))

        draw_button("SPIN", spin_button, spin_button.collidepoint(mouse_pos))
        draw_button("Upgrades", upgrade_button, upgrade_button.collidepoint(mouse_pos))
        draw_button("Payouts", payout_button, payout_button.collidepoint(mouse_pos))
        draw_balance_box(betting.balance)

        # RESULT
        result_text = "-"
        if last_result is not None:
            color = "GREEN"
            if last_result in RED:
                color = "RED"
            elif last_result in BLACK:
                color = "BLACK"
            result_text = f"{last_result}({color})"

        won_text = f"Won: ${last_win}"
        draw_result_box(result_text, 220, 20)
        draw_won_box(won_text, 540, 20)

        # CHIPS
        for chip in placed_chips:
            screen.blit(pygame.transform.scale(chip["img"], (60, 60)), chip["pos"])

        for rect, value in chip_bar:
            screen.blit(pygame.transform.scale(chips[value], (60, 60)), rect.topleft)

        if dragging_chip:
            screen.blit(pygame.transform.scale(drag_chip_img, (60, 60)),
                        (mouse_pos[0] - 30, mouse_pos[1] - 30))

        if upgrade_menu:
            layout = get_upgrade_menu_layout()
            menu_rect = layout["menu_rect"]
            close_rect = layout["close_rect"]

            pygame.draw.rect(screen, (15, 15, 15), menu_rect, border_radius=12)
            pygame.draw.rect(screen, GOLD, menu_rect, 4, border_radius=12)

            pygame.draw.rect(screen, RED_COLOR, close_rect, border_radius=4)
            pygame.draw.line(screen, WHITE, (close_rect.left + 3, close_rect.top + 3), (close_rect.right - 3, close_rect.bottom - 3), 3)
            pygame.draw.line(screen, WHITE, (close_rect.right - 3, close_rect.top + 3), (close_rect.left + 3, close_rect.bottom - 3), 3)

            title = title_font.render("UPGRADES", True, WHITE)
            screen.blit(title, ((WIDTH - title.get_width()) // 2, menu_rect.top + 20))

            draw_text_box(f"Balance: ${betting.balance}", menu_rect.left + 60, menu_rect.top + 90, width=300, height=40)

            labels = [
                ("Bonus Money", upgrades.bonus_level, ["+15", "+25", "+50"], "bonus"),
                ("Refund on Loss", upgrades.refund_level, ["10%", "25%", "45%"], "refund"),
                ("Luck Boost", upgrades.luck_level, ["+5%", "+20%", "+40%"], "luck"),
            ]

            for row, (label, level, values, category) in enumerate(labels):
                section_y = menu_rect.top + 150 + row * 140
                screen.blit(button_font.render(label, True, WHITE), (menu_rect.left + 60, section_y))

                if level > 0:
                    current_text = font.render(f"Current Level: Lv{level} {values[level-1]}", True, WHITE)
                else:
                    current_text = font.render("Current Level: None", True, WHITE)
                screen.blit(current_text, (menu_rect.left + 60, section_y + 40))

                rect = layout["options"][row][3]
                if level < 3:
                    next_level = level + 1
                    cost = upgrades._get_cost(category, next_level)
                    button_text = f"Lv{next_level} {values[next_level-1]} ${cost}"
                    if upgrades.can_purchase(category, next_level, betting.balance):
                        draw_button(button_text, rect, rect.collidepoint(mouse_pos))
                    else:
                        pygame.draw.rect(screen, DARK_GRAY, rect, border_radius=10)
                        btn_text = font.render(button_text, True, WHITE)
                        screen.blit(btn_text, (rect.left + 10, rect.top + (rect.height - btn_text.get_height()) // 2))
                else:
                    button_text = "MAX LEVEL"
                    pygame.draw.rect(screen, DARK_GRAY, rect, border_radius=10)
                    txt = button_font.render(button_text, True, WHITE)
                    screen.blit(txt, (
                        rect.left + (rect.width - txt.get_width()) // 2,
                        rect.top + (rect.height - txt.get_height()) // 2
                    ))
        # ---------------- PAYOUT MENU ----------------
        if payout_menu:

            payout_rect = pygame.Rect(
                WIDTH // 2 - 350,
                HEIGHT // 2 - 250,
                800,
                600
            )
            payout_close_rect = pygame.Rect(
                payout_rect.right - 50,
                payout_rect.top + 20,
                30,
                30
                )
            
            pygame.draw.rect(screen, (15, 15, 15), payout_rect, border_radius=12)
            pygame.draw.rect(screen, GOLD, payout_rect, 4, border_radius=12)
            pygame.draw.rect(screen, RED_COLOR, payout_close_rect, border_radius=4)
            pygame.draw.line(
                screen, WHITE,
                (payout_close_rect.left + 3, payout_close_rect.top + 3),
                (payout_close_rect.right - 3, payout_close_rect.bottom - 3), 3
                )
            pygame.draw.line(
                screen, WHITE,
                (payout_close_rect.right - 3, payout_close_rect.top + 3),
                (payout_close_rect.left + 3, payout_close_rect.bottom - 3), 3
                )

            title = title_font.render("PAYOUTS & UPGRADES", True, GOLD)

            screen.blit(
                title,
                (
                    payout_rect.centerx - title.get_width() // 2,
                    payout_rect.top + 20
                )
            )

            payout_lines = [
                "RED = x2 payout",
                "BLACK = x2 payout",
                "0 - 13 = x4 payout",
                "14 - 25 = x4 + $15",
                "",
                "BONUS Level 1 = + $15",
                "BONUS Level 2 = + $25",
                "BONUS Level 3 = + $50",
                "REFUND Level 1 = 10 percent back on losses",
                "REFUND Level 2 = 25 percent back on losses",
                "REFUND Level 3 = 45 percent back on losses",
                "LUCK Level 1 = 5 percent",
                "LUCK Level 2 = 20 percent",
                "LUCK Level 3 = 40 percent",
            ]

            y = payout_rect.top + 90

            for line in payout_lines:

                txt = font.render(line, True, WHITE)

                screen.blit(
                    txt,
                    (
                        payout_rect.left + 40,
                        y
                    )
                )

                y += 35
        # ---------------- BET MENU ----------------
        if bet_menu:
            layout = get_bet_menu_layout()
            menu_rect = layout["menu_rect"]
            close_rect = layout["close_rect"]
            red_rect = layout["red_rect"]
            zero_rect = layout["zero_rect"]
            black_rect = layout["black_rect"]
            count_input_rect = layout["count_input_rect"]
            count_button_rects = layout["count_button_rects"]
            input_rect = layout["input_rect"]
            confirm_rect = layout["confirm_rect"]

            # DIM BACKGROUND SO UNDERLYING CHIPS ARE HIDDEN
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            # BACKGROUND
            pygame.draw.rect(screen, (15, 15, 15), menu_rect, border_radius=12)
            pygame.draw.rect(screen, GOLD, menu_rect, 4, border_radius=12)

            # CLOSE BUTTON
            pygame.draw.rect(screen, RED_COLOR, close_rect, border_radius=4)
            pygame.draw.line(screen, WHITE, (close_rect.left + 3, close_rect.top + 3), (close_rect.right - 3, close_rect.bottom - 3), 3)
            pygame.draw.line(screen, WHITE, (close_rect.right - 3, close_rect.top + 3), (close_rect.left + 3, close_rect.bottom - 3), 3)

            # TITLE
            title = title_font.render("PLACE BET", True, WHITE)
            screen.blit(title, ((WIDTH - title.get_width()) // 2, menu_rect.top + 20))

            for count_number, count_rect in count_button_rects:
                selected = bet_quantity_input == count_number
                pygame.draw.rect(screen, SELECTED if selected else DARK_GRAY, count_rect, border_radius=8)
                num_text = font.render(count_number, True, WHITE)
                screen.blit(num_text, (count_rect.centerx - num_text.get_width() // 2, count_rect.centery - num_text.get_height() // 2))

            total_bets = int(bet_quantity_input) if bet_quantity_input in ["1", "2", "3", "4", "5"] else 1
            current_bet_index = min(len(betting.bets) + 1, total_bets)
            status_surface = font.render(f"Placing bet {current_bet_index} of {total_bets}", True, WHITE)
            screen.blit(status_surface,(menu_rect.left + 70, menu_rect.top + 180))

            # RED BUTTON
            red_selected = selected_bet_type == "red"
            pygame.draw.rect(
                screen,
                SELECTED if red_selected else RED_COLOR,
                red_rect,
                border_radius=8
            )
            red_text = font.render("RED", True, WHITE)
            screen.blit(
                red_text,
                (
                    red_rect.centerx - red_text.get_width() // 2,
                    red_rect.centery - red_text.get_height() // 2
                )
            )

            # ZERO BUTTON
            zero_selected = selected_bet_type == "0"
            zero_bg = SELECTED if zero_selected else GREEN
            pygame.draw.rect(
                screen,
                zero_bg,
                zero_rect,
                border_radius=8
            )
            zero_text = font.render("0", True, WHITE)
            screen.blit(
                zero_text,
                (
                    zero_rect.centerx - zero_text.get_width() // 2,
                    zero_rect.centery - zero_text.get_height() // 2
                )
            )

            # BLACK BUTTON
            black_selected = selected_bet_type == "black"
            pygame.draw.rect(
                screen,
                SELECTED if black_selected else DARK_GRAY,
                black_rect,
                border_radius=8
            )
            black_text = font.render("BLACK", True, WHITE)
            screen.blit(
                black_text,
                (
                    black_rect.centerx - black_text.get_width() // 2,
                    black_rect.centery - black_text.get_height() // 2
                )
            )

            # NUMBER GRID
            for number, rect in layout["number_rects"]:
                value = int(number)
                if value in RED:
                    bg = (180, 40, 40)
                elif value in BLACK:
                    bg = (40, 40, 40)
                else:
                    bg = (0, 140, 0)

                if selected_bet_type == number:
                    pygame.draw.rect(screen, SELECTED, rect.inflate(8, 8), border_radius=8)

                pygame.draw.rect(screen, bg, rect, border_radius=6)
                pygame.draw.rect(screen, WHITE, rect, 2, border_radius=6)

                txt = font.render(number, True, WHITE)
                screen.blit(
                    txt,
                    (
                        rect.centerx - txt.get_width() // 2,
                        rect.centery - txt.get_height() // 2
                    )
                )

            # BET INPUT
            border_color = GOLD if typing_amount else WHITE
            pygame.draw.rect(screen, BLACK_COLOR, input_rect, border_radius=6)
            pygame.draw.rect(screen, border_color, input_rect, 2, border_radius=6)
            amount_surface = font.render(f"${bet_amount_input}", True, WHITE)
            screen.blit(amount_surface, (input_rect.x + 15, input_rect.y + (input_rect.height - amount_surface.get_height()) // 2))

            if selected_bet_type and placed_chips:
                placed_amount = sum(
                    chip["value"] for chip in placed_chips if chip.get("bet_type") == selected_bet_type
                )
                if placed_amount > 0:
                    placed_surface = font.render(
                        f"Placed on {selected_bet_type}: ${placed_amount}", True, WHITE
                    )
                    screen.blit(placed_surface, (menu_rect.left + 60, confirm_rect.top - 140))
                else:
                    amount_value = f"${bet_amount_input}" if bet_amount_input else "$0"
                    amount_surface = font.render(f"Bet Amount: {amount_value}", True, WHITE)
                    screen.blit(amount_surface, (menu_rect.left + 60, confirm_rect.top - 140))
            else:
                placed_amount = sum(chip["value"] for chip in placed_chips)
                if placed_amount > 0:
                    placed_surface = font.render(f"Placed Chips: ${placed_amount}", True, WHITE)
                    screen.blit(placed_surface, (menu_rect.left + 60, confirm_rect.top - 140))
                else:
                    amount_value = f"${bet_amount_input}" if bet_amount_input else "$0"
                    amount_surface = font.render(f"Bet Amount: {amount_value}", True, WHITE)
                    screen.blit(amount_surface, (menu_rect.left + 60, confirm_rect.top - 140))

            chance_text = get_bet_chance_text(selected_bet_type)
            if chance_text:
                chance_surface = font.render(chance_text, True, WHITE)
                screen.blit(chance_surface, (menu_rect.left + 60, confirm_rect.top - 40))

            # CONFIRM BUTTON
            pygame.draw.rect(screen, GREEN, confirm_rect, border_radius=8)
            confirm_text = font.render("CONFIRM", True, WHITE)
            screen.blit(
                confirm_text,
                (
                    confirm_rect.centerx - confirm_text.get_width() // 2,
                    confirm_rect.centery - confirm_text.get_height() // 2
                )
            )

    elif state == GAME_OVER:
        screen.blit(pygame.transform.scale(game_over_bg, (WIDTH, HEIGHT)), (0, 0))
        title = title_font.render("You Lose. Skill Issue", True, WHITE)
        screen.blit(title, ((WIDTH - title.get_width()) // 2, 120))
        game_over_button = get_bottom_button()
        draw_button("Return to Main", game_over_button, game_over_button.collidepoint(mouse_pos))

    elif state == VICTORY:
        screen.blit(pygame.transform.scale(victory_bg, (WIDTH, HEIGHT)), (0, 0))
        victory_button = get_bottom_button()
        draw_button("Return to Main", victory_button, victory_button.collidepoint(mouse_pos))

        message = "You are kicked out due to too much luck. Cheating?"
        victory_font = pygame.font.SysFont("arialblack", 40)
        message_surface = victory_font.render(message, True, (0, 255, 120))
        message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT - 750))
        screen.blit(message_surface, message_rect)

    pygame.display.flip()
    clock.tick(60)