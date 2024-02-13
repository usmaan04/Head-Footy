# Define the button class
class Button():
	def __init__(self, image, pos, text_input, font, base_colour, hovering_colour):   # Each parameter is initialised
		self.image = image
		self.x_pos = pos[0]                           # Determines the inputted desired x coordinate of the button 
		self.y_pos = pos[1]                           # Determines the inputted y coordinate of the button
		self.font = font
		self.base_colour, self.hovering_colour = base_colour, hovering_colour         # Sets the user inputted variables as their self representatives
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_colour)
		if self.image is None:                                                    # If no image is set the text inputted is replaced by this 
			self.image = self.text
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))           
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

# Allows inputted text/images to be displayed on screen after updates
	def update(self, screen):                                
		if self.image is not None:                       # If image parameter is set as None the inputted '(text_input paramater)' is displayed instead else the image is displayed  
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)
		
# Checks for the users mouse, if the mouse is between the identified rectangle True is returned
	def checkForInput(self, position):               
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False
	
# Checks for the users x and y mouse  position and where it is, which determines the buttons colour
	def changeColour(self, position):                         
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_colour)    # If the mouse is hovering between the identified rectangle then this is registered as True 
		                                                                                     # and the buttons colour is set to the variable hovering_colour that is declared within the function and parameters passed
		else:
			self.text = self.font.render(self.text_input, True, self.base_colour)        # Otherwise the colour is set as base_colour

