import pygame
import os
import random
pygame.init()

#window size
width = height = 700


win = pygame.display.set_mode((width,height))
pygame.display.set_caption("Space Invaders")
#images
#ships
blue_ship = pygame.image.load(os.path.join("assets","pixel_ship_blue_small.png"))
green_ship = pygame.image.load(os.path.join("assets","pixel_ship_green_small.png"))
red_ship = pygame.image.load(os.path.join("assets","pixel_ship_red_small.png"))
yellow_ship = pygame.image.load(os.path.join("assets","pixel_ship_yellow.png"))
#laser
blue_laser = pygame.image.load(os.path.join("assets","pixel_laser_blue.png"))
green_laser = pygame.image.load(os.path.join("assets","pixel_laser_green.png"))
red_laser = pygame.image.load(os.path.join("assets","pixel_laser_red.png"))
yellow_laser = pygame.image.load(os.path.join("assets","pixel_laser_yellow.png"))
#bg
bg = pygame.transform.scale(pygame.image.load(os.path.join("assets","background-black.png")),(width,height))

def collide(obj1,obj2):
	offset_x = int(obj2.x - obj1.x)
	offset_y = int(obj2.y - obj1.y)
	return obj1.mask.overlap(obj2.mask,(offset_x,offset_y)) != None

class Laser:
	def __init__(self,x,y,img):
		self.x = x
		self.y = y
		self.img = img
		self.mask = pygame.mask.from_surface(self.img)
	def move(self,vel):
		self.y+=vel
	def draw(self,window):
		window.blit(self.img,(self.x,self.y))	
	def off_screen(self,height,laser):
		return (self.y > height and self.y<=0)
	def collision(self,obj2):
		return collide(self,obj2)	
			

class Ships:
	COOLDOWN =30
	def __init__(self,x,y,health = 100):
		self.x = x
		self.y = y
		self.ship_img = None
		self.laser_img = None
		self.health = health
		self.laser = []
		self.cool_down_counter = 0
	def draw(self,window):	
		window.blit(self.ship_img,(self.x,self.y))
		for laser in self.laser:
			laser.draw(window)
	def get_width(self):
		return self.ship_img.get_width()
	def get_height(self):
		return self.ship_img.get_height()
	def cooldown(self):
		if self.cool_down_counter >= self.COOLDOWN-10:
			self.cool_down_counter = 0
		else: 
			self.cool_down_counter+=1		
	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x,self.y,self.laser_img)
			self.laser.append(laser)
			cool_down_counter = 1
	def move_laser(self,vel,objs):
		self.cooldown()
		for laser in self.laser:
			laser.move(vel)
			if laser.off_screen(height,laser):
				self.laser.remove(laser)
			elif laser.collision(objs):
				objs.health -=10 
				self.laser.remove(laser)		

class Player(Ships):
	def __init__(self,x,y,health = 100):
		super().__init__(x,y,health)
		self.ship_img = yellow_ship
		self.laser_img = yellow_laser
		self.max_health = health
		self.mask= pygame.mask.from_surface(self.ship_img)
	def move_laser(self,vel,objs):
		self.cooldown()
		for laser in self.laser:
			laser.move(vel)
			if laser.off_screen(height,laser):
				self.laser.remove(laser)
			else: 
				for obj in objs:
					if laser.collision(obj):
						objs.remove(obj)
						self.laser.remove(laser)
	def healthbar(self,window):
		pygame.draw.rect(window,(255,0,0),(self.x,self.y+self.ship_img.get_height()+10,self.ship_img.get_width(),10))					
		pygame.draw.rect(window,(0,255,0),(self.x,self.y+self.ship_img.get_height()+10,self.ship_img.get_width() * (self.health/self.max_health),10))		
	def draw(self,window):
		super().draw(window)
		self.healthbar(window)	
		
class Enemy(Ships):
	color_map = {
		"red" :(red_ship,red_laser),
		"blue" : (blue_ship,blue_laser),
		"green" : (green_ship,green_laser)
	}
	def __init__(self,x,y,color,health = 100):
		super().__init__(x,y,health)
		self.ship_img,self.laser_img = self.color_map[color]
		self.mask = pygame.mask.from_surface(self.ship_img)
	def move(self,vel):
		self.y += 	vel 
	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x-20,self.y,self.laser_img)
			self.laser.append(laser)
			cool_down_counter = 1	

def main():
	FPS = 60
	run = True
	level = 0
	lives = 5
	player_vel = 5
	enemy_vel = 1
	laser_vel = 5
	wave_length = 0
	clock = pygame.time.Clock()
	main_font = pygame.font.SysFont("comicsans",50)
	player = Player(width/2,height/2+height/4)
	enemies = []
	def redrawWindow():
		win.blit(bg,(0,0))
		level_font = main_font.render(f"Level  {level}",1,(255,255,255))
		win.blit(level_font,(10,10))
		lives_font = main_font.render(f"lives {lives}",1,(255,255,255))
		win.blit(lives_font,(width-lives_font.get_width()-10,10))
		for enemy in enemies:
			enemy.draw(win)
		player.draw(win)
		pygame.display.update()
	def lost():
		game_over_font = pygame.font.SysFont("comicsans",100)
		lost_font = game_over_font.render("Game Over",1,(255,255,255))
		win.blit(lost_font,(width/2 - lost_font.get_width()/2,height/2 - lost_font.get_height()/2))
		pygame.display.update()
		pygame.time.delay(3000)
	while run:
		clock.tick(FPS)
		if len(enemies) == 0:
			level+=1			
			wave_length+=5
			for i in range(wave_length):
				enemy = Enemy(random.randrange(10,width-100),random.randrange(-700,0),random.choice(["red","blue","green"]))
				enemies.append(enemy)	
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
		keys = pygame.key.get_pressed()
		if keys[pygame.K_a] and player.x>0:#left
			player.x-=player_vel
		if keys[pygame.K_d] and player.x + player.get_width()<width :#right
			player.x+=player_vel	
		if keys[pygame.K_w] and player.y >0 :#up
			player.y-=player_vel	
		if keys[pygame.K_s] and player.y + player.get_height()+15 < height:#down
			player.y+=player_vel
		if keys[pygame.K_SPACE]:
			player.shoot()	
		for enemy in enemies:
			enemy.move_laser(laser_vel,player)
			enemy.move(enemy_vel)
			if random.randrange(0,60) == 1:	
				enemy.shoot()
			if enemy.y +enemy.get_height()> height:
				lives-=1
				enemies.remove(enemy)
			elif collide(enemy,player):
				player.health -=30
				enemies.remove(enemy)		
		player.move_laser(-laser_vel,enemies)		
		redrawWindow()
		if lives == 0 or player.health <=0:
			lost()
			main()
			run = False	
			
def main_menu():
	def draw_text_middle(text,color,size,win):
		font = pygame.font.SysFont('comicsans',size)
		label = font.render(text,1,color)
		win.blit(label,(width /2 -(label.get_width()/2),height/2 - label.get_height()/2))
	run = True
	while run:
		win.fill((0,0,0))
		draw_text_middle("Press any key to start...",(255,255,255),60,win)
		pygame.display.update()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.KEYDOWN:
				main()
main_menu()				