import os
import sys
import time
import pygame
import random
import globals
from resources import game
from resources import colors
from resources import phrases
from resources.classes import enemy
from resources.classes import weapons
from resources.classes import powerup

# Init pygame
pygame.mixer.pre_init(22050, -16, 2, 512)
pygame.init()
pygame.font.init()

# Load fonts
font = pygame.font.Font(os.path.join(globals.data_dir, 'fonts/LeelawUI.ttf'), 16)
fontSmall = pygame.font.Font(os.path.join(globals.data_dir, 'fonts/LeelUIsl.ttf'), 14)
fontElcwoodBig = pygame.font.Font(os.path.join(globals.data_dir, 'fonts/elkwood.ttf'), 68)
fontElcwoodSmall = pygame.font.Font(os.path.join(globals.data_dir, 'fonts/elkwood.ttf'), 14)
fontElcwoodMedium = pygame.font.Font(os.path.join(globals.data_dir, 'fonts/elkwood.ttf'), 30)
fontCaviar = pygame.font.Font(os.path.join(globals.data_dir, 'fonts/CaviarDreams_Bold.ttf'), 26)

# Game window
globals.winWidth = 1366
globals.winHeight = 768
fullscreen = True
winBackground = colors.black
win = game.window(globals.winWidth, globals.winHeight, pygame.FULLSCREEN, winBackground, "Warah Killer")

# Sprites
sprites = pygame.sprite.Group()
beerSprite = pygame.sprite.Group()
topSprites = pygame.sprite.Group()
pwrSprites = pygame.sprite.Group()

# Crosshair & Guns
cursor = weapons.Crosshair()
topSprites.add(cursor)
gun = weapons.Gun()
topSprites.add(gun)
gunOffsetY = 0

# Enemy
foe = enemy.Enemy()
sprites.add(foe)

# Beer
beer = enemy.Beer()
beerClock = random.randint(25, 40)

# Shooting
isShooting = False
shotOnce = False
isBombing = False

# Reloading
isReloading = False

# Load sounds
sndDie = (
    game.loadSound('snd/ah.wav', 0.9),
    game.loadSound('snd/ah2.wav', 0.9),
    game.loadSound('snd/ah3.wav', 0.9)
)
sndShot = game.loadSound('snd/shot.wav', 0.5)
sndEmpty = game.loadSound('snd/empty.wav')
sndReload = game.loadSound('snd/reload.wav')
sndGameOver = game.loadSound('snd/game_over.wav')
sndRebirth = game.loadSound('snd/rebirth.wav', 0.5)
sndRicochet = game.loadSound('snd/ricochet.wav')
sndGlassBreak = game.loadSound('snd/glass_break.wav')
sndBomb = game.loadSound('snd/bomb.wav', 0.5)

# Load spriotes background
bg = game.loadBackground()
statusBarImage = pygame.image.load(os.path.join(globals.data_dir, 'img/status_bar.png')).convert_alpha()
imgOhSnap = pygame.image.load(os.path.join(globals.data_dir, 'img/oh_snap.png')).convert_alpha()
imgReplay = pygame.image.load(os.path.join(globals.data_dir, 'img/replay.png')).convert_alpha()
imgLogo = pygame.image.load(os.path.join(globals.data_dir, 'img/logo.png')).convert_alpha()

# Generate stars
game.generateStars()

# Blink menu
menuBlink = False

# Is drunk
drunk = False

# Clock
clock = pygame.time.Clock()

# Hide cursor
pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))

# Starting room
room = 'menu'

# Load and play music
musicMain = game.loadMusic('snd/music.mp3')
musicMain.play(-1)
pygame.mixer.music.set_volume(0.7)

# App running
run = True

# Game loop
while run:

	globals.steps += 1

	# Handle events
	for event in pygame.event.get():

		# Quit game
		if event.type == pygame.QUIT: run = False

		# KEY EVENTS
		if event.type == pygame.KEYDOWN:

			# ESC
			if event.key == pygame.K_ESCAPE:

				globals.roomInit = False
				if room == 'main':
					# Clear all score and stuff
					game.clear()
					# Restart bullets
					gun.bulletsLeft = globals.gunMaxBullets
					# Kill existing enemy
					foe.kill()
					beer.kill()
					# Destroy powerups
					pwrBullets.kill()
					pwrBomb.kill()
					# Remove power-up text
					globals.drawPowerText = False
					# Restart phrase counter
					globals.phraseSteps = 0
					# Create an enemy
					foe = enemy.Enemy()
					sprites.add(foe)
					# Drunk mode off
					drunk = False
					beerClock = random.randint(25, 40)
					# Reset bomb amount
					globals.bombs = 5
					room = 'menu'
				else:
					run = False
					room = 'quit'

			# Full screen
			if event.key == pygame.K_F4:
				if not fullscreen:
					pygame.display.set_mode((globals.winWidth, globals.winHeight), pygame.FULLSCREEN)
					fullscreen = True
				else:
					pygame.display.set_mode((globals.winWidth, globals.winHeight))
					fullscreen = False

			
			if event.key == pygame.K_SPACE:
				# Replay game
				if room == 'game_over':
					# Clear all score and stuff
					game.clear()
					# Play sound
					sndRebirth.play()
					# Restart bullets
					gun.bulletsLeft = globals.gunMaxBullets
					# Create an enemy
					foe = enemy.Enemy()
					sprites.add(foe)
					# Restart bombs
					globals.bombs = 5
					# Switch rooms
					room = 'main'

				if room == 'menu':
					room = 'main'

	# Mouse position and button clicking.
	pos = pygame.mouse.get_pos()
	pressed1, pressed2, pressed3 = pygame.mouse.get_pressed()

	# Menu
	if room == 'menu':
		# Render room
		win.blit(bg, (0, 0))
		game.drawStars(win, True)

		win.blit(imgLogo, (globals.winWidth/2 - 250, globals.winHeight/2 - 60))
		
		if globals.steps % 50 == 0:
			if menuBlink == False:
				menuBlink = True
			else:
				menuBlink = False
			
		if menuBlink == True:
			game.drawMainMenu(win, fontElcwoodBig)
		pygame.display.update()
		
	# Main Room
	if room == 'main':
		# Init room
		if globals.roomInit == False:
			# Init power-ups
			pwrBullets = powerup.BulletPlus()
			pwrBomb = powerup.Bomb()
			# Put out of screen
			pwrBullets.rect.center = (-300, -300)
			pwrBomb.rect.center = (-300, -300)

			# Restart steps for room
			globals.steps = 1
			globals.roomInit = True
			
		# POWERUPS
		# Had some issues with clock.ste_timer...
		if globals.steps % (globals.second * globals.timerPowerUp) == 0:
			### Choose power-up
			pwrSelect = random.randint(0, 1)

			### CREATE AFTER {globals.timerPowerUp} SECONDS ###
			if pwrSelect == 0:
				pwrBullets.kill()
				pwrSprites.add(pwrBullets)
				pwrBullets.appeared = globals.steps # Last time powerup appeared
				pwrBullets.rect.x = random.randint(1, globals.winWidth - 140)
				pwrBullets.rect.y = random.randint(100, globals.winHeight - 140)
			else :
				pwrBomb.kill()
				pwrSprites.add(pwrBomb)
				pwrBomb.appeared = globals.steps # Last time powerup appeared
				pwrBomb.rect.x = random.randint(1, globals.winWidth - 140)
				pwrBomb.rect.y = random.randint(100, globals.winHeight - 140)
		if globals.steps % (pwrBullets.appeared + (globals.second * globals.timerPowerUpDestroy)) == 0:
			### DESTROY AFTER {globals.timerPowerUpDestroy} SECONDS ###
			pwrBullets.kill()
		if globals.steps % (pwrBomb.appeared + (globals.second * globals.timerPowerUpDestroy)) == 0:
			pwrBomb.kill()

		# KEY EVENTS JUST FOR THIS ROOM
		if event.type == pygame.KEYDOWN:

			# Z KEY - DROP BOMB
			if event.key == pygame.K_z:
				if isBombing == False and globals.bombs > 0:
					sndBomb.play()
					isBombing = True
					globals.bombs -= 1

					# Make blood
					blood = enemy.Blood()
					blood.rect.x = foe.rect.x
					blood.rect.y = foe.rect.y
					sprites.add(blood)
					# Show score for killed enemy
					globals.enemyScore = [50, blood.rect.x, blood.rect.y, int(time.time())]
					globals.enemyScorePos = 0
					globals.enemyScorePosChange = True
					# Play die sound
					random.choice(sndDie).play()
					# Remove enemy
					foe.kill()
					# Make a new one
					foe = enemy.Enemy()
					sprites.add(foe)
					# Add score & kills
					globals.kills += 1
					# Check if we should raise a level
					if globals.kills % globals.nextLevelKills == 0:
						globals.level += 1
					game.incrementScore(50)

		if event.type == pygame.KEYUP:
			# Z KEY RELEASE
			if event.key == pygame.K_z:
				isBombing = False

		# Check if left click and we still got bullets
		if pressed1 and gun.bulletsLeft > 0:
			if isShooting == False:

				# Kill enemy
				if pygame.sprite.collide_mask(foe, cursor):
					# Make blood
					blood = enemy.Blood()
					sprites.add(blood)
					# Show score for killed enemy
					globals.enemyScore = [globals.scorePerKill * globals.level, blood.rect.x, blood.rect.y, int(time.time())]
					globals.enemyScorePos = 0
					globals.enemyScorePosChange = True
					# Play die sound
					random.choice(sndDie).play()
					# Remove enemy
					foe.kill()
					# Make a new one
					foe = enemy.Enemy()
					sprites.add(foe)
					# Add score & kills
					globals.kills += 1
					# Check if we should raise a level
					if globals.kills % globals.nextLevelKills == 0:
						globals.level += 1
					game.incrementScore()

				# Get power up
				if pygame.sprite.collide_mask(pwrBullets, cursor):
					# Play sound
					sndRicochet.play()
					# EXAMPLE: +3 bullets (-1 for shooting and + 3 bonus = +2 new bullets)
					gun.bulletsLeft += 1 + globals.pwrBulletsAmount
					# Animate destroy
					pwrBulletsKill = powerup.BulletPlusGone(pwrBullets.rect.x, pwrBullets.rect.y)
					topSprites.add(pwrBulletsKill)
					# Destroy powerup icon
					pwrBullets.kill()
					# Draw power-up text
					globals.powerText = '+' + str(globals.pwrBulletsAmount) + ' bullets!'
					globals.drawPowerText = True
					globals.drawPowerTextStart = globals.steps
				if pygame.sprite.collide_mask(pwrBomb, cursor):
					# Play sound
					sndRicochet.play()

					# GIVE BOMB
					globals.bombs += 5

					# Animate destroy
					pwrBombKill = powerup.BombGone(pwrBullets.rect.x, pwrBullets.rect.y)
					topSprites.add(pwrBombKill)
					# Destroy powerup icon
					pwrBomb.kill()
					# Draw power-up text
					globals.powerText = '+ 5 bombs!'
					globals.drawPowerText = True
					globals.drawPowerTextStart = globals.steps

				# Drink beer
				if pygame.sprite.collide_mask(beer, cursor):
					sndGlassBreak.play()
					beer.kill()
					drunk = True 
					drunkExpire = 10 * globals.second # Drunk mode should expire in X seconds
					beerClock = random.randint(25, 40)
					# Kill crosshair
					cursor.kill()

		# Shooting
		if pressed1 and isShooting == False:
			if gun.bulletsLeft > 0:
				# Play shot sound
				sndShot.play()

				# Display gun shot
				gunShot = weapons.Gunshot()
				sprites.add(gunShot)

				# Increment shots
				globals.shots += 1
				gun.bulletsLeft -= 1
			else:
				sndEmpty.play()

		# Check if player is shooting
		if pressed1:
			isShooting = True

			# Animate gun position
			if shotOnce == False:
				if gun.rect.y < globals.winHeight - 148:
					gun.rect.y += 3
					if gun.rect.y == globals.winHeight - 148:
						shotOnce = True
			if shotOnce == True and gun.rect.y > globals.winHeight - 160:
				gun.rect.y -= 3
		else:
			isShooting = False

			# Restore original gun position
			if gun.rect.y > globals.winHeight - 160:
				gun.rect.y -= 3
			shotOnce = False

		if pressed3 and not pressed1 and gun.bulletsLeft == 0 and isReloading == False:
			sndReload.play()
			gun.bulletsLeft = globals.gunMaxBullets

		if pressed3:
			isReloading = True
		else:
			isReloading = False

		# Check if enemy is out of boundry (screen)
		if(foe.rect.x > globals.winWidth or foe.rect.y > globals.winHeight or foe.rect.x < 1-foe.spriteWidth or foe.rect.y < 1-foe.spriteWidth):
			# Remove enemy
			foe.kill()
			# Make a new one
			foe = enemy.Enemy()
			sprites.add(foe)
			# Increment missed
			globals.missed += 1
			# Game over if missed too much
			if globals.missed == globals.maxMissed:
				globals.roomInit = False
				room = 'game_over'

		# Check if beer is out of boundry (screen)
		if(beer.rect.x > globals.winWidth or beer.rect.y > globals.winHeight or beer.rect.x < 1-beer.spriteWidth or beer.rect.y < 1-beer.spriteWidth):
			# Destroy beer
			beer.kill()
			beerClock = random.randint(25, 40)

		# Place a beer on the screen
		if globals.steps % (beerClock * globals.second) == 0:
			beer.kill()
			beer = enemy.Beer()
			beerSprite.add(beer)

		# Expire drunk mode
		if drunk == True:
			drunkExpire -= 1
			if drunkExpire == 0:
				drunk = False
				# Make new crosshair
				cursor = weapons.Crosshair()
				topSprites.add(cursor)

		# Animate current kill score
		if globals.enemyScorePosChange == True:
			if globals.enemyScorePos < 50:
				globals.enemyScorePos += 2

		# Clear old kill score text
		if globals.enemyScore[3] + 1 < int(time.time()):
			globals.enemyScore = [0, -500, -500, 0] # Put out of screen
			globals.enemyScorePos = 0
			globals.enemyScorePosChange = False

		# Clear power-up text
		if globals.drawPowerTextStart != 0 and globals.steps % (globals.drawPowerTextStart + (globals.second*3)) == 0:
			globals.drawPowerText = False

		### RENDER SCREEN ###
		win.blit(bg, (0, 0))
		game.drawStars(win)
		sprites.update()
		sprites.draw(win)
		beerSprite.update()
		beerSprite.draw(win)
		pwrSprites.update()
		topSprites.update()
		game.drawBullets(win, gun.bulletsLeft)
		game.drawBombs(win, font)
		game.drawStatusbar(win, statusBarImage, font, fontSmall)
		pwrSprites.draw(win)
		game.drawEnemyScore(
			win, fontElcwoodSmall, 
			globals.enemyScore[0], 
			globals.enemyScore[1], 
			globals.enemyScore[2], 
			globals.enemyScore[3])
		topSprites.draw(win)
		if globals.drawPowerText == True:
			game.drawPowerUpText(win, fontElcwoodMedium, globals.powerText, 18, globals.winHeight - 48)
		if globals.debug == True:
			game.drawSeconds(win, font, 68, 142)
			game.drawDebugger(win, fontCaviar, globals.winWidth/2, globals.winHeight/2, str(pwrBomb.rect.x) + ' ' + str(pwrBomb.rect.y), str(pos[0]) + ' ' + str(pos[1])) 
		# game.drawPhrases(win, fontCaviar, globals.winWidth/2, 32)
		game.drawTime(win, font, 182, 63)
		
		if drunk == True:
			# Blur screen (drunk effect)
			if drunkExpire < (10 * globals.second) and drunkExpire > (5 * globals.second):
				surf = game.blurSurf(win, random.randint(1, 15))
			elif drunkExpire < (5 * globals.second) and drunkExpire > (3 * globals.second):
				surf = game.blurSurf(win, random.randint(1, 8))
			elif drunkExpire < (3 * globals.second) and drunkExpire > (2 * globals.second):
				surf = game.blurSurf(win, random.randint(1, 4))
			else:
				surf = game.blurSurf(win, random.randint(1, 2))
			win.blit(surf, (0, 0))

		pygame.display.update()
		### END RENDER SCREEN ###

	# Game over screen
	if room == 'game_over':
		if globals.roomInit == False:
			# Destroy powerups
			pwrBullets.kill()
			pwrBomb.kill()
			# Remove power-up text
			globals.drawPowerText = False
			# Kill enemy
			foe.kill()
			beer.kill()
			# Play game over sound
			sndGameOver.play()
			globals.roomInit = True
			# Restart phrase counter
			globals.phraseSteps = 0
			# Drunk mode off
			drunk = False

		win.blit(bg, (0, 0))
		game.drawStars(win)
		game.drawGameOver(win, imgOhSnap, imgReplay)
		# fontCaviar.render('Best Score: ', globals.kills ,(255,255,255))
		pygame.display.update()
	
	# Limit frame rate
	clock.tick(globals.FPS)

# Exiting game
pygame.quit()
exit()