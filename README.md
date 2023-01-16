# SoundLike
## How does it work?
1. Scrape WhoSampled for a given artist's samples.
2. Use Spotify API to find similar songs (recommendations) based on these songs.
3. YouTube links are provided for the found songs for easy and free listening.

## Usage

**Create & export spotify API keys**.\
[Learn more](https://spotipy.readthedocs.io/en/2.22.0/) (Go to 'Quick start').
```
export SPOTIPY_CLIENT_ID='your-spotify-client-id'
export SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
export SPOTIPY_REDIRECT_URI='your-app-redirect-url'
```

**Install requirements**
```
pip install -r requirements.txt
```

**Run program**
```
python scrape.py
```
Will run program. Search for any artist, and wait for YouTube links of songs that are similar to songs this artist has samples.


## Example
Examples can be found of [similar samples to J Dilla](./output/j_dilla_10.txt).
