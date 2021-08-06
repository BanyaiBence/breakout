import pygame
import os
from sys import exit
from random import randint, choice

pygame.init()

FPS = 60
CLOCK = pygame.time.Clock()

WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
RADIUS = 10

A_DOWN = False
D_DOWN = False

class COLORS:
    RED = (255, 0, 0)
    WHITE = (255 ,255, 255)
    BLACK = (0, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    GREY = (128, 128, 128)
    YELLOW = (255, 255, 0)


class GameObject:
    def __init__(self, display, width, height, color=COLORS.WHITE, x=1, y=1, shape="rect"):
        self.display = display
        self.color = color
        self.shape = shape
        self.frame = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        

    def draw(self):
        if self.shape == "rect" or self.shape == "rectangle":
            pygame.draw.rect(self.display, self.color, self.frame)
        elif self.shape == "circle" or self.shape == "ellipse":
            pygame.draw.ellipse(self.display, self.color, self.frame)

    def update(self):
        self.frame.x = self.x
        self.frame.y = self.y


class Ball(GameObject):
    def __init__(self, display, tile, color=COLORS.WHITE):
        self.x_speed = 7
        self.y_speed = 7
        self.tile = tile
        super().__init__(display, 20, 20, color, 200, 550, "circle")

    def move(self):
        global A_DOWN, D_DOWN

        result = False

        if self.x <= 0 or self.x > WIDTH-self.width:
            self.x_speed = -self.x_speed

        if self.y <= 0 or self.y >= 800-self.height:
            self.y_speed = -self.y_speed

        if self.y >= 799-self.height:
            self.y = 760 - self.height
            result = True

        self.x += self.x_speed
        self.y += self.y_speed

        if self.frame.colliderect(self.tile.frame):
            self.y_speed = -abs(self.y_speed)

        self.update()
        return result


class Brick(GameObject):
    def __init__(self, display, ball, x, y, color=COLORS.GREEN, hits_till_break=4):
        self.ball = ball
        super().__init__(display, 60, 30, color, x, y)
        self.left_side = BrickSide(display, ball, x, y)
        self.right_side = BrickSide(display, ball, x+60, y)
        self.top_side = BrickTop(display, ball, x, y)
        self.bottom_side = BrickTop(display, ball, x, y+30)
        self.hits_till_break = hits_till_break



    def check_for_collision(self):
        if self.frame.colliderect(self.ball.frame):
            left_coll = self.left_side.check_for_collision()
            right_coll = self.right_side.check_for_collision()
            top_coll = self.top_side.check_for_collision()
            bottom_coll = self.bottom_side.check_for_collision()

            if left_coll or right_coll or top_coll or bottom_coll:
                self.hits_till_break -= 1
            if self.hits_till_break == 3:
                self.color = COLORS.BLUE
            if self.hits_till_break == 2:
                self.color = COLORS.YELLOW
            if self.hits_till_break == 1:
                self.color = COLORS.RED

            if left_coll or right_coll or top_coll or bottom_coll:
                if self.hits_till_break == 0:
                    return True
                return False
        return False


class BrickSide(GameObject):
    def __init__(self, display, ball, x, y, color=COLORS.RED):
        self.ball = ball
        super().__init__(display, 1, 30, color, x, y)

    def check_for_collision(self):
        self.update()
        if self.frame.colliderect(self.ball.frame):
            self.ball.x_speed = -self.ball.x_speed
            return True
        return False


class BrickTop(GameObject):
    def __init__(self, display, ball, x, y, color=COLORS.RED):
        self.ball = ball
        super().__init__(display, 60, 1, color, x, y)

    def check_for_collision(self):
        self.update()
        if self.frame.colliderect(self.ball.frame):
            self.ball.y_speed = -self.ball.y_speed
            return True
        return False


class Tile(GameObject):
    def __init__(self, display, color=COLORS.GREEN):
        self.speed = 0
        super().__init__(display, 120, 15, color, 400, 765)

    def move(self):
        global A_DOWN, D_DOWN
        if self.x <= 0:
            self.x = 0
        if self.x >= WIDTH-self.width:
            self.x = WIDTH-self.width

        speed = 20

        if A_DOWN:
            self.speed = -speed
        elif D_DOWN:
            self.speed = speed

        if self.speed > 0:
            self.speed -= 0.8
        elif self.speed <0:
            self.speed += 0.8

        self.x += self.speed

        self.update()


class Window:
    def __init__(self, width, height, title, color=COLORS.BLACK):
        self.display = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(title)
        self.color = color

    def refresh(self):
        self.display.fill(self.color)


class EventHandler():
    @staticmethod
    def events():
        global A_DOWN, D_DOWN
        for event in pygame.event.get():
            # quit
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    A_DOWN = True
                if event.key == pygame.K_d:
                    D_DOWN = True
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    A_DOWN = False
                if event.key == pygame.K_d:
                    D_DOWN = False


class Game:
    def __init__(self):
        self.run = False
        self.window = Window(WIDTH, HEIGHT, "BREAKOUT")
        self.tile = Tile(self.window.display)
        self.events = EventHandler.events
        self.ball = Ball(self.window.display, self.tile)
        self.bricks = []
        self.font = pygame.font.Font("freesansbold.ttf", 25)
        self.score = 0
        self.lives = 3

        rand = 1
        for x in range(100, 700, 61):
            for y in range(100, 500, 31):
                rand = choice([rand, rand, 1, 2])
                rand_hits = randint(1, 4)
                if rand == 1:
                    self.bricks.append(Brick(self.window.display, self.ball, x, y, hits_till_break=rand_hits))

    def draw(self):
        self.window.refresh()
        self.tile.draw()
        self.ball.draw()
        for brick in self.bricks:
            brick.draw()

        text = self.font.render(f"{self.score}", False, COLORS.WHITE)
        self.window.display.blit(text, (10, 10))
        text = self.font.render(f"{self.lives}", False, COLORS.WHITE)
        self.window.display.blit(text, (780, 10))


        pygame.display.flip()


    def main(self):
        self.run = True
        while self.run:
            self.events()
            self.tile.move()
            off = self.ball.move()
            if off:
                self.lives -= 1
            if self.lives <= 0:
                print(f"Score: {self.score}")
                print("Game Over!")
                self.run = False
                
            for index, brick in enumerate(self.bricks):
                coll = brick.check_for_collision()
                if coll:
                    del self.bricks[index]
                    self.score += 1

            self.draw()
            CLOCK.tick(60)


if __name__ == "__main__":

    game = Game()
    game.main()
        