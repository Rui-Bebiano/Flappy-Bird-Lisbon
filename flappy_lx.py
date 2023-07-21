import pygame
import sys
import random
import numpy as np

"""
1 - Defining Game Functions --------------------------------------------------------------------------------------------------------------------------
"""

def draw_base():
    # the .blit method draws an image (or a part of an image) to another Surface. It takes two arguments:
    #   - the first argument ("base") is the source Surface, the image you want to draw.
    #   - the second argument is a tuple defining the top left corner of where you want to draw your source Surface on the destination Surface. 
    #     This point is defined in pixels, with (0,0) being the top-left corner of the Surface.
    screen.blit(base, (0, WINDOW_HEIGHT - base.get_height()))

def create_pipe():
    # When created, the pipes are positioned just outside the right edge of the screen
    random_pipe_pos = random.choice(pipe_heights)
    bottom_pipe = pipe_surface.get_rect(midtop = (WINDOW_WIDTH + PIPE_WIDTH, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom = (WINDOW_WIDTH + PIPE_WIDTH, random_pipe_pos - gap))
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    return pipes

def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= WINDOW_HEIGHT:
            # Bottom pipe
            screen.blit(pipe_surface, pipe)
        else:
            # Top pipe - must be fliped vertically
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)

def check_collision(pipes):
    global BIRD_MOVEMENT, bird_y_pos, bird_rect
    # Collision with pipes
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return True
    # Overshooting top or touching floor
    if bird_rect.top <= -100 or bird_rect.bottom >= WINDOW_HEIGHT:
        return True
    # No collision
    return False

def rotate_bird(bird):
    new_bird = pygame.transform.rotozoom(bird, -BIRD_MOVEMENT * 3, 1)
    return new_bird

def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center = (100, bird_rect.centery))
    return new_bird, new_bird_rect

def draw_score(SCORE, x, y):
    """Draw the score using digit images."""
    # Convert the score to a string
    score_str = str(SCORE)
    
    # Calculate the total width of the score images
    total_width = 0
    for digit in score_str:
        total_width += digits[int(digit)].get_width()
    
    # Calculate the starting x position
    start_x = x - total_width // 2
    
    # Draw each digit
    for digit in score_str:
        digit_img = digits[int(digit)]
        screen.blit(digit_img, (start_x, y))
        start_x += digit_img.get_width()

def score_display(game_state):
    if game_state == 'main_game':
        score_surface = game_font.render(str(int(SCORE)), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center = (WINDOW_WIDTH / 2, 50))
        screen.blit(score_surface, score_rect)
    if game_state == 'game_over':
        pass  # implement game over score

"""
2 - Initializing pygame -----------------------------------------------------------------------------------------------------------------------------
"""
# This function initializes all the modules required for Pygame.
pygame.init()

"""
3 - Initializing Variables --------------------------------------------------------------------------------------------------------------------------
"""

# game modes
# Start screen: GAME_MODE='StartScreen'
# Game: GAME_MODE='Play'
# Game Over: GAME_MODE='GameOver'
GAME_MODE = 'StartScreen'

# game variables
WINDOW_HEIGHT = 600
WINDOW_WIDTH = 600
GRAVITY = 0.25
BIRD_MOVEMENT = 0
SCORE = 0
bird_colors = ['blue', 'yellow', 'red']
bird_color = random.choice(bird_colors)

# bird variables
BIRD_INITIAL_y_pos = WINDOW_HEIGHT / 2
bird_y_pos = BIRD_INITIAL_y_pos
bird_flap = 0

# pipe variables
PIPE_WIDTH = 70
pipe_heights = range(280,450,10) #[200, 300, 400]  # add more values as needed
gap = 200
pipe_list = []
pipes_passed = []

# create a custom event for adding a new pipe; the value is the time difference between consecutive pipes
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 800)  

"""
4 - Game Window and Clock --------------------------------------------------------------------------------------------------------------------------
"""

# Creating game window - This function creates a game window, or screen, to which you can draw images and shapes.
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# setting up game clock - This is a simple way to track time and control the game's frame rate.
clock = pygame.time.Clock()

"""
5 - Load Images ------------------------------------------------------------------------------------------------------------------------------------
"""

# load images
bg_day = pygame.image.load('background-day.png').convert()
bg_night = pygame.image.load('background-night.png').convert()

bgs = [pygame.image.load(f'Lisbon_Sprites\\{i}.png').convert_alpha() for i in range(8)]
bg_gameover = pygame.image.load('background-gameover.png').convert()
base = pygame.image.load('base.png').convert()
bird_down = pygame.image.load(f'{bird_color}bird-downflap.png').convert_alpha()
bird_mid = pygame.image.load(f'{bird_color}bird-midflap.png').convert_alpha()
bird_up = pygame.image.load(f'{bird_color}bird-upflap.png').convert_alpha()
bird_frames = [bird_down, bird_mid, bird_up]
bird = bird_frames[bird_flap]
bird_rect = bird.get_rect(center = (WINDOW_WIDTH / 4, bird_y_pos))
pipe_surface = pygame.image.load('pipe-green.png').convert()
pipe_list.extend(create_pipe())
digits = [pygame.image.load(f'{i}.png').convert_alpha() for i in range(10)]
game_font = pygame.font.Font(None, 40)
game_over_surface = pygame.image.load('gameover.png').convert_alpha()
game_over_rect = game_over_surface.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
initial_message_surface = pygame.image.load('message.png').convert_alpha()
initial_message_rect = initial_message_surface.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

# Resizing images to fit the game screen
bgs = [pygame.transform.scale(bgs[i], (WINDOW_WIDTH, WINDOW_HEIGHT)) for i in range(8)]

bg_night = pygame.transform.scale(bg_night, (WINDOW_WIDTH, WINDOW_HEIGHT))
bg_day = pygame.transform.scale(bg_day, (WINDOW_WIDTH, WINDOW_HEIGHT))
bg_gameover = pygame.transform.scale(bg_gameover, (WINDOW_WIDTH, WINDOW_HEIGHT))
_, base_height = base.get_rect().size
base = pygame.transform.scale(base, (WINDOW_WIDTH, base_height))


"""
6 - Main Game Loop ------------------------------------------------------------------------------------------------------------------------------------
"""

while True:
    
    #### START SCREEN MODE ### -----------------------------------------------------
    if GAME_MODE=='StartScreen':
        
        # EVENTS
        for event in pygame.event.get():   # This function is used to handle events, like keyboard and mouse inputs.
            # if the event is QUIT, then the window's close button has been clicked; stop all pygame modules and terminate the program
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # if the event is a mouse button being clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                # activate the game
                GAME_MODE = 'Play'
                # clear the list of pipes
                pipe_list.clear()
                pipes_passed.clear()
                # recenter the bird
                bird_rect.center = (WINDOW_WIDTH / 4, WINDOW_HEIGHT / 2)
                # reset the bird's vertical movement
                BIRD_MOVEMENT = 0
                # reset the score
                SCORE = 0
                # returns the number of milliseconds since pygame.init() was called
                initial_time = pygame.time.get_ticks()  
        
        # RENDER
        # Drawing background 
        screen.blit(bg_day, (0, 0))
        screen.blit(initial_message_surface, initial_message_rect)
        draw_base() 
        # Bird in position
        bird_y_pos = BIRD_INITIAL_y_pos
        # Updating screen
        pygame.display.update()
    

    #### PLAY MODE ### -----------------------------------------------------
    elif GAME_MODE=='Play':
        
        # EVENTS
        for event in pygame.event.get():   # This function is used to handle events, like keyboard and mouse inputs.
            # if the event is QUIT, then the window's close button has been clicked; stop all pygame modules and terminate the program
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # if the event is a mouse button being clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                # reset the bird's vertical movement
                BIRD_MOVEMENT = 0
                # make the bird move upwards
                BIRD_MOVEMENT -= 6
                # reset the bird's flap state
                bird_flap = 0
            # if the event is our user-defined SPAWNPIPE event
            if event.type == SPAWNPIPE:
                # create a new pair of pipes (up and bottom) and add them to the list of pipes
                pipe_list.extend(create_pipe())

        # UPDATE GAME STATE 
        
        # bird
        bird_flap += 0.1
        if bird_flap > 2:
            bird_flap = 0
        bird = bird_frames[int(bird_flap)]
        BIRD_MOVEMENT += GRAVITY
        bird_y_pos += BIRD_MOVEMENT
        bird_rect.centery = bird_y_pos

        # pipes
        pipe_list = move_pipes(pipe_list)
        
        # check collision
        if check_collision(pipe_list):
            GAME_MODE = 'GameOver'

        # score update
        for i in range(len(pipe_list)):  # check if bird has passed any pipes
            pipe = pipe_list[i]
            if bird_rect.left > pipe.right:
                if i >= len(pipes_passed) or not pipes_passed[i]:
                    SCORE += 1
                    pipes_passed.append(True)
              
        # change of background based on score
        i = int(((SCORE/2)) // 10 % 7)
        bg = bgs[i]     
       
        
        # RENDER
        
        # Background
        screen.blit(bg, (0, 0))
        #bird
        screen.blit(bird, bird_rect)
        #pipes
        draw_pipes(pipe_list)
        #Scores
        draw_score(int(SCORE/2), WINDOW_WIDTH // 2, 50)
        # draw base
        draw_base()
        
        # Updating screen
        pygame.display.update()
        
        # Limit frames per second (i.e., speed of the bird)
        clock.tick(90)
    
    #### GAME OVER MODE ### -----------------------------------------------------
    elif GAME_MODE=='GameOver':
    
        # EVENTS
        for event in pygame.event.get():   # This function is used to handle events, like keyboard and mouse inputs.
            # if the event is QUIT, then the window's close button has been clicked; stop all pygame modules and terminate the program
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # if the event is a mouse button being clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                # activate the game
                GAME_MODE = 'StartScreen'

        #RENDER
        # Background
        screen.blit(bg_gameover, (0, 0))
        screen.blit(game_over_surface, game_over_rect)
        
        # draw base
        draw_base()
        
        # Updating screen
        pygame.display.update()
        
        # Limit frames per second (i.e., speed of the bird)
        clock.tick(90)





