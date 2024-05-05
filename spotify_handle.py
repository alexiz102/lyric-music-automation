import os
import spotdl

client_id = "Client ID"
client_secret = "Client Secret"

output_file_path = 'audio'

spotdl.SpotifyClient.init(client_id=client_id, client_secret=client_secret)


def download_song_via_spotdl(song_name):
    song_info = spotdl.Song.from_search_term(song_name)
    print("Downloading Song...")
    song_file = spotdl.Downloader().download_song(song_info)[1]
    print("Song Download Complete")
    new_file_path = os.path.join(output_file_path, "audio.mp3")
    if os.path.exists(new_file_path):
        os.remove(new_file_path)
    os.rename(song_file, new_file_path)

