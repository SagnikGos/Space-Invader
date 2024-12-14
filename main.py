import pygame 
from os.path import join
from random import randint, uniform

from pygame.sprite import Group

#classes
class player(pygame.sprite.Sprite):
    def __init__(self,groups): #dunder init function
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH/2,WINDOW_HEIGHT/2))
        self.direction = pygame.Vector2()
        self.speed = 30

        #cooldown mechanic
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.laser_shoot_cooldown = 200


    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            
            if current_time - self.laser_shoot_time >= self.laser_shoot_cooldown:
                self.can_shoot = True


    def update(self,dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction #truthy & falsy values
        #god statement
        self.rect.center += self.direction*self.speed*dt

        laser_keys = pygame.key.get_just_pressed()
        if laser_keys[pygame.K_j] and self.can_shoot:
            laser(laser_surf, (all_sprites, laser_sprites), self.rect.midtop)
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        
        self.laser_timer()

class star(pygame.sprite.Sprite):
    def __init__(self,groups,surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH), randint(0,WINDOW_HEIGHT)))

class laser(pygame.sprite.Sprite):
    def __init__(self,surf,groups,pos):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)

    def update(self,dt):
        self.rect.centery -= 70*dt
        if self.rect.bottom < 0:
            self.kill()
            

class meteor(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.direction = pygame.Vector2(uniform(-0.5,0.5),1)
        self.speed = randint(40, 70)
        self.rotation_speed = randint(40,80)
        self.rotation = 0

    def update(self, dt):
        self.rect.center += self.direction*self.speed*dt
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()
        self.rotation += self.rotation_speed*dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frame = frames
        self.frame_index = 0
        self.image = self.frame[self.frame_index]
        self.rect = self.image.get_frect(center = pos)

    def update(self, dt):
        self.frame_index += 7*dt
        if self.frame_index < len(self.frame):
            self.image = self.frame[int(self.frame_index)]
        else:
            self.kill()
            
def collisions():
        
        collision_main = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
        if collision_main:
            damage_sound.play()
            game_over_screen()
            


        for laser in laser_sprites:
            collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
            if collided_sprites:
                laser.kill()
                AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
                explosion_sound.play()
                


def Display_Score():
    current_score = pygame.time.get_ticks() // 300
    text_surf = font.render(str(current_score), True,(240, 240, 240) )
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH/2, WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10).move(0,-8), 5, 10)

def game_over_screen():
    display_surface.fill('black')
    game_over_text = font.render("Game Over", True, 'white')
    display_surface.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, WINDOW_HEIGHT // 2 - 100))

    restart_text = font.render("Press Q to Quit", True, 'white')
    display_surface.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 + 50))

    pygame.display.flip()

    # Wait for input to restart or quit
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                
            if event.type == pygame.KEYDOWN:
               
                if event.key == pygame.K_q:  # Quit
                    pygame.quit()
                    
def main_game():
    running = True
    dt = clock.tick() /1000
    while running:
        #event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == meteor_event:
                x = randint(0,WINDOW_WIDTH)
                y = randint(-200,-100)
                meteor((all_sprites, meteor_sprites), meteor_surf, (x,y))

    
        all_sprites.update(dt) #should be called before drawing anything
    
        #draw the game
        display_surface.fill("purple")  
        collisions()
        Display_Score()
        all_sprites.draw(display_surface)
        pygame.display.update()


#initialising pygame
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720

#set display
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

#set display title
pygame.display.set_caption("Space Shooter")

#clock
clock = pygame.time.Clock()

#imports
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 50)
explosion_frames = [(pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha()) for i in range(21)]
laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.1)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
explosion_sound.set_volume(0.1)
damage_sound = pygame.mixer.Sound(join('audio', 'damage.ogg'))
damage_sound.set_volume(0.3)
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.1)
game_music.play()



#all sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
for i in range(30):
    star(all_sprites, star_surf)
player = player(all_sprites)


meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 300)

   
# Make the display work
running = True
dt = clock.tick() /1000
while running:
    #event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x = randint(0,WINDOW_WIDTH)
            y = randint(-200,-100)
            meteor((all_sprites, meteor_sprites), meteor_surf, (x,y))

    
    all_sprites.update(dt) #should be called before drawing anything
    
    #draw the game
    display_surface.fill("purple")  
    collisions()
    Display_Score()
    all_sprites.draw(display_surface)
    pygame.display.update()
# main_game()

pygame.quit()
