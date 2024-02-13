import pygame,math

class AI:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = pygame.image.load("assets/AI boy.png")
        self.rect = self.image.get_rect

        # Beginner attributes
        self.beginner_speed = 7        # Set the speed for the beginner AI
        self.direction = 1             # Set the direction that the beginner AI will begin moving in
        self.difficulty = 'beginner'   # Set the AI's difficulty

        # Expert jump attributes
        self.jump = False
        self.gravity = 0

    def AI_hitbox(self):
        # Define the hit boX of the AI as a Rect object
        return pygame.Rect((self.x, self.y, 165, 241))

    def change_difficulty(self, AI_difficulty):
        # Change the difficulty based on the value passed from pregame screen selection
        self.difficulty = AI_difficulty
          
    def update(self, screen, ball):            
        # Movement code if beginner difficulty is chosen
        if self.difficulty == 'beginner':
            
            # Change direction if AI has reached the edges of the pitch
            if ball.x != self.x:
                if self.x > 955 or self.x < 155:
                    self.direction = -self.direction
                       
            # Move AI in specified direcion at specified speed
            self.x += self.beginner_speed * self.direction
     
        # Movement code if intermediate difficulty is chosen
        if self.difficulty == 'intermediate':
            # Calculate the distance between the AI and the ball
            distance = math.sqrt((self.x - ball.x) ** 2 + (self.y - ball.y) ** 2)
            
            if distance > 2 and self.x != ball.x:
                #If ball is to the right of the AI
                if ball.x > self.x + 165 // 2:
                    # Move the AI to the right towards the ball
                    self.x += 7
                    #If ball is to the left of the AI
                elif ball.x < self.x + 165 // 2:
                    # Move the AI to the left towards the ball
                    self.x -= 7

        # Movement code if expert difficulty is chosen
        if self.difficulty == 'expert':
            # Jump if the AI is on the ground and the ball is above it
            if self.jump == False and ball.y < self.y and ball.x < self.x + 165:
                self.jump = True
                self.gravity = -15  # Reduce gravitational strength 

            # Apply gravity to the AI's vertical speed
            self.gravity += 1  

            # Update the AI's vertical position based on its speed
            self.y += self.gravity
            
            #If ball is to the right of the AI
            if ball.x > self.x + 165 // 2:
                # Move the AI to the right towards the ball
                self.x += 5
            #If ball is to the left of the AI
            elif ball.x < self.x + 165 // 2:
                # Move the AI to the left towards with the ball
                self.x -= 5

            # Stop gravity and define the floor at y 480
            if self.y > 480:
                self.jump = False
                self.gravity = 0
                self.y = 480
            
        # Dsiplay the AI
        screen.blit(self.image, (self.x, self.y))

        
