import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import re


def check_birthday():
    """Checks if it's a valid format birthday."""
    while True:
        birthday = input("Enter your birthday in YYYY-MM-DD format: ")
        pattern = r"[1-2]\d{3}-[0-1]\d-[0-3]\d"
        it_is_correct = re.search(pattern, birthday)
        if it_is_correct:
            return birthday


def birthday_songs() -> list:
    """Enter your birthday and return a tuple with two lists where it has the song titles and the artists."""
    birthday = check_birthday()
    URL_BILLBOARD = f"https://www.billboard.com/charts/hot-100/{birthday}/"

    response = requests.get(url=URL_BILLBOARD).content
    soup = BeautifulSoup(response, "html.parser")

    song_titles = [song_title.get_text().replace("\n", "").replace("\t", "")
                   for song_title in soup.select("div li ul li h3")]

    artists = [artist.get_text().replace("\n", "").replace("\t", "")
               for artist in soup.find_all(name="span", class_="a-truncate-ellipsis-2line")]

    records = [f"{song_titles[i]} {artists[i]}" for i in range(len(song_titles))]
    return records


def spotipy_create_playlist(spotify_token, spotify_id, **kwargs):
    """Creates a playlist with the spotipy library."""
    scope = "playlist-modify-private"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=spotify_id,
                                                   client_secret=spotify_token,
                                                   scope=scope))

    data = sp.user_playlist_create(user=kwargs["user"],
                                   name=kwargs["playlist_name"],
                                   public=False,
                                   collaborative=False)
    return data["id"]


def search_songs(spotify_token, spotify_id, **kwargs):
    """From a given list make sure you, it searches for the first result.
    Returns a list with all the URI to identify each song."""
    scope = "user-read-private"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=spotify_id,
                                                   client_secret=spotify_token,
                                                   scope=scope))
    songs_uri = [sp.search(kwargs["list_songs"][i])["tracks"]["items"][0]["uri"]
                 for i in range(len(kwargs["list_songs"]))]
    return songs_uri


def add_songs_to_playlist(spotify_token, spotify_id, **kwargs):
    """With the created playlist ID add new items to the playlist."""
    scope = "playlist-modify-private"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=spotify_id,
                                                   client_secret=spotify_token,
                                                   scope=scope))
    sp.playlist_add_items(kwargs["playlist_id"], items=kwargs["list_songs"])


def main():
    spotify_ID = os.environ["SPOTIFY_CLIENT_ID"]
    spotify_token = os.environ["SPOTIFY_CLIENT_SECRET"]
    spotify_username = os.environ["SPOTIFY_USER"]
    id_playlist = spotipy_create_playlist(spotify_token=spotify_token,
                                          spotify_id=spotify_ID,
                                          user=f"{spotify_username}",
                                          playlist_name="Birthday Playlist")
    songs = birthday_songs()
    songs_uri = search_songs(spotify_token, spotify_ID, list_songs=songs)
    add_songs_to_playlist(spotify_token=spotify_token,
                          spotify_id=spotify_ID,
                          playlist_id=id_playlist,
                          list_songs=songs_uri)



if __name__ == "__main__":
    main()
