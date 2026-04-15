import pygame
import random
import math
import os

# 初始化Pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 750
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

# 屏幕设置
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("飞机大战")
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40))
        self.image.fill(GREEN)
        pygame.draw.polygon(self.image, (0, 200, 0), [(25, 0), (0, 40), (50, 40)])
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed_x = 0
        self.speed_y = 0
        self.health = 3
        self.max_health = 3
        self.attack_speed = 20  # 射击间隔帧数
        self.shoot_timer = 0
        self.bullet_width = 5
        
    def update(self):
        # 更新位置
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # 边界检查
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0
            
        # 射击计时器
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
    
    def shoot(self):
        if self.shoot_timer == 0:
            self.shoot_timer = self.attack_speed
            return True
        return False
    
    def draw_health_bar(self, surface):
        bar_length = 100
        bar_height = 10
        fill = (self.health / self.max_health) * bar_length
        outline_rect = pygame.Rect(10, 10, bar_length, bar_height)
        fill_rect = pygame.Rect(10, 10, fill, bar_height)
        pygame.draw.rect(surface, RED, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 2)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, level=1):
        super().__init__()
        size = random.randint(30, 50)
        self.image = pygame.Surface((size, size))
        color = (random.randint(100, 255), random.randint(0, 100), random.randint(0, 100))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 3) + level
        self.speedx = random.randrange(-2, 2)
        
    def update(self, current_level=1):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT + 10 or self.rect.left < -25 or self.rect.right > SCREEN_WIDTH + 20:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 3) + (current_level - 1)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, width, speed=-10):
        super().__init__()
        self.image = pygame.Surface((width, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = speed
        
    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Buff(pygame.sprite.Sprite):
    def __init__(self, buff_type):
        super().__init__()
        self.buff_type = buff_type  # 'health', 'attack_speed', 'bullet_width'
        self.image = pygame.Surface((20, 20))
        if self.buff_type == 'health':
            self.image.fill(RED)
        elif self.buff_type == 'attack_speed':
            self.image.fill(BLUE)
        else:  # bullet_width
            self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = 3
        
    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT + 10:
            self.kill()

class Game:
    def __init__(self):
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.buffs = pygame.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)
        
        self.level = 1
        self.score = 0
        try:
            # 尝试加载默认字体
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
        except:
            # 如果失败则使用默认字体
            self.font = pygame.font.SysFont('arial', 36)
            self.small_font = pygame.font.SysFont('arial', 24)
        
        self.game_over = False
        self.level_complete = False
        self.spawn_timer = 0
        self.buff_spawn_timer = 0
        
    def spawn_enemies(self):
        if self.spawn_timer <= 0:
            for i in range(self.level):
                enemy = Enemy(self.level)
                self.all_sprites.add(enemy)
                self.enemies.add(enemy)
            self.spawn_timer = max(30, 60 - self.level*10)  # 调整敌人生成频率
        else:
            self.spawn_timer -= 1
            
    def spawn_buffs(self):
        if self.buff_spawn_timer <= 0 and random.random() < 0.005:  # 0.5% 概率生成buff
            buff_types = ['health', 'attack_speed', 'bullet_width']
            buff = Buff(random.choice(buff_types))
            self.all_sprites.add(buff)
            self.buffs.add(buff)
            self.buff_spawn_timer = 300  # 至少300帧后才可能生成下一个buff
        else:
            self.buff_spawn_timer -= 1
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over or self.level_complete:
                    # 重启游戏
                    self.__init__()
            elif event.type == pygame.MOUSEMOTION:
                if not self.game_over and not self.level_complete:
                    # 鼠标拖动控制飞机
                    pos = pygame.mouse.get_pos()
                    self.player.rect.centerx = pos[0]
                    self.player.rect.centery = pos[1]
        
        # 持续射击
        if not self.game_over and not self.level_complete:
            if self.player.shoot():
                bullet = Bullet(self.player.rect.centerx, self.player.rect.top, 
                               self.player.bullet_width)
                self.all_sprites.add(bullet)
                self.bullets.add(bullet)
        
        return True
    
    def update(self):
        if self.game_over or self.level_complete:
            return
            
        # 更新所有精灵，传递当前关卡级别给敌人
        for sprite in self.all_sprites:
            if isinstance(sprite, Enemy):
                sprite.update(current_level=self.level)
            else:
                sprite.update()
        
        # 生成敌人和buff
        self.spawn_enemies()
        self.spawn_buffs()
        
        # 子弹与敌人碰撞检测
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
        for hit in hits:
            self.score += 10
            # 有一定概率生成新的敌人
            if random.random() < 0.3:
                new_enemy = Enemy(self.level)
                self.all_sprites.add(new_enemy)
                self.enemies.add(new_enemy)
        
        # 玩家与敌人碰撞检测
        hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
        for hit in hits:
            self.player.health -= 1
            if self.player.health <= 0:
                self.game_over = True
        
        # 玩家与buff碰撞检测
        hits = pygame.sprite.spritecollide(self.player, self.buffs, True)
        for hit in hits:
            if hit.buff_type == 'health':
                self.player.health = min(self.player.max_health, self.player.health + 1)
            elif hit.buff_type == 'attack_speed':
                self.player.attack_speed = max(5, self.player.attack_speed - 3)  # 增加攻击速度
            elif hit.buff_type == 'bullet_width':
                self.player.bullet_width = min(20, self.player.bullet_width + 2)  # 增加子弹宽度
        
        # 检查关卡完成条件
        if len(self.enemies) == 0 and self.spawn_timer <= 0:
            self.level_complete = True
            self.player.health = self.player.max_health  # 回满生命值
            if self.level < 3:
                self.level += 1
                # 清除所有精灵，准备下一关
                self.enemies.empty()
                self.bullets.empty()
                self.buffs.empty()
                self.all_sprites.empty()
                self.all_sprites.add(self.player)
    
    def draw(self):
        screen.fill(BLACK)
        
        # 绘制所有精灵
        self.all_sprites.draw(screen)
        
        # 绘制玩家血量条
        self.player.draw_health_bar(screen)
        
        # 显示分数和等级
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}/3", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH - 150, 10))
        screen.blit(level_text, (SCREEN_WIDTH - 150, 50))
        
        # 显示游戏结束或关卡完成信息
        if self.game_over:
            text = self.font.render("GAME OVER! Click to restart", True, RED)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text, text_rect)
        elif self.level_complete:
            if self.level > 3:
                text = self.font.render("YOU WIN! Click to restart", True, GREEN)
            else:
                text = self.font.render(f"LEVEL {self.level-1} COMPLETE! Click for next level", True, GREEN)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text, text_rect)
        
        # 显示操作提示
        hint_text = self.small_font.render("Move with mouse, collect buffs: Red=HP, Blue=Fire Rate, Purple=Bullet Width", True, WHITE)
        screen.blit(hint_text, (10, SCREEN_HEIGHT - 30))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            clock.tick(FPS)
            running = self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()