import sqlite3
from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)


playerHeadings = ['Player Number','Player Name', 'Date of Birth', 'Gender', 'Date Signed-Up', 'Current Team', 'Salary (£k/Week)', 'Start of Contract', 'Contract Duration', 'Games Played This Year', 'Games Won', 'Future Games']
clubHeadings = ['Club ID', 'Club Name', 'Club Location', 'Club Manager']

def calculatePrices(playerSalary, playerGamesWon, playerWeeksLeftInContract, playerGamesPlayedThisYear, playerFutureGames):
   playerPrices = []
   baseWinRate = playerGamesWon / playerGamesPlayedThisYear
   basePrice = playerSalary * playerWeeksLeftInContract * baseWinRate
   playerPrices.append(basePrice)
   for i in range(len(playerFutureGames)):
      if playerFutureGames[i] == 'W':
         playerGamesWon += 1
         playerGamesPlayedThisYear += 1
         playerWeeksLeftInContract -= 1
      else:
         playerGamesPlayedThisYear += 1
         playerWeeksLeftInContract -= 1

      newWinRate = playerGamesWon / playerGamesPlayedThisYear
      priceAfterGame = playerSalary * playerWeeksLeftInContract * newWinRate
      playerPrices.append(priceAfterGame)
   return playerPrices

def getWeeksLeftInContract(playerStartOfContract, playerContractDuration):
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
   #Find the difference between them for the remaining weeks in players contract
   playerWeeksLeftInContract = playerWeeksInContract - playerWeeksPlayedOfContract
   return playerWeeksLeftInContract

@app.route("/home") #Route for the home page
@app.route("/")        
def home():
   print("Home")
   with sqlite3.connect('MoneyballDB.db') as conn:      
      cur = conn.cursor()
      cur.execute('''SELECT * FROM Players ORDER BY RANDOM() LIMIT 5''')
      data = cur.fetchall()
   conn.close()
   trendingPlayers = []
   for i in range(5):
      playerWeeksLeftInContract = getWeeksLeftInContract(data[i][7], data[i][8])
      trendingPlayers.append(calculatePrices((data[i][6])*1000, data[i][10], playerWeeksLeftInContract, data[i][9], data[i][11]))
      for j in range(len(trendingPlayers[i])):
         trendingPlayers[i][j] = round(trendingPlayers[i][j], 2)
   print(trendingPlayers)
   print(trendingPlayers[0])
   return render_template("home.html", name1 = data[0][1], name2 = data[1][1], name3 = data[2][1], name4 = data[3][1], name5 = data[4][1], player1 = trendingPlayers[0], player2 = trendingPlayers[1], player3 = trendingPlayers[2], player4 = trendingPlayers[3], player5 = trendingPlayers[4], playerToWatch = data[0])

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

@app.route("/players/<playerName>")
def playerDetails(playerName):
   print("Player Details")
   print(playerName)
   with sqlite3.connect('MoneyballDB.db') as conn:      
      cur = conn.cursor()
      cur.execute("SELECT * FROM Players WHERE player_name = ?", (playerName,))
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
   playerWeeksLeftInContract = getWeeksLeftInContract(playerStartOfContract, playerContractDuration)
   #Get price of player and price after each future game
   playerPrices = calculatePrices(playerSalary, playerGamesWon, playerWeeksLeftInContract, playerGamesPlayedThisYear, playerFutureGames)
   print(playerPrices)
   for i in range(len(playerPrices)):
      playerPrices[i] = round(playerPrices[i], 2)
   print(playerPrices)

   conn.close()
   return render_template('playerdetails.html', playerName = playerName, playerDoB = playerDoB,\
                           playerGender = playerGender, playerDateSignedUp = playerDateSignedUp, playerCurrentTeam = playerCurrentTeam,\
                           playerTeamLocation = playerTeamLocation, playerTeamManager = playerTeamManager, playerSalary = playerSalary,\
                           playerStartOfContract = playerStartOfContract, playerContractDuration = playerContractDuration,\
                           playerGamesPlayedThisYear = playerGamesPlayedThisYear, playerGamesWon = playerGamesWon, playerFutureGames = playerFutureGames,\
                           playerWeeksLeftInContract = playerWeeksLeftInContract, playerPrices = playerPrices)

@app.route("/clubs/<clubName>")
def clubDetails(clubName):
   print("Club Details")
   print(clubName)
   with sqlite3.connect('MoneyballDB.db') as conn:      
      cur = conn.cursor()
      cur.execute("SELECT * FROM Clubs WHERE club_name = ?", (clubName,))
      clubData = cur.fetchone()      
      cur.execute("SELECT player_name, salary, start_of_contract, contract_duration, games_played_this_year, games_won, future_games FROM Players WHERE current_team = ?", (clubName,))
      players = cur.fetchall()
      clubValues = [0,0,0,0,0,0]
      playerSalaries = []
      playerNames = []
      for player in players:
         playerSalaries.append((player[1] * 1000))
         playerNames.append(player[0])
         playerWeeksLeftInContract = getWeeksLeftInContract(player[2], player[3])
         playerPrices = calculatePrices((player[1] * 1000), player[5], playerWeeksLeftInContract, player[4], player[6])
         for i in range(len(playerPrices)):
            clubValues[i] = clubValues[i] + playerPrices[i]
      print(clubValues)

   conn.close()


   return render_template('clubdetails.html', clubName = clubName, clubData = clubData, clubValues = clubValues, playerSalaries=playerSalaries, playerNames=playerNames )


if __name__ == "__main__":
   app.run(debug = True) #will run the flask app