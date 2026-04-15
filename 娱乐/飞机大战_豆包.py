import pygame
import random
import sys

pygame.init()
WIDTH, HEIGHT = 480, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("飞机大战 - 终极完整版")
clock = pygame.time.Clock()
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 220, 50)
BLUE = (50, 120, 255)
CYAN = (0, 200, 255)
YELLOW = (255, 220, 50)
PURPLE = (150, 80, 255)
GRAY = (40, 40, 40)

stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 2)) for _ in range(50)]

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 70), pygame.SRCALPHA)
        
        pygame.draw.polygon(self.image, (0, 170, 255), [(30, 0), (0, 70), (60, 70)])
        pygame.draw.polygon(self.image, (0, 220, 255), [(30, 10), (10, 60), (50, 60)])
        pygame.draw.polygon(self.image, (0, 130, 220), [(10, 40), (-5, 60), (25, 50)])
        pygame.draw.polygon(self.image, (0, 130, 220), [(50, 40), (65, 60), (35, 50)])
        pygame.draw.circle(self.image, WHITE, (30, 40), 7)
        pygame.draw.circle(self.image, (0, 90, 180), (30, 40), 5)
        
        pygame.draw.polygon(self.image, (255, 150, 0), [(22, 65), (30, 75), (38, 65)])
        
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH//2
        self.rect.bottom = HEIGHT - 20
        self.life = 3
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.bullet_width = 6
        self.invulnerable = False
        self.invul_time = 0

    def update(self):
        x, y = pygame.mouse.get_pos()
        self.rect.centerx = x
        self.rect.centery = y
        self.rect.clamp_ip(screen.get_rect())
        if self.invulnerable and pygame.time.get_ticks() - self.invul_time > 1500:
            self.invulnerable = False

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            b = Bullet(self.rect.centerx, self.rect.top, self.bullet_width)
            all_sprites.add(b)
            player_bullets.add(b)

    def hurt(self):
        if not self.invulnerable:
            self.life -= 1
            self.invulnerable = True
            self.invul_time = pygame.time.get_ticks()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, w):
        super().__init__()
        self.image = pygame.Surface((w, 18), pygame.SRCALPHA)
        pygame.draw.rect(self.image, YELLOW, (0, 0, w, 18), border_radius=3)
        pygame.draw.rect(self.image, WHITE, (w//3, 2, w//3, 14), border_radius=2)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -12

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, level=1):
        super().__init__()
        self.image = pygame.Surface((50, 45), pygame.SRCALPHA)
        
        pygame.draw.polygon(self.image, (255, 40, 40), [(25, 0), (0, 45), (50, 45)])
        pygame.draw.polygon(self.image, (200, 20, 20), [(25, 8), (6, 40), (44, 40)])
        pygame.draw.polygon(self.image, (220, 30, 30), [(0, 25), (-8, 40), (10, 35)])
        pygame.draw.polygon(self.image, (220, 30, 30), [(50, 25), (58, 40), (40, 35)])
        pygame.draw.circle(self.image, BLACK, (25, 25), 5)
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.w)
        self.rect.y = random.randint(-120, -30)
        self.speed = random.randint(2, 4 + level)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 12), pygame.SRCALPHA)
        pygame.draw.rect(self.image, WHITE, (0, 0, 5, 12), border_radius=2)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 6

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Buff(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = random.choice(["life", "speed", "width"])
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        c = {"life": GREEN, "speed": YELLOW, "width": CYAN}[self.type]
        pygame.draw.circle(self.image, c, (16, 16), 14)
        pygame.draw.circle(self.image, WHITE, (16, 16), 8, 2)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH-32)
        self.rect.y = -40
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 100, 0), (20, 20), 20)
        pygame.draw.circle(self.image, (255, 200, 0), (20, 20), 12)
        pygame.draw.circle(self.image, WHITE, (20, 20), 5)
        self.rect = self.image.get_rect(center=center)
        self.timer = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.timer > 100:
            self.kill()

all_sprites = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
buffs = pygame.sprite.Group()
explosions = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

def init_level(level):
    global enemy_spawn_rate, enemy_shoot_rate
    if level == 1:
        enemy_spawn_rate, enemy_shoot_rate = 100, 130
    elif level == 2:
        enemy_spawn_rate, enemy_shoot_rate = 65, 95
    else:
        enemy_spawn_rate, enemy_shoot_rate = 40, 65
    player.life = 3
    player.shoot_delay = 250
    player.bullet_width = 6
    enemies.empty()
    enemy_bullets.empty()
    buffs.empty()

def draw_text(text, size, x, y, color=WHITE, anchor="center"):
    font = pygame.font.Font(None, size)
    surf = font.render(text, True, color)
    rect = surf.get_rect(**{anchor: (x, y)})
    screen.blit(surf, rect)

def draw_bg():
    screen.fill(BLACK)
    global stars
    new_stars = []
    for (x, y, s) in stars:
        y += s
        if y > HEIGHT:
            y = 0
            x = random.randint(0, WIDTH)
        pygame.draw.circle(screen, WHITE, (x, y), s)
        new_stars.append((x, y, s))
    stars = new_stars

def draw_ui():
    s = pygame.Surface((WIDTH, 40))
    s.set_alpha(180)
    s.fill(GRAY)
    screen.blit(s, (0, 0))
    draw_text(f"第{level}关", 28, WIDTH//2, 20, CYAN)
    draw_text(f"生命: {player.life}", 26, 10, 20, GREEN, "midleft")
    draw_text(f"分数: {score}", 26, WIDTH-10, 20, YELLOW, "midright")
    
    pygame.draw.rect(screen, (50,50,50), (10, 30, 100, 8))
    current = min(player.life / 3, 1)
    pygame.draw.rect(screen, GREEN, (10, 30, 100 * current, 8))

def game():
    global level, score
    level = 1
    score = 0
    init_level(level)
    running = True
    game_over = False

    while running:
        clock.tick(FPS)
        draw_bg()

        if not game_over:
            all_sprites.update()
            explosions.update()

            if random.randint(0, enemy_spawn_rate) == 0:
                e = Enemy(level)
                all_sprites.add(e)
                enemies.add(e)

            for e in enemies:
                if random.randint(0, enemy_shoot_rate) == 0:
                    eb = EnemyBullet(e.rect.centerx, e.rect.bottom)
                    all_sprites.add(eb)
                    enemy_bullets.add(eb)

            if random.randint(0, 450) == 0:
                b = Buff()
                all_sprites.add(b)
                buffs.add(b)

            if pygame.mouse.get_pressed()[0]:
                player.shoot()

            hits = pygame.sprite.groupcollide(enemies, player_bullets, True, True)
            for hit in hits:
                score += 10
                ex = Explosion(hit.rect.center)
                all_sprites.add(ex)
                explosions.add(ex)

            for hit in pygame.sprite.spritecollide(player, enemies, True):
                player.hurt()
                ex = Explosion(hit.rect.center)
                all_sprites.add(ex)
                explosions.add(ex)

            for hit in pygame.sprite.spritecollide(player, enemy_bullets, True):
                player.hurt()

            for b in pygame.sprite.spritecollide(player, buffs, True):
                if b.type == "life":
                    player.life += 1
                elif b.type == "speed":
                    player.shoot_delay = max(70, player.shoot_delay - 40)
                elif b.type == "width":
                    player.bullet_width = min(22, player.bullet_width + 4)

            if score >= level * 100:
                level += 1
                if level > 3:
                    draw_text("恭喜通关！", 70, WIDTH//2, HEIGHT//2, GREEN)
                    pygame.display.flip()
                    pygame.time.delay(3000)
                    running = False
                else:
                    init_level(level)
                    draw_text(f"第{level}关", 90, WIDTH//2, HEIGHT//2, YELLOW)
                    pygame.display.flip()
                    pygame.time.delay(1500)

            if player.life <= 0:
                game_over = True

        all_sprites.draw(screen)
        explosions.draw(screen)
        draw_ui()

        if game_over:
            s = pygame.Surface((WIDTH, HEIGHT))
            s.set_alpha(180)
            s.fill(BLACK)
            screen.blit(s, (0, 0))
            draw_text("游戏结束", 80, WIDTH//2, HEIGHT//2-40, RED)
            draw_text("按 R 重新开始", 40, WIDTH//2, HEIGHT//2+30, WHITE)
            if pygame.key.get_pressed()[pygame.K_r]:
                game()
                return

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game()