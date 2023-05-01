import requests


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


# Example usage
artist_name = "2pac"
artist_id = search_artist(artist_name)
print(f"Artist ID for {artist_name}: {artist_id}")


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
            print(release_title)
            breakpoint()
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


print(get_artist_songs(artist_id=artist_id))
