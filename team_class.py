

class Team():
    '''This class is for the teams in the game; this is going to more or less a storage place for all the information pertaining to the team;
    The decision making will be found in the coaches; the 'playing' will be found in... well... the players; this will hold the list of players, coach,
    board members, and financials of the team.'''
    
    #Player Storage
    #These hold the id numbers for the objects that the team will use
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    #this is the coach/general-manager for the team
    manager = 0
    
    #this is the total list of players that a team has
    roster = [0,0,0,0]
    
    #this is the starters for a game that the team will field
    starters = [0,0,0]
    
    #this is the pointguard for the starters
    point_guard = 0
    
    #Finacials
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    #this is the total amount of money that the team has at its disposal
    money = 0
    
    #this is the amount of 'stock' available to the 'public'; the stock price is equal to the money/stock
    stock = 0
    stock_price = 0
    
    def set_stock_price(self):
        self.stock_price = float(self.money)/float(self.stock)
    
    