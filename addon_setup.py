import json
import os
import uuid
from pathlib import Path
from textwrap import indent

from downloader import download_songs
from filename import to_filename_format, get_recordname

import yaml

from texture_gen import generate_disc_textures

config = yaml.safe_load(open('config.yaml'))

def update_manifest_rp( rp_uuid ):
    current_dir = Path(__file__).parent.absolute()
    assets_dir = current_dir / config['ASSETS_DIR']
    export_dir = current_dir / config['EXPORT_DIR']
    addon_name = to_filename_format(config['ADDON_NAME'])

    manifest = json.load( open( assets_dir / "manifest_rp.json" ) )
    manifest['header']['name'] = f"{config['ADDON_NAME']} [RP]"
    manifest['header']['uuid'] = rp_uuid
    manifest['modules'][0]['uuid'] = str(uuid.uuid4())

    # print(json.dumps(manifest, indent=4))

    print(export_dir / config['ADDON_NAME'] / f"{addon_name}_rp")
    json.dump(
        manifest,
        open( export_dir / config['ADDON_NAME'] / f"{addon_name}_rp" / "manifest.json", "w" ),
        indent=4
    )

def update_manifest_bp( rp_uuid ):
    current_dir = Path(__file__).parent.absolute()
    assets_dir = current_dir / config['ASSETS_DIR']
    export_dir = current_dir / config['EXPORT_DIR']
    addon_name = to_filename_format(config['ADDON_NAME'])

    manifest = json.load( open( assets_dir / "manifest_bp.json" ) )
    manifest['header']['name'] = f"{config['ADDON_NAME']} [BP]"
    manifest['header']['uuid'] = str(uuid.uuid4())
    manifest['modules'][0]['uuid'] = str(uuid.uuid4())
    manifest['dependencies'][0]['uuid'] = rp_uuid

    print(export_dir / config['ADDON_NAME'] / f"{addon_name}_bp")
    json.dump(
        manifest,
        open( export_dir / config['ADDON_NAME'] / f"{addon_name}_bp" / "manifest.json", "w" ),
        indent=4
    )

def generate_disc_items( data_file ):

    current_dir = Path(__file__).parent.absolute()
    assets_dir = current_dir / config['ASSETS_DIR']
    export_dir = current_dir / config['EXPORT_DIR']
    addon_name = to_filename_format(config['ADDON_NAME'])


    discs = json.loads(open(data_file).read())['discs']

    for disc in discs: # TODO fix this shi

        if "artist" in disc:
            disc_artist = disc["artist"]
        else:
            disc_artist = "Various Artists"

        disc_item = json.loads( open( assets_dir / "record.example.json" ).read())

        record_name = get_recordname(disc_artist, disc['title'])
        disc_item["minecraft:item"]["description"][
            "identifier"] = f"{addon_name}:{to_filename_format(disc['artist'])}.{to_filename_format(disc['title'])}"
        disc_item["minecraft:item"]["components"]["minecraft:icon"] = record_name

        # print( json.dumps(disc['songs'], indent=4) )

        if len(disc["songs"]) == 1: # TODO tidy this up
            sound_name = get_recordname(disc_artist, disc['songs'][0]['title'])
            disc_item["minecraft:item"]["components"]["cdisc:record"]['sound'] = sound_name
            disc_item["minecraft:item"]["components"]["cdisc:record"]['author'] = disc_artist
            disc_item["minecraft:item"]["components"]["cdisc:record"]['title'] = disc['songs'][0]['title']
            disc_item["minecraft:item"]["components"]["cdisc:record"]['duration'] = 100 # TODO fix this

        print( json.dumps(disc_item, indent=4))

        print((export_dir / config['ADDON_NAME'] / f"{addon_name}_bp" / "items" /  f"{record_name}.json"))

        json.dump(
            disc_item,
            open(export_dir / config['ADDON_NAME'] / f"{addon_name}_bp" / "items" /  f"{record_name}.json", "w"),
            indent=4
        )

def create_addon( data_file ):

    current_dir = Path(__file__).parent.absolute()
    export_dir = current_dir / config['EXPORT_DIR']
    addon_name = to_filename_format(config['ADDON_NAME'])

    if not export_dir.exists():
        print("yum")
        export_dir.mkdir()
        ( export_dir / config['ADDON_NAME'] ).mkdir()

        ( export_dir / config['ADDON_NAME'] / f"{addon_name}_rp" ).mkdir()
        ( export_dir / config['ADDON_NAME'] / f"{addon_name}_rp" / "sounds" ).mkdir()
        ( export_dir / config['ADDON_NAME'] / f"{addon_name}_rp" / "sounds" / "records" ).mkdir()
        ( export_dir / config['ADDON_NAME'] / f"{addon_name}_rp" / "textures" ).mkdir()
        ( export_dir / config['ADDON_NAME'] / f"{addon_name}_rp" / "textures" / "items" ).mkdir()
        ( export_dir / config['ADDON_NAME'] / f"{addon_name}_rp" / "textures" / "items" / "records" ).mkdir()

        ( export_dir / config['ADDON_NAME'] / f"{addon_name}_bp" ).mkdir()
        ( export_dir / config['ADDON_NAME'] / f"{addon_name}_bp" / "items" ).mkdir()

    rp_uuid = str(uuid.uuid4())
    update_manifest_rp( rp_uuid )
    update_manifest_bp( rp_uuid )

    generate_disc_items( data_file )

    sound_export_dir = export_dir / config['ADDON_NAME'] / f"{addon_name}_rp" / "sounds" / "records"
    download_songs(data_file, sound_export_dir)
    generate_disc_textures( data_file )




create_addon( "songs.json" )




