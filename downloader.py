from pathlib import Path
from typing import Any

import pafy
import json

import pytubefix
import ffmpeg
import yaml

from filename import get_recordname, to_filename_format

config = yaml.safe_load(open('config.yaml'))


def sounddef_record( artist, title ):
    return {
        f"{get_recordname(artist, title)}": {
            "category": "record",
            "max_distance": 64.0,
            "sounds": [
                {
                    "name": f"sounds/records/{to_filename_format(artist)}.{to_filename_format(title)}",
                    "stream": True,
                    "volume": 0.5
                }
            ]
        }
    }


def download_songs( data_file, export_dir: Path ):

    current_dir = Path(__file__).parent.absolute()
    assets_dir = current_dir / config['ASSETS_DIR']
    export_dir = current_dir / config['EXPORT_DIR']
    addon_name = to_filename_format(config['ADDON_NAME'])

    with open(data_file) as json_file:

        sound_definitions = json.load( open( assets_dir / "sound_definitions.json") )
        # print( json.dumps(sound_definitions, indent=4))


        discs = list(json.load(json_file)["discs"])

        for disc in discs:

            # Get artist name for the disc
            if "artist" in disc:
                disc_artist = disc["artist"]
            else:
                disc_artist = "Various Artists"

            # Get disc name
            disc_title = disc["title"]

            if len(disc["songs"]) > 0: # TODO change to multidisc check
                for song in disc["songs"]:
                    # print(json.dumps(song, indent=4))

                    # Get artist name for the song
                    if "artist" in song:
                        artist = song["artist"]
                    else:
                        artist = disc_artist

                    # Get song name
                    title = song["title"]



                    print(type(song["url"]))

                    if "url" in song:
                        if song["url"] is list: # TODO fix

                            for url in song["url"]:
                                pass #TODO add multidisc support

                        elif isinstance(song["url"], str):

                            download_song( song["url"], artist, title )
                            #
                            sound_definitions['sound_definitions'].update(sounddef_record(artist, title)) # TODO check if file already exists
                            # print(json.dumps(sound_definitions, indent=4))

            json.dump(
                sound_definitions,
                open( export_dir / config['ADDON_NAME'] / f"{addon_name}_rp" / "sounds" / "sound_definitions.json", "w"),
                indent=4
            )


def download_song( url: str, artist: str, title: str ):

    current_dir = Path(__file__).parent.absolute()
    export_dir = current_dir / config['EXPORT_DIR']
    addon_name = to_filename_format(config['ADDON_NAME'])

    yt = pytubefix.YouTube(url)
    stream = yt.streams.get_audio_only()

    filename = get_recordname(artist, title)
    print(filename)

    if not stream: raise RuntimeError(f"No audio stream found for {artist} and {title}")
    #
    # print(str(export_dir / f"{filename}.ogg"))
    ffmpeg.input(stream.url).output(
        str(export_dir / config['ADDON_NAME'] / f"{addon_name}_rp" / "sounds" / "records" / f"{filename}.ogg"),
        format="ogg",
        loglevel="error",
    ).run()  # TODO check if file already exists


if __name__ == "__main__":
    download_songs("songs.json", 'export')