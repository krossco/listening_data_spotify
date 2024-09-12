# listening_data_spotify

Objective: 
Using Spotify's API to fetch song listening data, storing in a database on a regular cadence to then analyse listening data after enough data collected. End goal to automate this to run several times a day. 

Work in progress - not yet complete.

Steps taken

1. Create app via Spotify API Developer: https://developer.spotify.com/documentation/web-api. Set URI as localhost for dev 

2. Create virtual environment, then install dependancies - pip install spotipy pandas matplotlib mysql-connector-python

3. Clone repo, run db file to create database

4. Input the following into an .env file:  
    - SPOTIFY_CLIENT_ID='xxxxxxxxxxxxxxxxxxxxx'
    - SPOTIFY_CLIENT_SECRET='xxxxxxxxxxxxxxxxxxxxx'
    - SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
    - SPOTIFY_REFRESH_TOKEN= this will be generated when your spotify credentials are authorised and a .cache file is generated.
    - SPOTIFY_USERNAME= your spotify user name here
    - MYSQL_HOST= where your database is hosted
    - MYSQL_USER= username for database
    - MYSQL_PASSWORD= database password
    - MYSQL_DATABASE= database name

5. Run script - python autoscript.py

