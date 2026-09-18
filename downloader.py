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


def add_songs( data_file, export_dir: Path ):

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
            disc_artist = get_disc_artist(disc)

            # Get disc name
            disc_title = disc["title"]

            if len(disc["songs"]) > 0: # TODO change to multidisc check (is it necessary tho?)

                for song in disc["songs"]:
                    # print("@ SONG")
                    # print(json.dumps(song, indent=4))
                    # print(json.dumps(song, indent=4))

                    # Get artist name for the song
                    if "artist" in song:
                        artist = song["artist"]
                    else:
                        artist = disc_artist

                    # Get song name
                    title = song["title"]



                    # print(type(song["url"]))

                    if "url" in song:
                        if isinstance(song["url"], list): # TODO make smarter
                            download_songs_yt(song["url"], artist, title)

                        elif isinstance(song["url"], str):
                            download_songs_yt( [song["url"]], artist, title )

                    elif "audio" in song:
                        pass # load from audio folder
                    else:
                        raise RuntimeError("Audio source for the disc was not specified")
                            #
                    sound_definitions['sound_definitions'].update(sounddef_record(artist, title)) # TODO check if file already exists
                            # print(json.dumps(sound_definitions, indent=4))

            json.dump(
                sound_definitions,
                open( export_dir / config['ADDON_NAME'] / f"{addon_name}_rp" / "sounds" / "sound_definitions.json", "w"),
                indent=4
            )


def get_disc_artist(disc) -> Any:
    if "artist" in disc:
        disc_artist = disc["artist"]
    else:
        disc_artist = "Various Artists"
    return disc_artist

def get_songs_from_audio( audios: list[str], artist: str, title: str  ):
    current_dir = Path(__file__).parent.absolute()
    audio_dir = current_dir / config['AUDIO_DIR']


    sources = []

    for audio in audios:
        audio_path = Path(audio_dir / audio)
        if audio_path.exists():
            source = ffmpeg.input( str(audio_path.resolve()) )
            sources.append(source)
        else:
            print(f"No audio found for {audio_path}")

    ffmpeg_from_sources(artist, sources, title)


def ffmpeg_from_sources(artist: str, sources: list[Any], title: str):
    current_dir = Path(__file__).parent.absolute()
    export_dir = current_dir / config['EXPORT_DIR']
    addon_name = to_filename_format(config['ADDON_NAME'])

    filename = get_recordname(artist, title)
    print(filename)

    joined = ffmpeg.concat(*sources, v=0, a=1)

    ffmpeg.output(
        joined,
        str(export_dir / config['ADDON_NAME'] / f"{addon_name}_rp" / "sounds" / "records" / f"{filename}.ogg"),
        # acodec='libopus',
        format='ogg',
        ac=1,
        ab="128k",
        ar="44100",
        # loglevel="error",
    ).run()  # TODO check if file already exists


def download_songs_yt( urls: list[str], artist: str, title: str ):

    current_dir = Path(__file__).parent.absolute()
    export_dir = current_dir / config['EXPORT_DIR']
    addon_name = to_filename_format(config['ADDON_NAME'])

    sources = []

    for url in urls:
        yt = pytubefix.YouTube(url)
        audio_stream = yt.streams.get_audio_only()
        if audio_stream:
            source = ffmpeg.input(audio_stream.url)
            sources.append(source)
        else:
            print(f"No audio found for {url}")

    ffmpeg_from_sources(artist, title, sources)


if __name__ == "__main__":
    pass
    # download_songs("songs.json", 'export')