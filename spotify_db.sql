CREATE DATABASE spotify_data;
USE spotify_data;

CREATE TABLE tracks_recent (
  play_id INT AUTO_INCREMENT PRIMARY KEY,
  id VARCHAR(255),
  track_name VARCHAR(255),
  artist VARCHAR(255),
  album VARCHAR(255),
  played_at DATETIME UNIQUE
);

SELECT * from tracks_recent
ORDER BY played_at;

-- DROP TABLE tracks_recent;
