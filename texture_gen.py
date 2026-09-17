import json
from pathlib import Path
import random

from PIL import Image, ImageEnhance, ImageOps

import yaml

from filename import to_filename_format, get_recordname

config = yaml.safe_load(open('config.yaml'))

def itemtex_record( artist, title ):
    return {
        f"{get_recordname(artist,title)}": {
            "textures": f"textures/items/records/record_{to_filename_format(artist)}.{to_filename_format(title)}",
        }
    }

def generate_disc( color = "#404040" ):
    current_dir = Path(__file__).parent.absolute()
    assets_dir = current_dir / config['ASSETS_DIR']

    disc_img = Image.open(assets_dir / 'blank_music_disc.png' ).convert('L')

    # output = Image.blend(disc_img, color_layer, 0.5)
    # print(disc_img.mode)
    output = ImageOps.colorize(disc_img, (0,0,0,0), color).convert('RGBA')
    print(output.mode)

    # output.save('output.png', 'PNG')
    return output

def generate_label( color1, color2 ):
    current_dir = Path(__file__).parent.absolute()
    assets_dir = current_dir / config['ASSETS_DIR']

    types = ['cross', 'eye', 'flat', 'music', 'parallel', 'star']

    selected_type = random.choice(types)

    label_top = Image.open(assets_dir / 'disc_labels' / f'{selected_type}_label_top.png').convert('L')
    colored_top = ImageOps.colorize(label_top, (0,0,0,0), color1).convert('RGBA')
    colored_top.putalpha(label_top.getchannel(0))

    label_bottom = Image.open(assets_dir / 'disc_labels' / f'{selected_type}_label_bottom.png').convert('L')
    colored_bottom = ImageOps.colorize(label_bottom, (0, 0, 0, 0), color2).convert('RGBA')
    colored_bottom.putalpha(label_bottom.getchannel(0))

    colored_bottom.paste(colored_top, (0, 0), label_top)

    return colored_bottom



def generate_disc_textures( data_file ):
    current_dir = Path(__file__).parent.absolute()
    assets_dir = current_dir / config['ASSETS_DIR']
    export_dir = current_dir / config['EXPORT_DIR']
    addon_name = to_filename_format(config['ADDON_NAME'])

    item_texture = json.load( open(assets_dir / "item_texture.json") )
    # print(json.dumps( item_texture, indent=4 ))

    with open(data_file) as json_file:
        discs = list(json.load(json_file)["discs"])

        for disc in discs:
            print( json.dumps(disc, indent=4) )

            label_colors = disc['label_colors']
            disc_colors = disc['disc_colors']


            color1 = label_colors[0]

            if len(label_colors) <= 1:
                color2 = color1
            else:
                color2 = label_colors[1]

            if len(disc_colors) == 0:
                disc_color = "#404040"
            else:
                disc_color = disc_colors[0]

            disc_img = generate_disc( disc_color ).convert('RGBA')
            label_img = generate_label( color1, color2 ).convert('RGBA')

            disc_img.paste(label_img, (0, 0), label_img) #TODO one of label templates needs (0,-1)
            disc_img.save(
                export_dir / config['ADDON_NAME'] / f"{addon_name}_rp" / "textures" / "items" / "records" / f'record_{to_filename_format(disc['artist'])}.{to_filename_format(disc['title'])}.png'
            )

            item_texture["texture_data"].update(itemtex_record(disc["artist"], disc["title"]))

        json.dump(
            item_texture,
            open(export_dir / config['ADDON_NAME'] / f"{addon_name}_rp" / "textures" / "item_texture.json", "w"),
            indent=4
        )


if __name__ == "__main__":
    generate_disc_textures("songs.json")
