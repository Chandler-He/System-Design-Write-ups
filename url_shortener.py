import sqlite3
import string
import random

from flask import Flask, request, redirect, render_template
app = Flask(__name__)

#connect to the database
conn = sqlite3.connect('url_shortener.db')
curs = conn.cursor()

#create the table if it doesn't exist
curs.execute(
    "Create table if not exists url_shortener (id integer primary key, url text, short_url text)"
)

def generate_short_url():
    """generate a random short code for the URL"""
    #characters to choose from
    chars = string.ascii_letters + string.digits
    #generate 8 random characters
    short_url = ''.join(random.choice(chars) for i in range(8))
    #check if the short code already exists
    curs.execute("select * from url_shortener where short_url = ?", (short_url,))
    #if it exists, generate another one
    if curs.fetchone():
        return generate_short_url()
    else:
        #if it doesn't exist, return the short code
        return short_url

def shorten_url(url):
    #shorten the URL and store it in the database

    #generate a short code for the url
    short_url = generate_short_url()
    #insert the URL and the short code into the database
    curs.execute("insert into url_shortener (url, short_url) values (?, ?)", (url, short_url))
    conn.commit()
    #return the short url
    return f"http://localhost:5000/{short_url}"

def expand_url(short_url):
    #lookup the original URL for the given short url
    curs.execute("select url from url_shortener where short_url = ?", (short_url,))
    result = curs.fetchone()
    if result:
        return result[0]
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        #get the URL from the form
        url = request.form.get('url')
        #shorten the URL
        short_url = shorten_url(url)
        #display the shortened URL
        return render_template('index.html', short_url=short_url)
    else:
        #display the form
        return render_template('index.html')

@app.route('/<short_url>')
def redirect_to_url(short_url):
    #lookup the original URL for the given short URL
    url = expand_url(short_url)
    if url:
        #redirect to the original URL
        return redirect(url)
    else:
        #if the URL doesn't exist, display an error message
        return f"URL not found for {short_url}"