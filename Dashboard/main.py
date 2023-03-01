from DatabaseAccess import *
import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('MoneyballDB.db')
    conn.row_factory = sqlite3.Row
    return conn
@app.route("/home") #Route for the about us page
@app.route("/")        
def home():
   print("Home")
   with sqlite3.connect('MoneyballDB.db') as conn:      
      cur = conn.cursor()
      cur.execute("SELECT * FROM Players")
      data = cur.fetchall()
      print(data[0])
   return render_template("home.html", data = data[0])

@app.route("/players") #Route for the players page        
def players():
   playerHeadings = ['Player Name', 'Date of Birth', 'Gender', 'Date Signed-Up', 'Current Team', 'Team Location', 'Team Manager', 'Salary (£k/Week)', 'Start of Contract', 'Contract Duration', 'Games Played This Year', 'Games Won', 'Future Games']
   print("Players")
   return render_template("players.html", playerHeadings)

@app.route("/clubs") #Route for the clubs page        
def clubs():
   clubHeadings = ['Team Name', 'Team Location', 'Team Manager']
   print("Clubs")
   return render_template("clubs.html", clubHeadings)

if __name__ == "__main__":
   app.run(debug = True) #will run the flask app