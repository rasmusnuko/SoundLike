import my_headers
import requests, json, re
from bs4 import BeautifulSoup
from youtubesearchpython import VideosSearch

# SPOTIPY
import spotipy
from spotipy.oauth2 import SpotifyOAuth
scope = "user-library-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

RECOMMENDATIONS_PER_ID_LIMIT = 10


def get_response(url):
    response = requests.get(url, headers=my_headers.header)
    if not response.ok:
        print(f"Status code: {response.status_code}, url: {url}")
    return response.text


def find_artist_url():
    # Get user input
    query = input("Search: ")

    # Scrape artist query from https://whosampled.com
    url = f"https://www.whosampled.com/ajax/search/?q={query}&_=1672998766384"
    query_json = get_response(url)
    query_dict = json.loads(query_json)

    # Make artist url dict
    artists = {i+1: entry['url'] for i, entry in enumerate(query_dict["artists"])}

    # Retry if no artist found
    if len(artists) == 0:
        print("No such artist found. Try again.")
        return find_artist_url()

    # Present found artists for user
    for i in artists:
        print(f"{i}: {artists[i]}")

    # Ensure choice is valid
    choice = int(input("Choose: "))
    while not choice in artists:
        choice = int(input("enter valid choice: "))

    # Make and return artist url
    return f"http://whosampled.com{artists[choice]}"


def samples_from_artist_url(artist_url):
    page = requests.get(artist_url, headers=my_headers.header)
    soup = BeautifulSoup(page.text, "html.parser")

    results = []
    for sample in soup.find_all(class_ = "connectionName playIcon"):
        results.append(f"https://whosampled.com{sample['href']}")

    return results


def extract_sample_yt_from_url(url):
    # Get HTML
    page = requests.get(url, headers=my_headers.header)
    soup = BeautifulSoup(page.text, "html.parser")

    # Get YouTube watch ID
    dirty = soup.find_all(class_ = "embed-placeholder youtube-placeholder")[1].find('img')
    first_step = re.sub('^.*vi/', '', str(dirty))
    second_step = re.sub('/.*', '', first_step)

    # Make YT URL and return it
    return f"https://youtube.com/watch/{second_step}"


def yt_urls_from_samples(sample_urls):
    results = []
    for url in sample_urls:
        try:
            yt_url = extract_sample_yt_from_url(url)
            results.append(yt_url)
        except:
            print(f"Might use spotify: {url}")

    return results


def extract_sample_info_from_url(url):
    # Get HTML
    page = requests.get(url, headers=my_headers.header)
    soup = BeautifulSoup(page.text, "html.parser")

    # Get and clean song data
    artists = soup.find_all(class_ = "sampleTrackArtists")[1].text.strip().replace('%27', "'").split(" feat. ")
    title = soup.find_all(class_ = "trackName")[1]['href'].split('/')[2].replace('-', ' ').replace('%27', "'")

    #print({'artists': artists, 'title': title})
    return {'artists': artists, 'title': title} 


def track_info_from_samples(sample_urls):
    results = []
    for url in sample_urls:
        results.append(extract_sample_info_from_url(url))

    return results


def extract_spotify_id_from_track_info(track_info):
    results = sp.search(q=f"track:{track_info['title']}", type="track")
    assert results

    for item in results['tracks']['items']:
        for artist in item['artists']:
            for a in track_info['artists']:
                if artist['name'] in a or a in artist['name']:
                    return item['id']

    return None

def spotify_ids_from_track_info(track_info):
    results = []
    for track in track_info:
        spotify_id = extract_spotify_id_from_track_info(track)
        if spotify_id != None:
            results.append(spotify_id)

    return list(set(results))


def extract_similar_tracks_from_spotify_id(spotify_id):
    recom_results = sp.recommendations(seed_tracks=[spotify_id],
                                       limit=RECOMMENDATIONS_PER_ID_LIMIT)
    assert recom_results

    results = []
    for track in recom_results['tracks']:
        artists = []
        for artist in track['artists']:
            artists.append(artist['name'])
        
        results.append({'artists': artists, 'title': track['name']})
    
    return results


def similar_tracks_from_spotify_ids(spotify_ids):
    similar_tracks = []
    for id in spotify_ids:
        recommndations_from_id = extract_similar_tracks_from_spotify_id(id)
        similar_tracks.extend(recommndations_from_id)

    return similar_tracks


def extract_youtube_id_from_track_info(similar_track):
    result = VideosSearch(query=f"{similar_track['artists'][0]} {similar_track['title']}", limit=1)
    return result.result()['result'][0]['id']

def youtube_ids_from_similar_tracks(similar_tracks):
    youtube_ids = []
    for similar_track in similar_tracks:
        youtube_ids.append(extract_youtube_id_from_track_info(similar_track))
    
    return youtube_ids


def print_all(iter, prefix=''):
    #for i in iter:
    for i in set(iter):
        print(f"{prefix}{i}")

def output_to_file(iter, filename, prefix=''):
    with open(filename, "w+") as f:
        for i in set(iter):
            f.write(f'{prefix}{i}\n')



def main():
    artist_url     = find_artist_url()
    sample_urls    = samples_from_artist_url(artist_url)
    track_info     = track_info_from_samples(sample_urls)
    spotify_ids    = spotify_ids_from_track_info(track_info)
    similar_tracks = similar_tracks_from_spotify_ids(spotify_ids)
    youtube_ids    = youtube_ids_from_similar_tracks(similar_tracks)
    output_to_file(youtube_ids, "output/j_dilla_10.txt", "https://youtube.com/watch/")

if __name__ == "__main__":
    main()
