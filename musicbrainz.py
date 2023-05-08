# %%
import requests
import pandas as pd


# %%
def search_artist(artist_name):
    # Set up the MusicBrainz API endpoint and query parameters
    endpoint = "https://musicbrainz.org/ws/2/artist"
    params = {"query": artist_name, "fmt": "json"}

    # Send the HTTP request to the API and get the response
    response = requests.get(endpoint, params=params)

    # Parse the JSON response and extract the artist ID
    results = response.json()
    if len(results["artists"]) > 0:
        artist_id = results["artists"][0]["id"]
        return artist_id
    else:
        return None


def get_artist_songs(artist_id):
    # Set up the MusicBrainz API endpoint and query parameters
    endpoint = f"https://musicbrainz.org/ws/2/release?artist={artist_id}&inc=recordings+artist-credits&fmt=json"
    params = {"offset": 0, "limit": 100}
    # Send the HTTP request to the API and get the response
    response = requests.get(endpoint)

    # Parse the JSON response and extract the song titles
    results = response.json()
    recordings = []
    while True:
        response = requests.get(endpoint, params=params)
        # Parse the JSON response and extract the recordings for the release
        results = response.json()
        for release in results["releases"]:
            release_title = release["title"]
            release_id = release["id"]
            for medium in release["media"]:
                for track in medium["tracks"]:
                    recording_id = track["recording"]["id"]
                    recording_title = track["recording"]["title"]
                    artists = []
                    for artist_credit in track["recording"]["artist-credit"]:
                        artist = artist_credit["artist"]["name"]
                        artists.append(artist)
                    recordings.append(
                        {
                            "recording_id": recording_id,
                            "recording_title": recording_title,
                            "release_id": release_id,
                            "release_title": release_title,
                            "artists": artists,
                        }
                    )

        # If there are more results, update the offset and make another request
        count = results["release-count"]
        limit = params["limit"]
        offset = params["offset"] + limit
        if offset >= count:
            break
        params["offset"] = offset
    return recordings


def get_artist_featuring(
    artist_name: str,
) -> pd.DataFrame:
    """Get artists songs as a dataframe

    Args:
        artist_name (str): The name of an artist

    Returns:
        pd.DataFrame: dataframe with the list of songs and featuring artists
    """
    artist_id = search_artist(artist_name)
    print(f"Artist ID for {artist_name}: {artist_id}")
    songs = get_artist_songs(artist_id=artist_id)
    df = pd.DataFrame(songs)
    df["artist"] = df["artists"].apply(lambda x: x[0])
    return df.explode("artists")


# %%
def get_artists(
    artist_list: list,
) -> pd.DataFrame:
    base_df = pd.DataFrame(
        columns=[
            "recording_id",
            "recording_title",
            "release_id",
            "release_title",
            "artists",
            "artist",
        ]
    )
    for artist in artist_list:
        artist_df = get_artist_featuring(artist)
        print(len(artist_df))
        base_df = pd.concat([base_df, artist_df], ignore_index=True)
        print(len(base_df))
    return base_df


# %%
artist_list = [
    "Jay-Z",
    "Nas",
    "Wu-Tang Clan",
    "Redman",
    "The LOX",
    "Styles P",
    "Jadakiss",
    "50 Cent",
    "Diddy",
    "Notorious B.I.G.",
    "Kanye West",
    "Common",
    "Talib Kweli",
    "Mos Def",
    "2pac",
    "Snoop Dogg",
    "Dr Dre",
    "Kurupt",
    "Warren G",
    "Note Dogg",
    "Tha Dogg Pound",
    "Daz Dillinger",
]

# %%
all_artist = get_artists(artist_list)

# %%
# Remove records where the artist in the artist credit list is the recording artist
# This is so in the network graph does not contain self loop edges
mask = all_artist["artist"] != all_artist["artists"]

# apply the mask to the DataFrame to keep only the desired rows
all_artist = all_artist[mask]


# %%
# Remove duplicates
# Drop duplicates by the columns 'release_title', 'artist', and 'artists'
graph_df = all_artist.drop_duplicates(subset=["recording_title", "artist", "artists"])

# Keep only the columns 'release_title', 'artist', and 'artists'
graph_df = graph_df.loc[:, ["artist", "artists"]]
# Rename the columns "artist" to "source" and "artists" to "target"
graph_df = graph_df.rename(columns={"artist": "source", "artists": "target"})

# %%
# Assuming your DataFrame is named 'dataframe'
result = graph_df.groupby(["source", "target"]).size().reset_index(name="edge_count")
result = result[result["edge_count"] > 1]

# %%
result.to_csv("result.csv", index=False)

# %%
