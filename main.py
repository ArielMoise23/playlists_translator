import spotipy
from spotipy.oauth2 import SpotifyOAuth
import lyricsgenius
from googletrans import Translator
from fpdf import FPDF
import re

# 1. Setup Spotify API authentication
SPOTIPY_CLIENT_ID = ''
SPOTIPY_CLIENT_SECRET = ''
SPOTIPY_REDIRECT_URI = 'https://i.pinimg.com/736x/e5/b9/81/e5b98110fcd62d6ebe0e636262170175.jpg'
SCOPE = 'playlist-read-private'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=SCOPE))

# 2. Genius API for Lyrics
genius = lyricsgenius.Genius("")

# 3. Translator for lyrics translation
translator = Translator()

# 4. FPDF setup for PDF generation
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)

def fetch_playlist_tracks(playlist_id):
    # Fetches tracks from the given playlist ID
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    songs = []

    for idx, item in enumerate(tracks):
        track = item['track']
        song_info = {
            "name": track['name'],
            "artist": track['artists'][0]['name'],
            "lyrics": None,
            "translated_lyrics": None
        }
        songs.append(song_info)
    return songs

def fetch_lyrics(song_name, artist_name):
    # Fetch lyrics from Genius
    try:
        song = genius.search_song(song_name, artist_name)
    except Exception as e:
        print("An error occurred during fetching song lyrics:", str(e))
        return None
    return song.lyrics if song else None

def translate_lyrics(lyrics):
    # Translate lyrics to English
    lyrics_modified = remove_brackets_and_content(lyrics)
    try:
        translation = translator.translate(lyrics_modified, dest='en')
    except Exception as e:
        error = f"An error occurred during translation: {str(e)}"
        print(error)
        return error
    return translation.text


def create_pdf(song_title, original_lyrics, translated_lyrics):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.add_font('DejaVu', '', 'FlawsomeRegularRegular-PVrJ7.ttf', uni=True)  # Load your font
    pdf.set_font('DejaVu', '', 12)  # Set the font

    # Song title
    pdf.cell(200, 10, txt=song_title, ln=True, align="C")

    # Split the lyrics into lines
    original_lines = original_lyrics.split('\n')
    translated_lines = translated_lyrics.split('\n') if translated_lyrics else ''

    # Combine the original and translated lines
    for translated_line, original_line in zip(translated_lines, original_lines):
        # Add the translated line
        pdf.multi_cell(0, 10, txt=translated_line)
        
        # Add the original line
        pdf.multi_cell(0, 10, txt=original_line)
        
        # Add a blank line for separation (optional)
        pdf.cell(0, 5, ln=True)

    # Save the PDF
    try:
        pdf.output(f"{song_title.replace(' ', '_').replace('/', '')}.pdf")
    except Exception as e:
        print("An error occurred during creating PDF file:", str(e))
        return None


def remove_brackets_and_content(input_string):
    # Use regex to remove all occurrences of [] and their contents
    result = re.sub(r'\[.*?\]', '', input_string)
    return result.replace('\n', ' \n ')

def main():
    playlist_id = "5clhQH1nhrSaYTRMNO0C5L"  # Spotify playlist ID

    # 1. Fetch songs from the playlist
    songs = fetch_playlist_tracks(playlist_id)

    for song in songs:
        print(f"Fetching lyrics for {song['name']} by {song['artist']}")
        
        # 2. Fetch lyrics from Genius
        lyrics = fetch_lyrics(song['name'], song['artist'])
        song['lyrics'] = lyrics or "Lyrics not found"

        if lyrics:
            # 3. Translate lyrics
            song['translated_lyrics'] = translate_lyrics(lyrics)

    # 4. Generate the PDF
    for song in songs:
        lyrics = remove_brackets_and_content(song['lyrics'])
        create_pdf(f'{song['name']} by {song['artist']}', lyrics, song['translated_lyrics'])
        
    # song_title, original_lyrics, translated_lyrics

if __name__ == "__main__":
    main()
