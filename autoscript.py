import os
import json
import mysql.connector
from mysql.connector import errorcode
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Spotify credentials
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
USERNAME = os.getenv('SPOTIFY_USERNAME')

# MySQL credentials
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

# Scope for reading recently played tracks
SCOPE = 'user-read-recently-played'

def get_spotify_client():
    # Fetch spotify creds to authorise connection
    sp = Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=".cache-" + USERNAME  
    ))
    return sp


def fetch_recently_played(sp, limit=50):
    # Fetching recently played spotify songs - limited to 50 due to Spotify API
    results = sp.current_user_recently_played(limit=limit)
    return results['items']

def connect_mysql():
    # connect to mysql database
    try:
        cnx = mysql.connector.connect(
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            host=MYSQL_HOST,
            database=MYSQL_DATABASE
        )
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your MySQL username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        exit(1)

def track_exists(cnx, played_at):
    cursor = cnx.cursor()
    query = "SELECT 1 FROM tracks_recent WHERE played_at = %s"
    cursor.execute(query, (played_at,))
    result = cursor.fetchone()
    cursor.close()
    return result is not None


def insert_tracks_recent(cnx, played_track):
    """Insert a track into the tracks_recent table in MySQL if it doesn't already exist."""
    cursor = cnx.cursor()

    # Extract track details from the played_track dictionary
    id = played_track['track']['id']
    track_name = played_track['track']['name']
    artist = ", ".join([artist['name'] for artist in played_track['track']['artists']])
    album = played_track['track']['album']['name']
    played_at = datetime.strptime(played_track['played_at'], '%Y-%m-%dT%H:%M:%S.%fZ')

    # Check if the track already exists in the database
    if track_exists(cnx, played_at):
        print(f"Skipping track played at {played_at}, already exists.")
        return


    # Insert the track if it doesn't already exist
    add_track = ("""
        INSERT IGNORE INTO tracks_recent (id, track_name, artist, album, played_at)
        VALUES (%s, %s, %s, %s, %s)
    """)
    data_track = (id, track_name, artist, album, played_at)

    try:
        cursor.execute(add_track, data_track)
        cnx.commit()  # Commit the transaction
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        cnx.rollback()  # Roll back in case of an error
    finally:
        cursor.close()

def main():
    sp = get_spotify_client()
    recent_tracks = fetch_recently_played(sp)
    
    if not recent_tracks:
        print("No recent tracks found.")
        return
    
    cnx = connect_mysql()
    
    for track in recent_tracks:
        insert_tracks_recent(cnx, track)
    
    cnx.close()
    print("Data fetched and stored successfully.")

if __name__ == "__main__":
    main()
