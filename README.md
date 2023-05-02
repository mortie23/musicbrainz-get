# Get all artists songs from releases and featured artists

## Example of the JSON data response

```json
[
  {
    "recording_id": "74326370-65c8-40d2-8da8-6f8142da8972",
    "recording_title": "I Pray for You",
    "release_id": "3da32548-84cf-4812-90af-19e17d0c1839",
    "release_title": "It’s Almost Dry",
    "artists": ["Pusha T", "Labrinth", "Malice"]
  },
  {
    "recording_id": "702dd924-289d-4d29-b04e-e40d413bcd02",
    "recording_title": "Diet Coke",
    "release_id": "3f4a1e6e-75df-4697-bf4f-a07d88d384f8",
    "release_title": "Diet Coke",
    "artists": ["Pusha T"]
  }
]
```

## Load data into a pandas dataframe

TODO: Get the data from the JSON into two dataframes.
A list of songs and a list of artists featuring key pairs.

## Analysis

TODO: I think I will try to use this for connectedness of rappers through featuring:

[https://plotly.com/python/network-graphs/](https://plotly.com/python/network-graphs/)