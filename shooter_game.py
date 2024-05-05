from pygame import *
from random import randint

def getRandomColor():
    return (randint(0, 255), randint(0, 255), randint(0, 255))

class GameSprite(sprite.Sprite):
    def __init__(self, image_, x, y, speed, width=80, height=80):
        super().__init__()
        self.image = transform.scale(image.load(image_), (width, height))
        self.rect = self.image.get_rect()        
        self.speed = speed
        self.rect.x = x
        self.rect.y = y
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))
class Player(GameSprite):
    def __init__(self, image, x, y, speed):
        super().__init__(image, x, y, speed, 60, 80)
        self.countDown = 0
        self.lifes = 3
        self.godMode = 0 
    def reduceLifes(self):
        if self.godMode == 0:
            self.lifes -= 1
            if not self.lifes:
                global finish
                finish = 2 #lose
            else:
                self.godMode = 255
    def restart(self):
        self.goStart()  
        self.lifes = 3
        self.godMode = 0      
    def update(self):
        if self.countDown:
            self.countDown -= 1
        if self.godMode:
            self.godMode -= 1
        keys = key.get_pressed()
        if keys[K_a] and self.rect.x > self.speed:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x < 1120 - self.rect.width - self.speed:
            self.rect.x += self.speed 
        if keys[K_SPACE]:
            self.fire()
    def goStart(self):
        self.rect.x, self.rect.y = (560, 720)
    def fire(self):
        if not self.countDown:
            self.countDown = 10 - score//30
            if self.countDown < 0:
                self.countDown = 0
            bullets.add(Bullet('bullet.png', self.rect.x + 25, self.rect.y))
class Enemy(GameSprite):
    def __init__(self, image, width=80, height=40):
        x = randint(0, 1040)
        y = -80
        speed = randint(2, 4)
        super().__init__(image, x, y, speed, width, height)        
    def update(self):
        self.rect.y += self.speed
        if self.rect.y >= 800:
            global unScore
            unScore += 1
            self.respawn()
    def respawn(self):
        self.rect.y = -80
        self.rect.x = randint(0, 1040)
class Bullet(GameSprite):
    def __init__(self, image, x, y):
        speed = 15
        super().__init__(image, x, y, speed, 10, 20)        
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y <= 0:
            self.kill()
class Asteroid(Enemy):
    def __init__(self, image, size=80):
        self.size = size
        super().__init__(image, self.size, self.size)
        self.respawn()
    def update(self):
        self.rect.y += self.speedY
        if self.rect.y >= 800:
            self.respawn()
        self.rect.x += self.speedX
        #self.rotate()
    def rotate(self):
        self.image = transform.rotate(self.image, 5)
    def respawn(self):
        super().respawn()
        destX = randint(0, 1040)
        destY = 800
        self.speedX = (- self.rect.x + destX)//200
        self.speedY = (- self.rect.y + destY)//200
    def reduce(self):
        global score
        score += 2
        oldSize = self.size
        self.size = self.size // 1.25
        if self.size < 20:
            asteroids.add(Asteroid('asteroid.png'))
            if ((score//100) + 1) > len(asteroids):
                asteroids.add(Asteroid('asteroid.png'))
            self.kill()
        else:
            delta = (oldSize - self.size)//2
            oldX, oldY = (self.rect.x, self.rect.y)
            self.image = transform.scale(self.image, (self.size, self.size))
            self.rect = self.image.get_rect()  
            self.rect.x = oldX+delta
            self.rect.y = oldY+delta
def enemyCreate():
    enemys.remove(enemys)
    asteroids.remove(asteroids)
    for i in range(5):
        enemys.add(Enemy('ufo.png'))
    asteroids.add(Asteroid('asteroid.png'))
#создай окно игры
window = display.set_mode((1120, 800))
display.set_caption('Супер-пупер-шутер')
#задай фон сцены
background = transform.scale(image.load('galaxy.jpg'), (1120, 800))
#создай 2 спрайта и размести их на сцене
player = Player('rocket.png', 560, 720, 10)
bullets = sprite.Group()
enemys = sprite.Group()
asteroids = sprite.Group()
enemyCreate()
#работа со звуками
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
fire = mixer.Sound('fire.ogg')
#обработай событие «клик по кнопке "Закрыть окно"»
gameOver = False
finish = 0 #0-играем 1-выиграли 2-проиграли
clock = time.Clock()
FPS = 60
font.init()
fnt = font.Font(None, 170)
fntMidle = font.Font(None, 70)
fntSmall = font.Font(None, 35)
win = fnt.render('YOU WIN', True, (80, 200, 120))
lose = fnt.render('YOU LOSE', True, (220, 20, 60))

score = 0
unScore = 0
while not gameOver:
    window.blit(background, (0, 0))
    events = event.get()
    for ev in events:
        if ev.type == QUIT:
            gameOver = True
    if not finish:
        player.update()
        player.reset()
        enemys.update()
        enemys.draw(window)
        asteroids.update()
        asteroids.draw(window)
        bullets.update()
        bullets.draw(window)
        collideList = sprite.groupcollide(enemys, bullets, True, True)
        score += len(collideList)
        for i in range(5 + score//10 - len(enemys)):
            enemys.add(Enemy('ufo.png'))
        collideList = sprite.groupcollide(asteroids, bullets, False, True)
        for asteroid in collideList:
            asteroid.reduce()
        collideList = sprite.spritecollide(player, asteroids, False)
        if len(collideList) > 0:
            player.reduceLifes()
        if score > 1000:
            if score//unScore > 50:
                finish = 1
        if unScore:
            if score//unScore < 10:
                finish = 2
    else:
        keys = key.get_pressed()
        if keys[K_r]:
            player.restart()
            finish = 0
            score = 0
            unScore = 0
            enemyCreate()
    if finish == 1:
        window.blit(win, (300, 350))
    elif finish == 2:
        window.blit(lose, (250, 350))
    scoreText = fntSmall.render('УНИЧТОЖЕНО: ' + str(score), True, (255, 255, 255))
    window.blit(scoreText, (0, 0))
    unScoreText = fntSmall.render('ПРОПУЩЕНО: ' + str(unScore), True, (255, 255, 255))
    window.blit(unScoreText, (0, 35))
    lifesText = fntSmall.render('ЖИЗНИ: ' + str(player.lifes), True, (255, 255, 255))
    window.blit(lifesText, (980, 0))
    if player.godMode:
        godModeText = fntMidle.render('ЩИТЫ АКТИВНЫ', True, (255-player.godMode, player.godMode, 0))
        window.blit(godModeText, (330, 80))
    display.update()
    clock.tick(FPS)