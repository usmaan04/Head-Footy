# Import required libraries pygame, sys, and time
# Refernces py files and imports named classes within them
import pygame, sys, time, math        
from button import Button   
from pygame import mixer
from ai import AI

# Initialise pygame and mixer 
pygame.init()               
mixer.init()
pygame.joystick.init()

# Define pygame screen dimensions and create window
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
logo = pygame.image.load("assets/Head Footy.png")
pygame.display.set_icon(logo)

# Load and set images 
BG = pygame.image.load("assets/background pitch.jpg")
instructions_BG = pygame.image.load("assets/football.jpg")
backdrop = pygame.image.load("assets/whiteboard.jpg")
backbutton_image = pygame.image.load("assets/back.png")
playbutton_image = pygame.image.load("assets/play.png")
button_backdrop = pygame.image.load("assets/button backdrop.png")
game_pitch = pygame.image.load("assets/main pitch.jpg")
scoreboard = pygame.image.load("assets/scoreboard.png")
blueboy_left = pygame.image.load("assets/blue boy left.png")
capboy_left = pygame.image.load("assets/cap boy left.png")
girl_left = pygame.image.load("assets/girl left.png")
redgirl_left = pygame.image.load("assets/red girl left.png")
blueboy_right = pygame.image.load("assets/blue boy right.png")
capboy_right = pygame.image.load("assets/cap boy right.png")
girl_right = pygame.image.load("assets/girl right.png")
redgirl_right = pygame.image.load("assets/red girl right.png")
goal_text = pygame.image.load("assets/Goal !!!.png")

# Set sound files as variables
#Sound from Zapsplat.com
button_click = pygame.mixer.Sound('assets/button click.mp3')
ball_hit = pygame.mixer.Sound('assets/ball hit.mp3')
goal_cheer = pygame.mixer.Sound('assets/goal cheer.mp3')
stadium_cheer = pygame.mixer.Sound('assets/stadium ambient cheer.mp3')
mixer.music.set_volume(1)

# Set time limit
countdown_time = 180

# Set the scores for the players 
player1_score = 0
player2_score = 0

joystick_count = pygame.joystick.get_count()
if joystick_count == 0:
    print("Error, no joystick detected")
else:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

# Returns the requested text in the labelled font and in the desired size
def get_font(size):
    return pygame.font.Font("assets/sporty.ttf", size)

# Multi line paragraphing
def drawText(surface, text, colour, rect, font, aa=False, bkg=None):
    rect = pygame.Rect(rect)
    y = rect.top
    lineSpacing = -2

    #gets the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside the created surface box
        if y + fontHeight > rect.bottom:
            break

        # determines the maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if the text has just been wrapped, then adjust the wrap to the last word      
        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1

        # render the line and displays it to the surface
        if bkg:
            image = font.render(text[:i], 1, colour, bkg)
            image.set_colourkey(bkg)
        else:
            image = font.render(text[:i], aa, colour)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text just blit
        text = text[i:]

    return text

# Define the Player class
class Player:
    def __init__(self, x, y):
        # Initialize the player's starting image, position, and hitbox rect
        self.image = blueboy_left
        self.rect = pygame.Rect((x, y, 165, 241))
        self.x = x
        self.y = y

        #Set jump attributes
        self.jump = False          # Set jump to False to start
        self.gravity = 0           # Set the gravitational strength
        self.on_floor = True       # Set on_floor to True to start

    def change_character(self, image):
        # Change the player's image based on the value passed from character selection
        if image == "blueboy_left":
            self.image = blueboy_left
        elif image == "capboy_left":
            self.image = capboy_left
        elif image == "girl_left":
            self.image = girl_left
        elif image == "redgirl_left":
            self.image = redgirl_left

        if image == "blueboy_right":
            self.image = blueboy_right
        elif image == "capboy_right":
            self.image = capboy_right
        elif image == "girl_right":
            self.image = girl_right
        elif image == "redgirl_right":
            self.image = redgirl_left

    def move_left(self):
        # Move the player left by subtracting from the x coordinate
        self.x -= 10

    def move_right(self):
        # Move the player right by adding to the x coordinate
        self.x += 10
            
    def move_jump(self):
        # Set jump to True if the player is on the floor
        if self.on_floor == True:
            self.jump = True

        # Jump if the player is on the ground and the ball is above it
        if self.jump == True and self.on_floor == True :
            self.gravity = -15  # Reduce gravitational strength
            self.on_floor = False

    def character_hitbox(self):
        # Define the hit box of the player as a Rect object
        return pygame.Rect((self.x, self.y, 165, 241))

    def update(self, screen):
        # Boundary to prevent player from going too far to the left
        if self.x < 145:
            self.x = 145

        # Boundary to prevent player from going too far to the right
        if self.x > 955:
            self.x = 955

        # Incerase the strength of gravity
        self.gravity += 1

        if self.on_floor == False:
            # If player is not on the floor apply gravity
            self.y += self.gravity

        # Boundary to prevent player from falling off screen and labeling this as the floor
        if self.y > 480:
            self.y = 480
            self.on_floor = True
            
        # Display the character
        screen.blit(self.image, (self.x, self.y))

# Define the Ball class
class Ball:
    def __init__(self, x, y, radius):
        # Set the initial position and image of the ball
        self.x = x
        self.y = y
        self.image = pygame.image.load("assets/ball.png")
        self.rect = self.image.get_rect()
        self.radius = radius
        
        # Set the initial speed and gravity of the ball, and its bounce factor
        self.speed_x = 1
        self.speed_y = 1
        self.gravity = 1
        self.bounce_factor = 0.8

        # Add a cooldown timer and set its duration
        self.cooldown = False
        self.cooldown_duration = 0.5  # in seconds
        self.last_hit_time = 0
        
    def update(self, screen, player1_hitbox,AI_hitbox,player2_hitbox,left_goal_hitbox, right_goal_hitbox,game_mode):
        # Update the ball position based on its speed and gravity
        self.y += self.speed_y
        self.speed_y += self.gravity
        self.x += self.speed_x

        # Check if the ball hits the bottom of the screen
        if self.y + self.radius > 690:
            # Reverse the ball's direction and reduce its speed when it hits the ground
            self.y = 690 - self.radius
            self.speed_y *= -self.bounce_factor 

        # Check if the ball hits the top of the screen
        if self.y - self.radius < 20:
            # Reverse the ball's direction and reduce its speed when it hits the ceiling
            self.y = 20 + self.radius
            self.speed_y *= -0.1

        # Check if the ball hits the right walls
        if self.x + self.radius > 1050 and self.y + self.radius < 400 :
            # Reverse the ball's horizontal direction and reduce its speed when it hits a wall
            self.speed_x *= -1

        ## Check if the cooldown is active
        if self.cooldown:
            current_time = time.time()
            elapsed_time = current_time - self.last_hit_time

            # If the cooldown has expired, reset the cooldown flag
            if elapsed_time >= self.cooldown_duration:
                self.cooldown = False

        # Check if the ball can be hit (not in cooldown)
        if not self.cooldown:
            # Check if the ball collides with the player
            if self.rect.colliderect(player1_hitbox):
                pygame.mixer.Sound.play(ball_hit)
                # Move the ball in this direction to indicate the ball has been hit
                self.x += 100
                if self.speed_x < 0:
                    self.speed_x *= -0.8
                    self.speed_x *= 3 * self.bounce_factor
                else:
                    self.speed_x *= 0.8
                    self.speed_x *= 3 * self.bounce_factor
                        
                self.y -= 50

                # Set the cooldown flag and record the time
                self.cooldown = True
                self.last_hit_time = time.time()

            # Only check for player 2 collisions if gamemode is Two Player
            if game_mode == 'two_player' and not self.cooldown:
                if self.rect.colliderect(player2_hitbox):
                    pygame.mixer.Sound.play(ball_hit)
                    # Move the ball in this direction to indicate the ball has been hit
                    self.x -= 100
                    
                    if self.speed_x < 0:
                        self.speed_x *= 0.8
                        self.speed_x *= 3 * self.bounce_factor
                    else:
                        self.speed_x *= -0.8
                        self.speed_x *= 3 * self.bounce_factor
                        
                    self.y -= 50

                    # Set the cooldown flag and record the time
                    self.cooldown = True
                    self.last_hit_time = time.time()

            # Only check for AI collisions if gamemode is One Player
            if game_mode == 'one_player' and not self.cooldown:
                if self.rect.colliderect(AI_hitbox):
                    pygame.mixer.Sound.play(ball_hit)
                    # Move the ball in this direction to indicate the ball has been hit
                    self.x -= 100

                    if self.speed_x < 0:
                        self.speed_x *= 0.8
                        self.speed_x *= 3 * self.bounce_factor
                    else:
                        self.speed_x *= -0.8
                        self.speed_x *= 3 * self.bounce_factor
                        
                    self.y -= 50

                    # Set the cooldown flag and record the time
                    self.cooldown = True
                    self.last_hit_time = time.time()

        # If there is a collision with the right goal
        if self.rect.colliderect(right_goal_hitbox):
            global player1_score
            player1_score += 1
            pygame.mixer.Sound.play(goal_cheer)
            screen.blit(goal_text,(screen_width/2 - goal_text.get_width()/2, 200))
            pygame.display.update()
            time.sleep(1)
            Player1.x = 175
            Player1.y = 480
            if game_mode == 'one_player':
                AI.x = 935
                AI.y = 480
            elif game_mode == 'two_player':
                Player2.x = 935
                Player2.y = 480
            create_ball()

        # If there is a collision with the left goal
        if self.rect.colliderect(left_goal_hitbox):
            global player2_score
            player2_score += 1
            pygame.mixer.Sound.play(goal_cheer)
            screen.blit(goal_text,(screen_width/2 - goal_text.get_width()/2, 200))
            pygame.display.update()
            time.sleep(1)
            Player1.x = 175
            Player1.y = 480
            if game_mode == 'one_player':
                AI.x = 935
                AI.y = 480
            elif game_mode == 'two_player':
                Player2.x = 935
                Player2.y = 480
            create_ball()

        # Update the rect object for the image
        self.rect.center = (self.x, int(self.y))
        self.rect.x = self.x
        self.rect.y = self.y
        screen.blit(self.image, (self.rect.x, self.rect.y))


# Creates instances of the player and AI class for characters
Player1 = (Player(175,480))
Player2 = (Player(935,480))
AI = (AI(935,480))

class Goal():
    def __init__(self, image, pos):
        # Initialize the goal object with an image and position
        self.image = image
        self.x_pos = pos[0]                           
        self.y_pos = pos[1]
        # Create a rect object to represent the goal's position and size
        self.rect = self.image.get_rect(topright=(self.x_pos, self.y_pos))

    def goal_hitbox(self):
        return self.rect

    def update(self, screen):
        # Display the goal image onto the screen at its current position
        screen.blit(self.image, self.rect)

def create_ball():
    # Creates an instance of the ball class for the ball
    global ball
    ball = Ball(screen_width // 2, screen_height // 2, 20)

def instructions():
    while True:
        # Get the mouse position
        INSTRUCTIONS_MOUSE_POS = pygame.mouse.get_pos()

        # Set the image of the player controls
        controls_display = pygame.image.load("assets/Both controls.png")

        # Display the background and  backdrop image
        pygame.display.set_caption("Instructions")
        screen.blit(instructions_BG, (0, 0))
        screen.blit(backdrop,(215,78))  
        
        # Display title text 
        title_text = get_font(30).render("How To Play", True, "Black")
        title_rect = title_text.get_rect(center =(650,100)) 
        screen.blit(title_text, title_rect)

        # Display controls text
        controls_text = get_font(30).render("Player 1      Player 2 ", True, "Black")
        controls_rect = title_text.get_rect(center =(780,600))
        screen.blit(controls_text, controls_rect)

        # Create a game description text object, display it on a white rectangle on the screen
        game_description = "Head Footy is a new 2D football game where you can choose from a list of different characters to battle it out on the pitch either with a friend or on your own against our challenging AI. The aim of the game is simple, use your character to hit the ball into the opposing teams net while trying to defend your own. Do you have what it takes to be a Head Footy superstar?"
        description_rect = pygame.draw.rect(screen, "White", pygame.Rect(235, 120, 814, 410))
        font = pygame.font.Font("assets/font.ttf", 30)
        drawText(screen, game_description, "Dark Gray", description_rect, font)                
        
        # Create a back button object and display it on the screen
        instruction_back = Button(image=backbutton_image, pos=(275, 575),
                                 text_input=None, font=get_font(10), base_colour="White", hovering_colour="White")     


        # Change the color of the back button if the mouse is hovering over it and update the screen to display the updated button
        instruction_back.changeColour(INSTRUCTIONS_MOUSE_POS)
        instruction_back.update(screen)

        # Display an image showing the controls for both players
        screen.blit(controls_display,(650,460))

        # Listen for events like button clicks and mouse movements
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # if the user clicks the 'X' button, quit the game
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN: # if the user clicks the mouse
                if instruction_back.checkForInput(INSTRUCTIONS_MOUSE_POS): # and the back button is clicked
                    pygame.mixer.Sound.play(button_click)
                    main_menu() # return to the main menu

        # Update the display to show any changes   
        pygame.display.update() 

def one_pregame():
    while True:
        # Get the current mouse position
        ONEPLAYER_MOUSE_POS = pygame.mouse.get_pos()

        # Set the image of the player controls
        controls_display = pygame.image.load("assets/Player 1 controls.png")
        
        # Display the background and  backdrop image
        screen.blit(instructions_BG, (0, 0))
        screen.blit(backdrop,(215,78))
        
        # Set the window caption to "One Player"
        pygame.display.set_caption("One Player")

        # Create rescaled image icons
        newblueboy_left = pygame.transform.scale(blueboy_left, (blueboy_left.get_width() // 4, blueboy_left.get_height() // 4))
        newcapboy_left = pygame.transform.scale(capboy_left, (capboy_left.get_width() // 4, capboy_left.get_height() // 4))
        newgirl_left = pygame.transform.scale(girl_left, (girl_left.get_width() // 4, girl_left.get_height() // 4))
        newredgirl_left = pygame.transform.scale(redgirl_left, (redgirl_left.get_width() // 4, redgirl_left.get_height() // 4))
        
        # Display the controls image and text
        font = pygame.font.Font("assets/font.ttf", 30)
        screen.blit(controls_display, (700, 475))
        controls_text = font.render("Controls", True, "Black")
        controls_rect = controls_text.get_rect(center =(795,610)) #sets text position within the window
        screen.blit(controls_text, controls_rect)

        # Display title text
        title_text = get_font(30).render("1 Player", True, "Black")
        title_rect = title_text.get_rect(center =(650,100)) #sets text position within the window
        screen.blit(title_text, title_rect)

        # Display character selection prompt
        character_text =  get_font(30).render("Select your character:", True, "Black")
        character_rect = character_text.get_rect(center =(477,150)) #sets text position within the window
        screen.blit(character_text, character_rect)

        # Display difficulty selection prompt
        difficulty_text =  get_font(30).render("Select the AI's  difficulty:", True, "Black")
        difficulty_rect = difficulty_text.get_rect(center =(507,370)) #sets text position within the window
        screen.blit(difficulty_text, difficulty_rect)

        # Create instances of the button class
        oneplayer_back = Button(image=backbutton_image, pos=(275, 575),
                            text_input=None, font=get_font(10), base_colour="White", hovering_colour="White")
        blueboyleft_button = Button(image=button_backdrop, pos=(390, 210), 
                            text_input="Name 1", font=pygame.font.Font("assets/font.ttf", 30), base_colour="Black", hovering_colour="Red")
        capboyleft_button = Button(image=button_backdrop, pos=(700, 210), 
                            text_input="Name 2", font=pygame.font.Font("assets/font.ttf", 30), base_colour="Black", hovering_colour="Dark Green")
        girlleft_button = Button(image=button_backdrop, pos=(390, 310),                                 
                            text_input="Name 3", font=pygame.font.Font("assets/font.ttf", 30), base_colour="Black", hovering_colour="Yellow")
        redgirlleft_button = Button(image=button_backdrop, pos=(700, 310),                                 
                            text_input="Name 4", font=pygame.font.Font("assets/font.ttf", 30), base_colour="Black", hovering_colour="Red")
        beginner_button = Button(image=pygame.image.load("assets/background button green.png"), pos=(390, 420), 
                            text_input="Beginner", font=pygame.font.Font("assets/font.ttf", 30), base_colour="Black", hovering_colour="Blue")
        intermediate_button = Button(image=pygame.image.load("assets/background button yellow.png"), pos=(700, 420), 
                            text_input="Intermediate", font=pygame.font.Font("assets/font.ttf", 30), base_colour="Black", hovering_colour="Blue")
        expert_button = Button(image=pygame.image.load("assets/background button red.png"), pos=(545, 490),
                            text_input="Expert", font=pygame.font.Font("assets/font.ttf", 30), base_colour="Black", hovering_colour="Blue")
        play_button = Button(image=playbutton_image, pos=(1000, 575),
                            text_input=None, font=pygame.font.Font("assets/font.ttf", 30), base_colour="Black", hovering_colour="Red")

        #Update all buttons
        for button in [oneplayer_back, blueboyleft_button, capboyleft_button, girlleft_button,redgirlleft_button,beginner_button,intermediate_button,expert_button, play_button]:
                        button.changeColour(ONEPLAYER_MOUSE_POS)
                        button.update(screen)
                        
        # Displays all the resized image icons 
        screen.blit(newblueboy_left,(267,177))
        screen.blit(newcapboy_left,(578,177))
        screen.blit(newgirl_left,(268,279))
        screen.blit(newredgirl_left,(578,277))

        # Listen for events like button clicks and mouse movements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Sets variable and plays sound for confirmation
                if oneplayer_back.checkForInput(ONEPLAYER_MOUSE_POS):
                    pygame.mixer.Sound.play(button_click)
                    main_menu()
                if blueboyleft_button.checkForInput(ONEPLAYER_MOUSE_POS):
                    player1_choice = 'blueboy_left'
                if capboyleft_button.checkForInput(ONEPLAYER_MOUSE_POS):
                    player1_choice = 'capboy_left' 
                if girlleft_button.checkForInput(ONEPLAYER_MOUSE_POS):
                    player1_choice = 'girl_left'
                if redgirlleft_button.checkForInput(ONEPLAYER_MOUSE_POS):
                    player1_choice = 'redgirl_left'
                    
                if beginner_button.checkForInput(ONEPLAYER_MOUSE_POS):
                    AI_difficulty = 'beginner'
                if intermediate_button.checkForInput(ONEPLAYER_MOUSE_POS):
                    AI_difficulty = 'intermediate'
                if expert_button.checkForInput(ONEPLAYER_MOUSE_POS):
                    AI_difficulty = 'expert'

                # Determines the character the player has chosen for player 1 and changes its character image from the default
                if blueboyleft_button.checkForInput(ONEPLAYER_MOUSE_POS) or capboyleft_button.checkForInput(ONEPLAYER_MOUSE_POS) or girlleft_button.checkForInput(ONEPLAYER_MOUSE_POS) or redgirlleft_button.checkForInput(ONEPLAYER_MOUSE_POS):
                    Player1.change_character(player1_choice)
                    pygame.mixer.Sound.play(button_click)

                # Determines the difficulty the player has chosen for AI by passing a parameter to change its value
                if beginner_button.checkForInput(ONEPLAYER_MOUSE_POS) or intermediate_button.checkForInput(ONEPLAYER_MOUSE_POS) or expert_button.checkForInput(ONEPLAYER_MOUSE_POS):
                    AI.change_difficulty(AI_difficulty)
                    pygame.mixer.Sound.play(button_click)

                # Start timer, create ball, begin stadiums sound, set player score and switch screen      
                if play_button.checkForInput(ONEPLAYER_MOUSE_POS):
                    pygame.mixer.Sound.play(button_click)
                    global start_time
                    start_time = time.time()
                    create_ball()
                    channel = pygame.mixer.Channel(0)
                    channel.play(stadium_cheer, -1)
                    channel.set_volume(0.2)
                    global player1_score
                    player1_score = 0
                    global player2_score
                    player2_score = 0
                    Player1.x = 175
                    AI.x = 935
                    one_player()

        # Update the display to show any changes       
        pygame.display.update()

def one_player():
    while True:
        # Get the current mouse position
        ONEPLAYER_MOUSE_POS = pygame.mouse.get_pos()

        # Set the RGB colours
        black = (0, 0, 0)
    
        # Blit the game background onto the screen
        screen.blit(game_pitch, (0, 0))

        # Displays the scoreboard image on the screen
        screen.blit(scoreboard,(416,1))

        # Set the window caption to "One Player"
        pygame.display.set_caption("One Player")

        # Set the goal score font and font size
        scorefont = pygame.font.Font(None, 120)

        # Set the time font and size
        timefont = pygame.font.Font(None, 45)

        # Set the Win system text
        player1_wins_text = pygame.image.load("assets/Player 1 Wins.png")
        player2_wins_text = pygame.image.load("assets/Player 2 Wins.png")
        draw_text = pygame.image.load("assets/Draw.png")

        # Display scoreboard text
        scoreboard_text = get_font(20).render("Player 1       Time      Player 2", True, "Black")
        scoreboard_rect = scoreboard_text.get_rect(center =(640,50)) #sets text position within the window
        screen.blit(scoreboard_text, scoreboard_rect)
        
        # Create goal objects for the left and right sides of the screen
        left_goal = Goal(image= pygame.image.load("assets/Left goal.png"), pos =(150,389))
        right_goal = Goal(image= pygame.image.load("assets/Right goal.png"),pos=(1330,389))
        
        # Create a button object for the "back" button
        oneplayer_back = Button(image=backbutton_image, pos=(200,100),
                            text_input=None, font=get_font(10), base_colour="White", hovering_colour="White")
        
        ball_creator = Button(image=backbutton_image, pos=(650,180),
                            text_input=None, font=get_font(10), base_colour="White", hovering_colour="White")

        # Create hitboxes for collisions
        player1_hitbox = Player1.character_hitbox()
        right_goal_hitbox = right_goal.goal_hitbox()
        left_goal_hitbox = left_goal.goal_hitbox()
        AI_hitbox = AI.AI_hitbox()
        player2_hitbox = None

        # Update the time remaining
        time_remaining = countdown_time - int(time.time() - start_time)

        # Create the formatted text that will be displayed for timer and scores
        scoreboard_time = timefont.render("{}".format(time_remaining), True, black)
        scoreboard_player1 = scorefont.render("{}".format(player1_score), True, black)
        scoreboard_player2 = scorefont.render("{}".format(player2_score), True, black)

        # Display/Update positions of all object,images and text on screen
        left_goal.update(screen)
        right_goal.update(screen)
        AI.update(screen,ball)
        screen.blit(scoreboard_time,(615,120))
        screen.blit(scoreboard_player1, (500, 100))
        screen.blit(scoreboard_player2, (735, 100))
        ball.update(screen,player1_hitbox, AI_hitbox, player2_hitbox, left_goal_hitbox, right_goal_hitbox,game_mode = 'one_player')

        #Update all buttons
        for button in [oneplayer_back]:
            button.changeColour(ONEPLAYER_MOUSE_POS) 
            button.update(screen)

        # If time runs out, display winner and return to main menu
        if time_remaining == 0 and player1_score > player2_score:
            screen.blit(player1_wins_text, (screen_width/2 - player1_wins_text.get_width()/2, 200))
            pygame.display.update()
            pygame.mixer.stop() #Stop all sound
            time.sleep(3) # wait for 3 seconds
            main_menu()
        elif time_remaining == 0 and player2_score > player1_score:
            screen.blit(player2_wins_text, (screen_width/2 - player2_wins_text.get_width()/2, 200))
            pygame.display.update()
            time.sleep(3) # wait for 3 seconds
            pygame.mixer.stop()
            main_menu()
        elif time_remaining == 0 and player2_score == player1_score :
            screen.blit(draw_text, (screen_width/2 - draw_text.get_width()/2, 200))
            pygame.display.update()
            pygame.mixer.stop() #Stop all sound
            time.sleep(3) # wait for 3 seconds
            main_menu()

        # Listen for events like button clicks and mouse movements
        for event in pygame.event.get():
            # Quit the game if the user closes the window
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # If the "back" button is clicked, play a sound effect and go back to the one-player pregame screen
            if event.type == pygame.MOUSEBUTTONDOWN:
                if oneplayer_back.checkForInput(ONEPLAYER_MOUSE_POS):
                    pygame.mixer.Sound.play(button_click)
                    pygame.mixer.stop()
                    one_pregame()
                if ball_creator.checkForInput(ONEPLAYER_MOUSE_POS):
                    pygame.mixer.Sound.play(button_click)
                    create_ball()
        
        Player1.update(screen)
                    
        # Listen for keyboard inputs to control the player character's movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            Player1.move_left()
        if keys[pygame.K_d]:
            Player1.move_right()
        if keys[pygame.K_w]:
            Player1.move_jump()

        #if abs(joystick.get_axis(0)) > 0.1:
         #   Player1.x += joystick.get_axis(0) * 10

        #if joystick.get_button(0):
         #   Player1.move_jump()
            
        # Update the display to show any changes
        pygame.display.update()
                                                    
def two_pregame():
    while True:
        # Get the current mouse position
        TWOPLAYER_MOUSE_POS = pygame.mouse.get_pos()

        # Set the image of the player controls
        player1_controls = pygame.image.load("assets/Player 1 controls.png")
        player2_controls = pygame.image.load("assets/Player 2 controls.png")

        # Display the background and  backdrop image
        screen.blit(instructions_BG, (0, 0))
        screen.blit(backdrop,(215,78))

        # Set the window caption to "Head Footy"
        pygame.display.set_caption("Two Player")

        # Display the controls image and text
        screen.blit(player1_controls,(850,155))
        screen.blit(player2_controls,(850,365))

        font = pygame.font.Font("assets/font.ttf", 25)
        player1_text = font.render("Player 1 controls", True, "Black")
        player1_rect = player1_text.get_rect(center =(945,300)) 
        screen.blit(player1_text, player1_rect)

        player2_text = font.render("Player 2 controls", True, "Black")
        player2_rect = player2_text.get_rect(center =(945,510)) 
        screen.blit(player2_text, player2_rect)

        # Create rescaled image icons
        newblueboy_left = pygame.transform.scale(blueboy_left, (blueboy_left.get_width() // 4, blueboy_left.get_height() // 4))
        newcapboy_left = pygame.transform.scale(capboy_left, (capboy_left.get_width() // 4, capboy_left.get_height() // 4))
        newgirl_left = pygame.transform.scale(girl_left, (girl_left.get_width() // 4, girl_left.get_height() // 4))
        newredgirl_left = pygame.transform.scale(redgirl_left, (redgirl_left.get_width() // 4, redgirl_left.get_height() // 4))
        newblueboy_right = pygame.transform.scale(blueboy_right, (blueboy_right.get_width() // 4, blueboy_right.get_height() // 4))
        newcapboy_right = pygame.transform.scale(capboy_right, (capboy_right.get_width() // 4, capboy_right.get_height() // 4))
        newgirl_right = pygame.transform.scale(girl_right, (girl_right.get_width() // 4, girl_right.get_height() // 4))
        newredgirl_right = pygame.transform.scale(redgirl_right, (redgirl_right.get_width() // 4, redgirl_right.get_height() // 4))

        # Display title text
        title_text = get_font(30).render("2 Player", True, "Black")
        title_rect = title_text.get_rect(center =(650,100)) #sets text position within the window
        screen.blit(title_text, title_rect)

        # Display Player 1 character selection prompt text
        player1_text =  get_font(22).render("Player 1 select your character:", True, "Black")
        player1_rect = player1_text.get_rect(center =(477,130)) #sets text position within the window
        screen.blit(player1_text, player1_rect)

        # Display Player 2 character selection prompt text
        player2_text =  get_font(22).render("Player 2 select your character:", True, "Black")
        player2_rect = player2_text.get_rect(center =(477,340)) #sets text position within the window
        screen.blit(player2_text, player2_rect)

        # Create instances of the button class
        twoplayer_back = Button(image=backbutton_image, pos=(275, 575),
                            text_input=None, font=get_font(10), base_colour="White", hovering_colour="White")
        blueboyleft_button = Button(image=button_backdrop, pos=(390, 190), 
                            text_input="Name 1", font=pygame.font.Font("assets/font.ttf", 30), base_colour="Black", hovering_colour="Red")
        capboyleft_button = Button(image=button_backdrop, pos=(700, 190), 
                            text_input="Name 2", font=pygame.font.Font("assets/font.ttf", 30), base_colour="Black", hovering_colour="Dark Green")
        girlleft_button = Button(image=button_backdrop, pos=(390, 290),                                 
                            text_input="Name 3", font=pygame.font.Font("assets/font.ttf", 30), base_colour="Black", hovering_colour="Yellow")
        redgirlleft_button = Button(image=button_backdrop, pos=(700, 290),                                 
                            text_input="Name 4", font=pygame.font.Font("assets/font.ttf", 30), base_colour="Black", hovering_colour="Red")
        blueboyright_button = Button(image=button_backdrop, pos=(390,400), 
                            text_input="Name 1", font=pygame.font.Font("assets/font.ttf", 30), base_colour="Black", hovering_colour="Green")
        capboyright_button = Button(image=button_backdrop, pos=(700, 400), 
                            text_input="Name 2", font=pygame.font.Font("assets/font.ttf", 30), base_colour="Black", hovering_colour="Green")
        girlright_button = Button(image=button_backdrop, pos=(390, 500), 
                            text_input="Name 3", font=pygame.font.Font("assets/font.ttf", 30), base_colour="Black", hovering_colour="Green")
        redgirlright_button = Button(image=button_backdrop, pos=(700, 500), 
                            text_input="Name 4", font=pygame.font.Font("assets/font.ttf", 30), base_colour="Black", hovering_colour="Green")
        play_button = Button(image=playbutton_image, pos=(1000, 575),
                            text_input=None, font=pygame.font.Font("assets/font.ttf", 30), base_colour="Black", hovering_colour="Red")

        twoplayer_back = Button(image=backbutton_image, pos=(275, 575),
                                 text_input=None, font=get_font(10), base_colour="White", hovering_colour="White")

        # Update all buttons
        for button in [twoplayer_back, blueboyleft_button, capboyleft_button, girlleft_button ,redgirlleft_button,blueboyright_button,capboyright_button,girlright_button,redgirlright_button, play_button]:
            button.changeColour(TWOPLAYER_MOUSE_POS)          
            button.update(screen)

        # Displays all the resized image icons 
        screen.blit(newblueboy_left,(267,157))
        screen.blit(newcapboy_left,(578,157))
        screen.blit(newgirl_left,(268,259))
        screen.blit(newredgirl_left,(578,257))
        screen.blit(newblueboy_right,(267,367))
        screen.blit(newcapboy_right,(578,367))
        screen.blit(newgirl_right,(268,469))
        screen.blit(newredgirl_right,(578,467))

        # Listen for events like button clicks and mouse movements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Sets variable and plays sound for confirmation
                if twoplayer_back.checkForInput(TWOPLAYER_MOUSE_POS):
                    pygame.mixer.Sound.play(button_click)
                    main_menu()
                if blueboyleft_button.checkForInput(TWOPLAYER_MOUSE_POS):
                    player1_choice = 'blueboy_left'
                if capboyleft_button.checkForInput(TWOPLAYER_MOUSE_POS):
                    player1_choice = 'capboy_left' 
                if girlleft_button.checkForInput(TWOPLAYER_MOUSE_POS):
                    player1_choice = 'girl_left'
                if redgirlleft_button.checkForInput(TWOPLAYER_MOUSE_POS):
                    player1_choice = 'redgirl_left'
                    
                if blueboyright_button.checkForInput(TWOPLAYER_MOUSE_POS):
                    player2_choice = 'blueboy_right'
                if capboyright_button.checkForInput(TWOPLAYER_MOUSE_POS):
                    player2_choice = 'capboy_right' 
                if girlright_button.checkForInput(TWOPLAYER_MOUSE_POS):
                    player2_choice = 'girl_right'
                if redgirlright_button.checkForInput(TWOPLAYER_MOUSE_POS):
                    player2_choice = 'redgirl_right'

                # Determines the character the player has chosen for player 1 and changes its character image from the default
                if blueboyleft_button.checkForInput(TWOPLAYER_MOUSE_POS) or capboyleft_button.checkForInput(TWOPLAYER_MOUSE_POS) or girlleft_button.checkForInput(TWOPLAYER_MOUSE_POS) or redgirlleft_button.checkForInput(TWOPLAYER_MOUSE_POS):
                    Player1.change_character(player1_choice)
                    pygame.mixer.Sound.play(button_click)

                # Determines the character the player has chosen for player 2 and changes its character image from the default
                if blueboyright_button.checkForInput(TWOPLAYER_MOUSE_POS) or capboyright_button.checkForInput(TWOPLAYER_MOUSE_POS) or girlright_button.checkForInput(TWOPLAYER_MOUSE_POS) or redgirlright_button.checkForInput(TWOPLAYER_MOUSE_POS):
                    Player2.change_character(player2_choice)
                    pygame.mixer.Sound.play(button_click)

                # Start timer, create ball, begin stadiums sound, set player score and switch screen
                if play_button.checkForInput(TWOPLAYER_MOUSE_POS):
                    pygame.mixer.Sound.play(button_click)
                    global start_time
                    start_time = time.time()
                    create_ball()
                    channel = pygame.mixer.Channel(0)
                    channel.play(stadium_cheer, -1)
                    channel.set_volume(0.2)
                    global player1_score
                    player1_score = 0
                    global player2_score
                    player2_score = 0
                    two_player()

        # Update the display to show any changes          
        pygame.display.update()

def two_player():
    while True:
        # Get the current mouse position
        TWOPLAYER_MOUSE_POS = pygame.mouse.get_pos()

        # Set the colours
        white = (255, 255, 255)
        black = (0, 0, 0)
    
        # Blit the game background onto the screen
        screen.blit(game_pitch, (0, 0))

        # Displays the scoreboard image on the screen
        screen.blit(scoreboard,(416,1))

        # Set the window caption to "Two Player"
        pygame.display.set_caption("Two Player")

        # Set the goal score font and font size
        scorefont = pygame.font.Font(None, 120)

        # Set the time font and size
        timefont = pygame.font.Font(None, 45)

        # Set the Win system text
        player1_wins_text = pygame.image.load("assets/Player 1 Wins.png")
        player2_wins_text = pygame.image.load("assets/Player 2 Wins.png")
        draw_text = pygame.image.load("assets/Draw.png")

        # Display scoreboard text
        scoreboard_text = get_font(20).render("Player 1       Time      Player 2", True, "Black")
        scoreboard_rect = scoreboard_text.get_rect(center =(640,50)) 
        screen.blit(scoreboard_text, scoreboard_rect)
        
        # Create goal objects for the left and right sides of the screen
        left_goal = Goal(image= pygame.image.load("assets/Left goal.png"), pos =(150,389))
        right_goal = Goal(image= pygame.image.load("assets/Right goal.png"),pos=(1330,389))
        
        # Create a button object for the "back" button
        twoplayer_back = Button(image=backbutton_image, pos=(200,100),
                            text_input=None, font=get_font(10), base_colour="White", hovering_colour="White")

        # Create hitboxes for collisions
        player1_hitbox = Player1.character_hitbox()
        player2_hitbox = Player2.character_hitbox()
        right_goal_hitbox = right_goal.goal_hitbox()
        left_goal_hitbox = left_goal.goal_hitbox()
        AI_hitbox = None

        # Update the time remaining
        time_remaining = countdown_time - int(time.time() - start_time)

        # Display the time remaining
        time_text = get_font(30).render("{}".format(time_remaining), True, black)

        # Create the formatted text that will be displayed for timer and scores
        scoreboard_time = timefont.render("{}".format(time_remaining), True, black)
        scoreboard_player1 = scorefont.render("{}".format(player1_score), True, black)
        scoreboard_player2 = scorefont.render("{}".format(player2_score), True, black)

        # Display/Update positions of all object,images and text on screen
        left_goal.update(screen)
        right_goal.update(screen)
        ball.update(screen, player1_hitbox, AI_hitbox, player2_hitbox, left_goal_hitbox ,right_goal_hitbox,game_mode = 'two_player')
        screen.blit(scoreboard_time,(615,120))
        screen.blit(scoreboard_player1, (500, 100))
        screen.blit(scoreboard_player2, (735, 100))

        # Update all buttons
        for button in [twoplayer_back]:
            button.changeColour(TWOPLAYER_MOUSE_POS) 
            button.update(screen)

        # If time runs out, display winner and return to main menu
        if time_remaining == 0 and player1_score > player2_score:
            screen.blit(player1_wins_text, (screen_width/2 - player1_wins_text.get_width()/2, 200))
            pygame.display.update()
            pygame.mixer.stop() #Stop all sound
            time.sleep(3) # wait for 3 seconds
            main_menu()
        elif time_remaining == 0 and player2_score > player1_score:
            screen.blit(player2_wins_text, (screen_width/2 - player2_wins_text.get_width()/2, 200))
            pygame.display.update()
            time.sleep(3) # wait for 3 seconds
            pygame.mixer.stop()
            main_menu()
        elif time_remaining == 0 and player2_score == player1_score :
            screen.blit(draw_text, (screen_width/2 - draw_text.get_width()/2, 200))
            pygame.display.update()
            pygame.mixer.stop() #Stop all sound
            time.sleep(3) # wait for 3 seconds
            main_menu()


        Player2.update(screen)
        Player1.update(screen)

        # Listen for game events
        for event in pygame.event.get():
            # Quit the game if the user closes the window
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # If the "back" button is clicked, play a sound effect and go back to the one-player pregame screen
            if event.type == pygame.MOUSEBUTTONDOWN:
                if twoplayer_back.checkForInput(TWOPLAYER_MOUSE_POS):
                    pygame.mixer.Sound.play(button_click)
                    two_pregame()

                    
        # Listen for keyboard inputs to control the player character's movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            Player1.move_left()
        if keys[pygame.K_d]:
            Player1.move_right()
        if keys[pygame.K_w]:
            Player1.move_jump()
            
        if keys[pygame.K_LEFT]:
            Player2.move_left()
        if keys[pygame.K_RIGHT]:
            Player2.move_right()
        if keys[pygame.K_UP]:
            Player2.move_jump()

        #if abs(joystick.get_axis(0)) > 0.1:
         #   Player1.x += joystick.get_axis(0) * 10

        #if joystick.get_button(0):
         #   Player1.move_jump()
        
        # Update the display to show any changes
        pygame.display.update()

def main_menu():
    while True:
        # Get the current mouse position
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        # Display the background and logo image
        screen.blit(BG, (0, 0))                         
        screen.blit(logo,(457,-50))

        # Set the window caption to "Head Footy"
        pygame.display.set_caption("Head Footy")
        
        # Create instances of the button class
        instruction_button = Button(image=pygame.image.load("assets/background button rectangle.png"), pos=(320, 500),     
                            text_input="Instructions", font=get_font(52), base_colour="Black", hovering_colour="Blue")     
        oneplayer_button = Button(image=pygame.image.load("assets/background button rectangle.png"), pos=(320, 350), 
                            text_input="1 Player", font=get_font(60), base_colour="Black", hovering_colour="Green")
        twoplayer_button = Button(image=pygame.image.load("assets/background button rectangle.png"), pos=(960, 350), 
                            text_input="2 Player", font=get_font(60), base_colour="Black", hovering_colour="Green")
        quit_button = Button(image=pygame.image.load("assets/background button rectangle.png"), pos=(960, 500), 
                            text_input="Quit", font=get_font(60), base_colour="Black", hovering_colour="Red")
        
        # Update all buttons
        for button in [instruction_button, oneplayer_button, twoplayer_button, quit_button]:                           
            button.changeColour(MENU_MOUSE_POS)          
            button.update(screen)

        # Listen for events like button clicks and mouse movements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Call function to switch screen if button is clicked
            if event.type == pygame.MOUSEBUTTONDOWN:                    
                if instruction_button.checkForInput(MENU_MOUSE_POS):    
                    pygame.mixer.Sound.play(button_click)
                    instructions()
                elif oneplayer_button.checkForInput(MENU_MOUSE_POS):
                    pygame.mixer.Sound.play(button_click)
                    one_pregame()
                elif twoplayer_button.checkForInput(MENU_MOUSE_POS):
                    pygame.mixer.Sound.play(button_click)
                    two_pregame()
                elif quit_button.checkForInput(MENU_MOUSE_POS):
                    pygame.mixer.Sound.play(button_click)
                    pygame.quit()
                    sys.exit()
                    
        # Update the display to show any changes
        pygame.display.update()

# Load the main menu
main_menu()

