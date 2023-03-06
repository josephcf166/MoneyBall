import sqlite3
from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)


playerHeadings = ['Player Number','Player Name', 'Date of Birth', 'Gender', 'Date Signed-Up', 'Current Team', 'Salary (£k/Week)', 'Start of Contract', 'Contract Duration', 'Games Played This Year', 'Games Won', 'Future Games']
clubHeadings = ['Club Name', 'Club Location', 'Club Manager']

def calculatePrices(playerSalary, playerGamesWon, playerWeeksLeftInContract, playerGamesPlayedThisYear, playerFutureGames):
   playerPrices = []
   baseWinRate = playerGamesWon / playerGamesPlayedThisYear
   basePrice = playerSalary * playerWeeksLeftInContract * baseWinRate
   playerPrices.append(basePrice)
   for i in range(len(playerFutureGames)):
      if playerFutureGames[i] == 'W':
         playerGamesWon += 1
         playerGamesPlayedThisYear += 1
      else:
         playerGamesPlayedThisYear += 1

      newWinRate = playerGamesWon / playerGamesPlayedThisYear
      priceAfterGame = playerSalary * playerWeeksLeftInContract * newWinRate
      playerPrices.append(priceAfterGame)
   return playerPrices

@app.route("/home") #Route for the about us page
@app.route("/")        
def home():
   print("Home")
   with sqlite3.connect('MoneyballDB.db') as conn:      
      cur = conn.cursor()
      cur.execute("SELECT * FROM Players ORDER BY RANDOM()")
      playerToWatch = cur.fetchone()
   conn.close()
   return render_template("home.html", playerToWatch = playerToWatch)

@app.route("/players") #Route for the players page        
def players():
   
   print("Players")
   with sqlite3.connect('MoneyballDB.db') as conn:      
      cur = conn.cursor()
      cur.execute("SELECT * FROM Players")
      playerData = cur.fetchall()
   conn.close()
   return render_template("players.html", playerHeadings = playerHeadings, playerData=playerData)

@app.route("/clubs") #Route for the clubs page        
def clubs():
   print("Clubs")
   with sqlite3.connect('MoneyballDB.db') as conn:      
      cur = conn.cursor()
      cur.execute("SELECT * FROM Clubs")
      clubData = cur.fetchall()
   conn.close()
   return render_template("clubs.html", clubHeadings = clubHeadings, clubData=clubData)

@app.route("/players/<playerID>")
def playerDetails(playerID):
   print("Player Details")
   print(playerID)
   with sqlite3.connect('MoneyballDB.db') as conn:      
      cur = conn.cursor()
      cur.execute("SELECT * FROM Players WHERE player_ID = ?", (playerID,))
      playerInfo = cur.fetchone()
      print(playerInfo)
      playerName = playerInfo[1]
      playerDoB = playerInfo[2]
      playerGender = playerInfo[3]
      playerDateSignedUp = playerInfo[4]
      playerCurrentTeam = playerInfo[5]
      playerSalary = playerInfo[6]
      playerStartOfContract = playerInfo[7]
      playerContractDuration = playerInfo[8]
      playerGamesPlayedThisYear = playerInfo[9]
      playerGamesWon = playerInfo[10]
      playerFutureGames = playerInfo[11]
      cur.execute("SELECT club_location, club_manager FROM Clubs WHERE club_name = ?", (playerCurrentTeam, ))
      clubInfo = cur.fetchone()
      playerTeamLocation = clubInfo[0]
      playerTeamManager = clubInfo[1]
   #Convert salary to value in thousands (e.g. 50 becomes 50000)
   playerSalary = int(playerSalary) * 1000
   print(playerSalary)
   #Get current date in desired format
   currentDate = datetime.now()
   currentDate = currentDate.strftime("%d/%m/%Y")
   currentDate = datetime.strptime(currentDate, "%d/%m/%Y")
   #Get start of contract in desired format
   playerStartOfContractAsDate = datetime.strptime(playerStartOfContract, '%d/%m/%Y')
   #Get the weeks the player has already played of his contract
   playerWeeksPlayedOfContract = (currentDate - playerStartOfContractAsDate).days
   playerWeeksPlayedOfContract = playerWeeksPlayedOfContract // 7
   #Get the weeks the player has over his entire contract
   playerWeeksInContract = ((playerContractDuration * 365) // 7)
   print(playerWeeksInContract)
   print(playerWeeksPlayedOfContract)
   #Find the difference between them for the remaining weeks in players contract
   playerWeeksLeftInContract = playerWeeksInContract - playerWeeksPlayedOfContract
   print(playerWeeksLeftInContract)
   #Get price of player and price after each future game
   playerPrices = calculatePrices(playerSalary, playerGamesWon, playerWeeksLeftInContract, playerGamesPlayedThisYear, playerFutureGames)
   print(playerPrices)
   for i in range(len(playerPrices)):
      playerPrices[i] = round(playerPrices[i], 2)
   print(playerPrices)

   conn.close()
   return render_template('playerdetails.html', playerID = playerID, playerName = playerName, playerDoB = playerDoB,\
                           playerGender = playerGender, playerDateSignedUp = playerDateSignedUp, playerCurrentTeam = playerCurrentTeam,\
                           playerTeamLocation = playerTeamLocation, playerTeamManager = playerTeamManager, playerSalary = playerSalary,\
                           playerStartOfContract = playerStartOfContract, playerContractDuration = playerContractDuration,\
                           playerGamesPlayedThisYear = playerGamesPlayedThisYear, playerGamesWon = playerGamesWon, playerFutureGames = playerFutureGames,\
                           playerWeeksLeftInContract = playerWeeksLeftInContract, playerPrices = playerPrices)

@app.route("/clubs/<clubID>")
def clubDetails(clubID):
   print("Club Details")
   print(clubID)
   with sqlite3.connect('MoneyballDB.db') as conn:      
      cur = conn.cursor()
      cur.execute("SELECT * FROM Clubs WHERE club_name = ?", (clubID,))
      clubData = cur.fetchone()
   conn.close()
   
   return render_template('clubdetails.html', clubID = clubID, clubData = clubData)


if __name__ == "__main__":
   app.run(debug = True) #will run the flask app