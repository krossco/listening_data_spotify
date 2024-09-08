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
    """Get the Spotify client using SpotifyOAuth."""
    sp = Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=".cache-" + USERNAME  # cache path manages the refresh token automatically
    ))
    return sp

def fetch_recently_played(sp, limit=50):
    """Fetch recently played tracks from Spotify."""
    results = sp.current_user_recently_played(limit=limit)
    return results['items']

def connect_mysql():
    """Establish a connection to the MySQL database."""
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

def insert_recently_played(cnx, played_track):
    """Insert a track into the recently_played table in MySQL."""
    cursor = cnx.cursor()
    add_track = ("INSERT INTO tracks_recent "
                "(id, track_name, artist_name, played_at) "
                "VALUES (%s, %s, %s, %s)")
    id = played_track['track']['id']
    track_name = played_track['track']['name']
    artist_name = ", ".join([artist['name'] for artist in played_track['track']['artists']])
    played_at = datetime.strptime(played_track['played_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
    data_track = (id, track_name, artist_name, played_at)
    
    try:
        cursor.execute(add_track, data_track)
        cnx.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        cnx.rollback()
    finally:
        cursor.close()

def main():
    """Main function to fetch and store recently played tracks."""
    sp = get_spotify_client()
    recent_tracks = fetch_recently_played(sp)
    
    if not recent_tracks:
        print("No recent tracks found.")
        return
    
    cnx = connect_mysql()
    
    for track in recent_tracks:
        insert_recently_played(cnx, track)
    
    cnx.close()
    print("Data fetched and stored successfully.")

if __name__ == "__main__":
    main()
