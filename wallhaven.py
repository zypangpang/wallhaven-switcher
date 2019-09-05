#!/usr/bin/env python
import configparser
import urllib.request
from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
import time
import os, sys, string, random, subprocess, argparse, copy

DEFAULT_CONFIG_STRING = '''
[DEFAULT]
wallpaper path = /tmp/wallpapers 
baseurl = https://wallhaven.cc/search
categories = 110
purity = 100
sorting = random
order = desc
width = 2560
height = 1440
page = 1
seed = Zypang
current wallpaper = -1
system = xfce

[ZYPANG]
wallpaper path = {wallpaper_path}
system = gnome
'''

THREAD_NUM = 10
IMG_THREAD_NUM = 7
DEFAULT_CONFIG_PATH='./configs.ini'
CONFIG_FILE = './configs.ini'
SECTION_NAME = 'ZYPANG'
ITEM_PER_PAGE = 24
SEED_LEN = 6
# SYS_NAME='xfce'

myconfigs = None
noset = False
savecounter=True

def main():
    global myconfigs, noset,CONFIG_FILE,SECTION_NAME,savecounter,INIT_IMG_FOLDER
    args = parse_cmd_args()
    if args.init:
        wallpaper_path=args.init
        config_str=DEFAULT_CONFIG_STRING.format(wallpaper_path=wallpaper_path)
        with open('configs.ini','w') as f:
            f.write(config_str)
        print(f'Init success. \nWallpaper path is {wallpaper_path}. \nSystem is set to gnome. Change it to your '
              f'DE if necessary. Now supported DE is "xfce" and "gnome".\n:-) Have fun!')
        exit(0)

    if args.config:
        CONFIG_FILE = args.config
    if not os.path.isfile(CONFIG_FILE):
        print('Config file does not exist. You can use "--init WALLPAPER_FOLDER_PATH" to get a '
              'default config, or you can specify a config file path with "-c".\n Exit.')
        exit(0)

    configs = configparser.ConfigParser()
    configs.read(CONFIG_FILE)

    if args.reset:
        if args.reset == 0:
            configs[SECTION_NAME]['current wallpaper'] = '0'
        if args.reset == 1:
            configs[SECTION_NAME]['current wallpaper'] = '0'
            configs[SECTION_NAME]['page'] = '1'
        update_configs(configs, CONFIG_FILE)
        print('Exit.')
        exit(0)

    myconfigs = copy.deepcopy(configs[SECTION_NAME])
    # IMG_FOLDER_PATH=myconfigs['wallpaper path']
    # SEED = myconfigs['seed']
    # SYS_NAME = myconfigs['system']
    if args.image_path:
        savecounter=False
        myconfigs['current wallpaper'] = '0'
        print("You have changed the image path, this time it will choose the first image from the folder as the "
              "wallpaper. If you want to change it permanently, please change the config file.")
        myconfigs['wallpaper path'] = args.image_path
    if args.wallpaper:
        savecounter=False
        myconfigs['current wallpaper']=str(args.wallpaper)

    if args.categories:
        myconfigs['categories'] = args.categories
        noset = True

    if args.purity:
        myconfigs['purity'] = args.purity
        noset = True
        print("ATTENTION: You have changed the purity. Make sure you also changed the image_path, or newly downloaded "
              "images will reside in the same folder with your wallpapers and can be picked next time!")
    if args.page:
        savecounter=False
        myconfigs['page'] = str(args.page)
        noset = True
    if args.random:
        savecounter=False
        myconfigs['seed'] = random_string(SEED_LEN)
        myconfigs['page'] = '1'
        noset = True
    if args.noset:
        noset = True
    if args.NSFW:
        print("ATTENTION: You have chosen THE NSFW OPTION. Make sure you also changed the image_path, "
              "or newly downloaded images will reside in the same folder with your wallpapers and "
              "can be picked next time!")
        noset = True
        myconfigs['purity'] = '001'
        myconfigs['categories'] = '011'

    if noset:
        print("You specified some options. Will just download images and not change the wallpaper.")
        get_new_wallpapers()
    else:
        print("Changing the wallpaper...")
        set_wallpaper()

    if args.save:
        print("ATTENTION: You are going to save the configs specified by the command arguments. Make sure that the "
              "configs are WHAT YOU REALLY WANT.")
        configs[SECTION_NAME] = myconfigs
    elif savecounter:
        configs[SECTION_NAME]['current wallpaper'] = myconfigs['current wallpaper']
        configs[SECTION_NAME]['page'] = myconfigs['page']
    update_configs(configs, CONFIG_FILE)

    print('Exit.')


def parse_cmd_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--image_path", help="The folder path to the wallpaper image."
                                                   " If not given, use the path in config file")
    parser.add_argument("-c", "--config",
                        help="The config file path. If not given, default is ~/.config/wallhaven/config")
    parser.add_argument("-t", "--categories", help="Categories represented in the form of binary code.")
    parser.add_argument("-x", "--purity", help="Purity represented in the form of binary code.")
    parser.add_argument("-p", "--page", help="Page number", type=int)
    parser.add_argument("-w", "--wallpaper", help="Wallpaper index in the folder.",type=int)
    parser.add_argument("-r", "--reset", help="reset inner state. 0 only resets current wallpaper counter while "
                                              "1 resets both current wallpaper and page counter.", type=int)
    parser.add_argument("--init", help="Init the config file with wallpaper folder path INIT.")

    parser.add_argument("--random", help="Download images with a random seed and page 1.", action="store_true")
    parser.add_argument("--save", help="Save the command line configs in config file.", action="store_true")
    parser.add_argument("--noset", help="Do not set the wallpaper. Just dry run.", action="store_true")
    parser.add_argument("--NSFW", help="Temporally download NSFW images", action="store_true")
    return parser.parse_args()


def update_configs(configs, file_path):
    with open(file_path, 'w') as f:
        configs.write(f)


def set_wallpaper():
    cur_img = int(myconfigs['current wallpaper'])
    IMG_FOLDER_PATH = myconfigs['wallpaper path']
    SYS_NAME = myconfigs['system']
    (_, _, filenames) = next(os.walk(IMG_FOLDER_PATH))
    if not filenames:
        print(f'No files in {IMG_FOLDER_PATH}.')
        get_new_wallpapers()
        cur_img = -1
    elif cur_img + 1 >= len(filenames):
        print(f"Images in {IMG_FOLDER_PATH} ran out.\n"
              f"Type 1 to clear and download new.\n"
              f"Type anything else to go through again.")
        user_input = input()
        if user_input == '1':
            for file in filenames:
                os.remove(os.path.join(IMG_FOLDER_PATH, file))
            get_new_wallpapers()
        cur_img = -1

    (_, _, filenames) = next(os.walk(IMG_FOLDER_PATH))
    if cur_img < 0:
        set_system_wallpaper(SYS_NAME, os.path.join(IMG_FOLDER_PATH, filenames[0]))
        cur_img = 0
    else:
        cur_img = cur_img + 1
        set_system_wallpaper(SYS_NAME, os.path.join(IMG_FOLDER_PATH, filenames[cur_img]))
    myconfigs['current wallpaper'] = str(cur_img)


def set_system_wallpaper(sys_name, wallpaper_path):
    if sys_name == 'xfce':
        xfcesetwallpaper = 'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitoreDP1/workspace0/last-image -s'.split()
        xfcesetwallpaper.append(wallpaper_path)
        print(xfcesetwallpaper)
        subprocess.run(xfcesetwallpaper)
    elif sys_name == 'gnome':
        gnomesetwallpaper = f'gsettings set org.gnome.desktop.background picture-uri "file://{wallpaper_path}"'
        subprocess.run(gnomesetwallpaper.split())
    print('successfully set wallpaper ' + wallpaper_path)


def fetch_img_src(img):
    try:
        req = urllib.request.Request(img['url'], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            soup = BeautifulSoup(response.read(), 'lxml')
        img_obj = soup.select_one("#wallpaper")
        img['url'] = img_obj['src']
        img['width'] = img_obj['data-wallpaper-width']
        img['height'] = img_obj['data-wallpaper-height']
        # print(img['name']+" done")
        return img, None
    except Exception as e:
        return img, e


def fetch_img(img):
    IMG_FOLDER_PATH = myconfigs['wallpaper path']
    try:
        f = open(os.path.join(IMG_FOLDER_PATH, img["name"]), 'wb')
        req = urllib.request.Request(img['url'], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            f.write(response.read())
        f.close()
        # print(f"{img['name']} done.")
        return img, None
    except Exception as e:
        return img, e


def check_progress(maxval, results, rm=False):
    IMG_FOLDER_PATH = myconfigs['wallpaper path']
    i = 1
    j = 0
    for img, error in results:
        print_progress(maxval, i)
        i = i + 1
        if error is not None:
            print(f" !{img['name']} error: {error}")
            if rm:
                os.remove(os.path.join(IMG_FOLDER_PATH, img['name']))
        else:
            j = j + 1
    return j


def print_progress(maxval, i):
    sys.stdout.write('\r')
    # the exact output you're looking for:
    sys.stdout.write("[%-24s] %d/%d" % ('=' * i, i, maxval))
    sys.stdout.flush()


def random_string(stringLength):
    """Generate a random string with the combination of lowercase and uppercase letters """
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))


def get_wallhaven_url(seed, page):
    return (f"{myconfigs['baseurl']}"
            f"?categories={myconfigs['categories']}"
            f"&purity={myconfigs['purity']}"
            f"&atleast={myconfigs['width']}x{myconfigs['height']}"
            f"&sorting={myconfigs['sorting']}"
            f"&order={myconfigs['order']}"
            f"&seed={seed}&page={page}")


def get_new_wallpapers():
    page = int(myconfigs['page'])
    url = get_wallhaven_url(myconfigs['seed'], page)

    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        html = response.read()
    soup = BeautifulSoup(html, 'lxml')
    img_num = int(soup.select_one('h1').text.strip().split()[0].replace(',', ''))

    if (page + 1) * ITEM_PER_PAGE >= img_num:
        myconfigs['seed'] = random_string(SEED_LEN)
        myconfigs['page'] = '1'
    else:
        myconfigs['page'] = str(page + 1)

    fig_as = soup.select('figure .preview')
    fig_urls = [a['href'] for a in fig_as]
    imgs = [{'url': url, 'name': url[url.rfind('/') + 1:]} for url in fig_urls]

    print("downloading img src page...")
    results = ThreadPool(THREAD_NUM).imap_unordered(fetch_img_src, imgs)
    check_progress(len(imgs), results)

    # print('\nwaiting for 30s to avoid being forbidden ...')
    # time.sleep(5)

    print('\ndownloading imgs...')

    results = ThreadPool(IMG_THREAD_NUM).imap_unordered(fetch_img, imgs)
    img_get = check_progress(len(imgs), results, True)

    print(f'\nfinished. {img_get} images are stored in {myconfigs["wallpaper path"]}')


main()

