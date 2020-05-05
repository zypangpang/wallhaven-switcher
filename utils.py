import string, urllib, random
from pathlib import Path
import os, subprocess, configparser, sys
from threading import Timer

from common import *

def get_config_file(create=False):
    home = str(Path.home())
    config_dir = os.path.join(home, '.config/wallhaven/')
    config_file = os.path.join(home, '.config/wallhaven/configs.ini')
    if os.path.isfile(config_file):
        return config_file
    elif create:
        image_folder = os.path.join(home, 'WallhavenImgs/')
        store_image_folder = os.path.join(home, 'Pictures/Wallpapers')
        subprocess.run(['mkdir', '-p', image_folder])
        subprocess.run(['mkdir', '-p', store_image_folder])
        subprocess.run(['mkdir', '-p', config_dir])
        config_str = DEFAULT_CONFIG_STRING.format(wallpaper_path=image_folder,
                                                  store_wallpaper_path=store_image_folder)
        with open(config_file, 'w') as f:
            f.write(config_str)
        return config_file
    return None


def read_config_file(config_file, section_name):
    configs = configparser.ConfigParser()
    try:
        configs.read(config_file)
        # myconfigs.read(CONFIG_FILE)
        t = configs[section_name]
        return configs, t
    except Exception as e:
        print("Config file format error or there is no section " + section_name)


def update_configs(configs, file_path):
    print("updating configs...")
    config_file = get_config_file()
    tconfigs, tsection = read_config_file(config_file, SECTION_NAME)
    tsection['page'] = configs[SECTION_NAME]['page']
    tsection['current wallpaper'] = configs[SECTION_NAME]['current wallpaper']
    with open(file_path, 'w') as f:
        tconfigs.write(f)


def clear_folder(folder_path):
    print("Are you sure you want to clear " + folder_path + ' ?\n Type y to confirm.')
    ok = input()
    if ok != 'y' and ok != 'Y':
        return
    try:
        (_, _, filenames) = next(os.walk(folder_path))
        for file in filenames:
            os.remove(os.path.join(folder_path, file))
    except Exception as e:
        print("Error occurred. Check the path and its contents.")
    else:
        print("Clear done.")
    exit(0)


def check_progress(maxval, results, myconfigs, rm=False):
    img_folder_path = myconfigs['wallpaper path']
    i = 1
    j = 0
    for img, error in results:
        print_progress(maxval, i)
        i = i + 1
        if error:
            print(f" !{img['id']} error: {error}")
            if rm:
                try:
                    os.remove(os.path.join(img_folder_path, img['id']))
                except:
                    pass
        else:
            j = j + 1
    return j


def print_progress(maxval, i):
    sys.stdout.write('\r')
    # the exact output you're looking for:
    sys.stdout.write("[%-24s] %d/%d" % ('=' * i, i, maxval))
    sys.stdout.flush()


def fetch_img(img, configs):
    def timer_handler(response):
        response.close()

    img_folder_path = configs['wallpaper path']
    try:
        filename = f'{img["id"]}.{img["file_type"].split("/")[1]}'
        with open(os.path.join(img_folder_path, filename), 'wb') as f:
            req = urllib.request.Request(img['path'], headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=TIME_OUT) as response:
                timer = Timer(TIME_OUT, timer_handler, [response])
                timer.start()
                try:
                    f.write(response.read())
                except:
                    timer.cancel()
                    f.close()
                    return img, 'Time out!'
                timer.cancel()
            # print(f"{img['name']} done.")
        return img, None
    except Exception as e:
        return img, e


def set_system_wallpaper(myconfigs, sys_name, wallpaper):
    # if myconfigs['hsetroot']=='1':
    #    wallpaper=hsetroot_process(wallpaper_path)
    if sys_name == 'xfce':
        xfcesetwallpaper = 'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitoreDP-1/workspace0/last-image -s'.split()
        xfcesetwallpaper.append(wallpaper)
        # print(xfcesetwallpaper)
        subprocess.run(xfcesetwallpaper)
    elif sys_name == 'gnome':
        gnomesetwallpaper = f'gsettings set org.gnome.desktop.background picture-uri "file://{wallpaper}"'
        subprocess.run(gnomesetwallpaper.split())
    elif sys_name == 'feh':
        feh_options = myconfigs['feh options']
        feh_set_wallpaper = f'feh {feh_options} {wallpaper}'
        print(feh_set_wallpaper)
        subprocess.run(feh_set_wallpaper.split())
    elif sys_name == 'hsetroot':
         wallpaper=hsetroot_process(wallpaper,myconfigs)
         command=f'hsetroot {myconfigs["hsetroot image option"]} {wallpaper}'
         print(command)
         subprocess.run(command.split())

        # image tweak for xfce lock screen
        # xfcesetwallpaper = 'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitoreDP-1/workspace0/last-image -s'.split()
        # xfcesetwallpaper.append(wallpaper)
        # print(xfcesetwallpaper)
        # subprocess.run(xfcesetwallpaper)

    print('successfully set wallpaper ' + wallpaper)


def random_string(string_length):
    """Generate a random string with the combination of lowercase and uppercase letters """
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(string_length))

def hsetroot_process(wallpaper_path,myconfigs):
    cur_path=os.path.join(myconfigs['wallpaper path'],CUR_WALLPAPER_NAME)
    #subprocess.run(['cp', wallpaper_path, cur_path])
    command=f'hsetroot {myconfigs["hsetroot image option"]} {wallpaper_path} {myconfigs["hsetroot tweak options"]} -write {cur_path}'
    print(command)
    subprocess.run(command.split())
    return cur_path
