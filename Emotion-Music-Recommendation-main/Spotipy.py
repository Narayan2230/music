import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time
import os

# Setup Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id='f0f5b4e1862846c39953077d37c423e4',
    client_secret='34ecccbea564456ebf34cd435f9dabf6'
))

# Emotion playlist mappings
emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}
music_dist = {
    0: "0l9dAmBrUJLylii66JOsHB",  # Angry Playlist
    1: "1n6cpWo9ant4WguEo91KZh",  # Disgusted Playlist
    2: "4cllEPvFdoX6NIVWPKai9I",  # Fearful Playlist
    3: "0deORnapZgrxFY4nsKr9JA",  # Happy Playlist
    4: "4kvSlabrnfRCQWfN0MgtgA",  # Neutral Playlist
    5: "1n6cpWo9ant4WguEo91KZh",  # Sad Playlist
    6: "37i9dQZEVXbMDoHDwVN2tF"   # Surprised Playlist
}

# Create folder if not exists
os.makedirs("songs", exist_ok=True)

# Fetch all track IDs from a playlist
def getTrackIDs(playlist_id):
    track_ids = []
    try:
        playlist = sp.playlist(playlist_id)
        for item in playlist['tracks']['items']:
            track = item['track']
            if track:  # Check if track is not None
                track_ids.append(track['id'])
    except spotipy.exceptions.SpotifyException as e:
        print(f"Error fetching playlist {playlist_id}: {e}")
    return track_ids

# Extract track features including the Spotify URL
def getTrackFeatures(track_id):
    track_info = sp.track(track_id)
    name = track_info['name']
    album = track_info['album']['name']
    artist = track_info['album']['artists'][0]['name']
    url = track_info['external_urls']['spotify']
    return [name, album, artist, url]

# Save playlist tracks to CSV by emotion
def saveEmotionPlaylist(emotion_id):
    emotion = emotion_dict[emotion_id]
    playlist_id = music_dist[emotion_id]
    print(f"Fetching playlist for emotion: {emotion}")

    track_ids = getTrackIDs(playlist_id)
    track_list = []

    for track_id in track_ids:
        time.sleep(0.3)  # Avoid hitting rate limits
        track_data = getTrackFeatures(track_id)
        track_list.append(track_data)

    # Save to CSV with additional URL column
    df = pd.DataFrame(track_list, columns=['Name', 'Album', 'Artist', 'URL'])
    df.to_csv(f'songs/{emotion.lower()}.csv', index=False)
    print(f"{emotion} CSV saved.")

# Call the saveEmotionPlaylist function for each emotion
saveEmotionPlaylist(0)  # Angry
saveEmotionPlaylist(1)  # Disgusted
saveEmotionPlaylist(2)  # Fearful
saveEmotionPlaylist(3)  # Happy
saveEmotionPlaylist(4)  # Neutral
saveEmotionPlaylist(5)  # Sad
saveEmotionPlaylist(6)  # Surprised
