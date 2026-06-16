import pygame
import random
import math


pygame.init()
pygame.mixer.init()
width, height = 1000, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Seoul After Dark")
clock = pygame.time.Clock()


font = pygame.font.SysFont("Arial", 20, bold=True)
score_font = pygame.font.SysFont("Arial", 26, bold=True)
menu_font = pygame.font.SysFont("Courier New", 28, bold=True)
title_font = pygame.font.SysFont("Impact", 72)
gameover_font = pygame.font.SysFont("Impact", 90)


asset_path = "assets/"


def load_and_clean_image(path, w, h, transparent_png=False):
    try:
        if transparent_png:
            image = pygame.image.load(path).convert_alpha()
        else:
            image = pygame.image.load(path).convert()
        image = pygame.transform.scale(image, (w, h))
        return image
    except Exception:
        surf = pygame.Surface((w, h))
        surf.fill((255, 0, 255))
        return surf



try:
    bell_sound = pygame.mixer.Sound(asset_path + "sounds/bell.wav")
    pygame.mixer.music.load(asset_path + "sounds/city.mp3")
    pygame.mixer.music.set_volume(0.4)  # Громкость от 0.0 до 1.0 (0.4 — чтобы не глушила звуки игры)
    pygame.mixer.music.play(-1)  # Параметр -1 заставляет музыку играть бесконечно по кругу
    has_music = True
    has_sound = True
except Exception:
    has_music = False
    has_sound = False


bg_texture = load_and_clean_image(asset_path + "background/pixel_bg.jpg", width, height)

try:
    table_texture = pygame.image.load(asset_path + "background/table.jpg").convert()
    table_texture = pygame.transform.scale(table_texture, (width, 160))
    has_table_img = True
except Exception:
    has_table_img = False

dish_images = {
    "Кимпаб": asset_path + "ingredients/dish.png",
    "Пибимпаб": asset_path + "ingredients/dish_bibimbap.png"
}


recipes = {
    "Кимпаб": [0, 1, 2],
    "Пибимпаб": [3, 4, 2]
}


char_data = [
    {
        "name": "Со Мунджо",
        "image": asset_path + "characters/mon_char.png",
        "hi": [
            "Выглядит аппетитно... Вы ведь положите туда \nсамое свежее мясо, верно?",
            "Мне нравится это место. Здесь можно \nнаблюдать за людьми, пока они ждут"
        ],
        "bye": [
            "Это было... уникальное послевкусие. \nЯ сделаю вас своим особым гостем",
            "У вас талант. Я бы хотел изучить \nвас поближе в своей клинике"
        ],
        "fail": "Какое разочарование...\nА я думал, мы станем друзьями."
    },
    {
        "name": "Чон У",
        "image": asset_path + "characters/chon_char.png",
        "hi": [
            "Быстрее, пожалуйста... мне нужно вернуться \nк работе, пока я не сошел с ума",
            "В этом районе все такие странные... \nхотя бы еда здесь нормальная?"
        ],
        "bye": [
            "Спасибо. Кажется, это единственное \nнормальное событие за весь мой день",
            "Вкусно. Но почему тот человек в \nуглу так на меня смотрит?"
        ],
        "fail": "Я больше не могу здесь находиться... \nэто место сводит меня с ума!"
    }
]


ing_data = [
    {"id": 0, "image": asset_path + "ingredients/ing1.png", "pos": (15, 480)},
    {"id": 1, "image": asset_path + "ingredients/ing2.png", "pos": (95, 480)},
    {"id": 2, "image": asset_path + "ingredients/ing3.png", "pos": (175, 480)},
    {"id": 3, "image": asset_path + "ingredients/ing4.png", "pos": (255, 480)},
    {"id": 4, "image": asset_path + "ingredients/ing5.png", "pos": (335, 480)},
]

for ing in ing_data:
    ing["loaded_img"] = load_and_clean_image(ing["image"], 80, 80, transparent_png=True)
    ing["small_img"] = load_and_clean_image(ing["image"], 50, 50, transparent_png=True)


class Guest:
    def __init__(self):
        data = random.choice(char_data)
        image_path = data["image"]
        self.image = load_and_clean_image(image_path, 350, 380, transparent_png=True)
        self.rect = self.image.get_rect(midbottom=(1150, height - 140))
        self.target_x = 500
        self.state = "incoming"

        self.name = data["name"]
        self.base_phrase = random.choice(data["hi"])
        self.bye_phrase = random.choice(data["bye"])
        self.fail_phrase = data["fail"]

        self.requested_dish = random.choice(list(recipes.keys()))
        self.phrase = f"{self.base_phrase}\nПриготовь мне {self.requested_dish}."
        self.max_patience = 900
        self.patience = self.max_patience
        if has_sound and game_state == "game":
            bell_sound.play()
    def update(self):
        if self.state == "incoming":
            if self.rect.centerx > self.target_x:
                self.rect.x -= 6
            else:
                self.state = "waiting"
        elif self.state == "waiting":
            self.patience -= 1
            if self.patience <= 0:
                self.state = "angry_leaving"
                global score, lives, game_state
                score = max(0, score - 5)
                lives -= 1  # Теряем жизнь, если гость ушел злым
                if lives <= 0:
                    game_state = "game_over"  # Если жизней нет — проигрыш
        elif self.state in ["leaving", "angry_leaving"]:
            self.rect.x -= 8
            if self.rect.right < 0:
                return True
        return False
    def draw_patience_bar(self):
        if self.state == "waiting":
            bar_width = 160
            bar_height = 8
            x = self.rect.centerx - (bar_width // 2)
            y = self.rect.top - 125
            pct = self.patience / self.max_patience
            if pct > 0.5:
                color = (50, 255, 50)
            elif pct > 0.25:
                color = (255, 165, 0)
            else:
                color = (255, 50, 50)
            pygame.draw.rect(screen, (50, 50, 50), (x, y, bar_width, bar_height))
            pygame.draw.rect(screen, color, (x, y, int(bar_width * pct), bar_height))


def draw_speech_bubble(text, speaker_name, char_rect):
    box_width = 580
    box_height = 115
    box_x = char_rect.centerx - (box_width // 2)
    box_y = char_rect.top - box_height - 10
    box_x = max(10, min(box_x, width - box_width - 10))
    box_y = max(45, box_y)
    bubble_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    bubble_surface.fill((20, 20, 20, 220))
    screen.blit(bubble_surface, (box_x, box_y))
    border_color = (255, 75, 75) if current_guest.state != "angry_leaving" else (139, 0, 0)
    pygame.draw.rect(screen, border_color, (box_x, box_y, box_width, box_height), 2, border_radius=4)
    name_img = font.render(f"[{speaker_name}]:", True, (255, 215, 0))
    screen.blit(name_img, (box_x + 15, box_y + 10))
    if "\n" in text:
        line1, line2 = text.split("\n", 1)
    else:
        words = text.split(' ')
        line1, line2 = "", ""
        for word in words:
            if font.size(line1 + word)[0] < box_width - 40 and not line2:
                line1 += word + " "
            else:
                line2 += word + " "
    text_img1 = font.render(line1.strip(), True, (255, 255, 255))
    screen.blit(text_img1, (box_x + 15, box_y + 38))
    if line2:
        text_img2 = font.render(line2.strip(), True, (255, 255, 255))
        screen.blit(text_img2, (box_x + 15, box_y + 64))



game_state = "menu"
current_guest = Guest()
choosen_ingredients = []
dish_ready = False
score = 0
lives = 3
wrong_dish_timer = 0
pulse_time = 0


start_btn_rect = pygame.Rect(width // 2 - 125, 300, 250, 55)
exit_btn_rect = pygame.Rect(width // 2 - 125, 390, 250, 55)
menu_btn_rect = pygame.Rect(width // 2 - 150, 380, 300, 55)

running = True
while running:
    mx, my = pygame.mouse.get_pos()
    if game_state == "menu":
        screen.fill((15, 15, 22))

        pulse_time += 0.05
        title_color = (255, 43, 97)

        title_text = title_font.render("SEOUL AFTER DARK", True, title_color)
        title_rect = title_text.get_rect(center=(width // 2, 160))
        screen.blit(title_text, title_rect)

        if start_btn_rect.collidepoint(mx, my):
            pygame.draw.rect(screen, (255, 43, 97), start_btn_rect, border_radius=8)
            start_txt = menu_font.render("СТАРТ", True, (255, 255, 255))
        else:
            pygame.draw.rect(screen, (40, 20, 30), start_btn_rect, border_radius=8)
            pygame.draw.rect(screen, (150, 30, 60), start_btn_rect, 2, border_radius=8)
            start_txt = menu_font.render("СТАРТ", True, (200, 200, 200))

        if exit_btn_rect.collidepoint(mx, my):
            pygame.draw.rect(screen, (255, 43, 97), exit_btn_rect, border_radius=8)
            exit_txt = menu_font.render("ВЫХОД", True, (255, 255, 255))
        else:
            pygame.draw.rect(screen, (40, 20, 30), exit_btn_rect, border_radius=8)
            pygame.draw.rect(screen, (150, 30, 60), exit_btn_rect, 2, border_radius=8)
            exit_txt = menu_font.render("ВЫХОД", True, (200, 200, 200))

        screen.blit(start_txt, start_txt.get_rect(center=start_btn_rect.center))
        screen.blit(exit_txt, exit_txt.get_rect(center=exit_btn_rect.center))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn_rect.collidepoint(mx, my):
                    game_state = "game"
                    lives = 3
                    score = 0
                    choosen_ingredients = []
                    dish_ready = False
                    current_guest = Guest()
                if exit_btn_rect.collidepoint(mx, my):
                    running = False


    elif game_state == "game":
        screen.blit(bg_texture, (0, 0))
        screen.blit(current_guest.image, current_guest.rect)

        if current_guest.state == "waiting":
            draw_speech_bubble(current_guest.phrase, current_guest.name, current_guest.rect)
            current_guest.draw_patience_bar()
        elif current_guest.state == "leaving":
            draw_speech_bubble(current_guest.bye_phrase, current_guest.name, current_guest.rect)
        elif current_guest.state == "angry_leaving":
            draw_speech_bubble(current_guest.fail_phrase, current_guest.name, current_guest.rect)


        pygame.draw.rect(screen, (36, 36, 36), (0, 0, width, 40))


        score_text = score_font.render(f"Очки: {score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 5))


        lives_text = score_font.render(f"Клиенты до вызова полиции: {'❤️ ' * lives}", True, (255, 80, 80))
        screen.blit(lives_text, (width - lives_text.get_width() - 20, 5))


        if has_table_img:
            screen.blit(table_texture, (0, height - 160))
        else:
            pygame.draw.rect(screen, (45, 45, 48), (0, height - 160, width, 160))
            pygame.draw.rect(screen, (70, 70, 75), (0, height - 160, width, 6))


        for ing in ing_data:
            screen.blit(ing["loaded_img"], ing["pos"])


        pygame.draw.rect(screen, (90, 50, 20), (600, 460, 350, 110), border_radius=5)

        for i, ing_id in enumerate(choosen_ingredients):
            small_ing = ing_data[ing_id]["small_img"]
            screen.blit(small_ing, (620 + (i * 60), 490))
            cross_img = font.render("x", True, (200, 50, 50))
            screen.blit(cross_img, (640 + (i * 60), 465))

        if wrong_dish_timer > 0:
            error_text = font.render("Неправильный рецепт! Сборка сброшена!", True, (255, 50, 50))
            screen.blit(error_text, (610, 425))
            wrong_dish_timer -= 1

        if dish_ready:
            try:
                if choosen_ingredients[0] in [0, 1, 2]:
                    current_dish_path = asset_path + "ingredients/dish.png"
                else:
                    current_dish_path = asset_path + "ingredients/dish_bibimpab.png"
                final_dish = load_and_clean_image(current_dish_path, 90, 90, transparent_png=True)
                screen.blit(final_dish, (840, 470))
            except Exception as e:
                surf = pygame.Surface((90, 90))
                surf.fill((255, 0, 255))
                screen.blit(surf, (840, 470))

            ready_text = font.render("Кликни на гостя!", True, (50, 255, 50))
            screen.blit(ready_text, (620, 540))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if current_guest.state == "waiting" and not dish_ready:
                    for i, ing in enumerate(ing_data):
                        center_x = ing["pos"][0] + 40
                        center_y = ing["pos"][1] + 40

                        dist = ((mx - center_x) ** 2 + (my - center_y) ** 2) ** 0.5

                        if dist < 40 and len(choosen_ingredients) < 3:
                            choosen_ingredients.append(i)
                            if len(choosen_ingredients) == 3:
                                dish_ready = True

                if dish_ready and current_guest.rect.collidepoint(mx, my) and current_guest.state == "waiting":
                    correct_recipe = recipes[current_guest.requested_dish]

                    if sorted(choosen_ingredients) == sorted(correct_recipe):
                        current_guest.state = "leaving"
                        score += 10
                        dish_ready = False
                        choosen_ingredients = []
                    else:
                        dish_ready = False
                        choosen_ingredients = []
                        wrong_dish_timer = 120

        if current_guest.update():

            if game_state == "game":
                current_guest = Guest()


    elif game_state == "game_over":
        screen.fill((10, 5, 5))

        # Надпись конца игры
        go_text = gameover_font.render("ИГРА ОКОНЧЕНА", True, (200, 30, 30))
        go_rect = go_text.get_rect(center=(width // 2, 180))
        screen.blit(go_text, go_rect)

        # Вывод финального счета
        final_score_txt = menu_font.render(f"Ваш итоговый счет: {score} очков", True, (255, 255, 255))
        screen.blit(final_score_txt, final_score_txt.get_rect(center=(width // 2, 280)))

        # Кнопка возврата в меню
        if menu_btn_rect.collidepoint(mx, my):
            pygame.draw.rect(screen, (200, 30, 30), menu_btn_rect, border_radius=8)
            menu_btn_txt = menu_font.render("В ГЛАВНОЕ МЕНЮ", True, (255, 255, 255))
        else:
            pygame.draw.rect(screen, (30, 10, 10), menu_btn_rect, border_radius=8)
            pygame.draw.rect(screen, (120, 20, 20), menu_btn_rect, 2, border_radius=8)
            menu_btn_txt = menu_font.render("В ГЛАВНОЕ МЕНЮ", True, (180, 180, 180))

        screen.blit(menu_btn_txt, menu_btn_txt.get_rect(center=menu_btn_rect.center))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_btn_rect.collidepoint(mx, my):
                    game_state = "menu"

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
