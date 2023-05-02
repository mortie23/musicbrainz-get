# %%
import requests
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import plotly.io as pio


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
    # "Wu-Tang Clan",
    # "Styles P",
    # "Jadakiss",
    # "50 Cent",
    # "P Diddy",
    # "Notorious B.I.G.",
    # "Kanye West",
    # "Common",
    # "Talib Kweli",
    # "Mos Def",
]

# %%
all_artist = get_artists(artist_list)

# %%
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

# Create an empty directed graph using the DiGraph() function from NetworkX
G = nx.DiGraph()

# Create the graph from the dataframe
G = nx.from_pandas_edgelist(graph_df, source="source", target="target")
# Generate the positions of the nodes using the spring layout algorithm
pos = nx.spring_layout(G)
node_freq = dict(G.degree())

# filter nodes that only have one edge
filtered_nodes = [node for node in G.nodes() if node_freq[node] > 1]
# create a new graph with the filtered nodes and edges
H = G.subgraph(filtered_nodes)

# %%
for node in H.nodes():
    print(node_freq.values())
# %%

# Create the layout
layout = go.Layout(title="My Network Graph")

# Create the plotly figure
fig = go.Figure(
    data=go.Scatter(
        x=[],
        y=[],
        mode="markers",
        text=[],
        hovertemplate="%{text}",
    )
)

# Add the edges to the plotly figure
for edge in H.edges():
    fig.add_trace(
        go.Scatter(
            x=[pos[edge[0]][0], pos[edge[1]][0]],
            y=[pos[edge[0]][1], pos[edge[1]][1]],
            mode="lines",
        )
    )

# Add the nodes to the plotly figure
node_x = []
node_y = []
node_text = []
for node in H.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_text.append(node)
fig.add_trace(
    go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="middle center",
        marker=dict(size=[freq for freq in node_freq.values()], color="red"),
    )
)


# mode="markers",
# text=node_text,
# hovertemplate="%{text}",
# marker=dict(
#     size=[
#         freq for freq in node_freq.values()
#     ],  # set the node size based on frequency
#     color="blue",
# )

# Update the layout
fig.update_layout(layout)

# Assume the Plotly figure is stored in a variable called fig
# You can write it to an HTML file like this:
pio.write_html(fig, "my_plotly_figure.html")

# %%
