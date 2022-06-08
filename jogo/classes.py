import pygame
from animations import import_folder
from level_layout import screen_height,screen_width,tile_size,vertical_tile_number

#classe para os blocos
class Tile(pygame.sprite.Sprite):
    def __init__(self,size,x,y):
        super().__init__()
        self.image = pygame.Surface((size,size))
        self.rect = self.image.get_rect(topleft = (x,y))
    
    def update(self,shift):
        self.rect.x += shift


    def update(self, x_shift):
        self.rect.x += x_shift
    
#classe para o jogador
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, surface):
        self.import_character_animation()
        self.frame_index = 0
        self.animation_speed = 0.15
        super().__init__()
        idle = self.animations['idle']
        self.image = idle[self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)

        # movimento do player
        self.direction = pygame.math.Vector2(0,0)
        self.speed = 4
        self.gravity = 0.8
        self.jump_speed = -20

        # estado do jogador
        self.status = 'idle'
        self.olhando_frente = True
        self.on_ground = False
        self.on_celling = False
        self.on_right = False
        self.on_left = False

    def import_character_animation(self):
        character_path = r'./graficos/player/'
        self.animations = {'idle': [], 'andar': [], 'pulo': [], 'cair': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed

        if self.frame_index >= len(animation):
            self.frame_index = 0
        
        image = animation[int(self.frame_index)]
        if self.olhando_frente:
            self.image = image
        else:
            virar_jogador = pygame.transform.flip(image,True,False)
            self.image = virar_jogador

        if self.on_ground and self.on_right:
            self.rect = self.image.get_rect(bottomright = self.rect.bottomright)
        elif self.on_ground and self.on_left:
            self.rect = self.image.get_rect(bottomleft = self.rect.bottomleft)
        elif self.on_ground:
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
        elif self.on_celling and self.on_right:
            self.rect = self.image.get_rect(topright = self.rect.topright)
        elif self.on_celling and self.on_left:
            self.rect = self.image.get_rect(topleft = self.rect.topleft)
        elif self.on_celling:
            self.rect = self.image.get_rect(midtop = self.rect.midtop)

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.olhando_frente = True
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.olhando_frente = False
        else:
            self.direction.x = 0

        if (keys[pygame.K_UP] or keys[pygame.K_SPACE])  and self.on_ground:
            self.pulo()
    
    def get_status(self):
        if self.direction.y < 0:
            self.status = 'pulo'
        elif self.direction.y > 1:
            self.status = 'cair'
        else:
            if self.direction.x != 0:
                self.status = 'andar'
            else:
                self.status = 'idle'

    def gravidade(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def pulo(self):
        self.direction.y = self.jump_speed

    def update(self):
        self.get_input()
        self.get_status()
        self.animate()


class StaticTile(Tile):
    def __init__(self,size,x,y,surface):
        super().__init__(size,x,y)
        self.image = surface

class AnimatesTile(Tile):
    def __init__(self, size, x, y, path):
        super().__init__(size, x, y)
        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

    def animate(self):
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self,shift):
        self.animate()
        self.rect.x += shift

class Enemy(AnimatesTile):
    def __init__(self, size, x, y):
        super().__init__(size, x, y, './graficos/tiles/enemy')
        self.speed = 3

    def move(self):
        self.rect.x += self.speed

    def reverse_image(self):
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image,True,False)
    
    def reverse(self):
        self.speed *= -1

    def update(self, shift):
        self.rect.x += shift
        self.animate()
        self.move()
        self.reverse_image()

class Fundo:
    def __init__(self,horizon):
        self.horizon = horizon

        self.fundo = pygame.image.load('./graficos/background.png').convert()
        self.fundo = pygame.transform.scale(self.fundo,(screen_width,tile_size))

    def draw(self,surface):
        for row in range(vertical_tile_number):
            y = row * tile_size
            surface.blit(self.fundo,(0,y))