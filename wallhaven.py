#!/usr/bin/env python
import configparser
import urllib.request
#from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
#import time
import os, sys, string, random, subprocess, argparse, copy,json
from pathlib import Path
from threading import Timer

BASE_URL = 'https://wallhaven.cc/api/v1/search'
DEFAULT_CONFIG_STRING = '''[DEFAULT]
# Folder to store images
wallpaper path = {wallpaper_path}
store wallpaper path = {store_wallpaper_path}
# Categories: General Anime People
categories = 110
# Purity: SFW Sketchy NSFW
purity = 100
# Sorting: date_added, relevance, random, views, favorites, toplist
sorting = toplist
# Order: desc, asc
order = desc
# Image width
width = 1920
# Image height
height = 1080
# The page to query
page = 1
# Seed for random sorting
seed = Zypang
# Current wallpaper counter in the folder
current wallpaper = -1
# Desktop environment
system = xfce
# Your api key
api key = 
cycle = 0
# hsetroot support
hsetroot = 0
hsetroot image option = -cover
hsetroot tweak options = -tint red

[USER]
wallpaper path = {wallpaper_path}
store wallpaper path = {store_wallpaper_path}
system = gnome
'''

#THREAD_NUM = 10
IMG_THREAD_NUM = 5
#DEFAULT_CONFIG_PATH='./configs.ini'
CONFIG_FILE = '~/.config/wallhaven/configs.ini'
SECTION_NAME = 'USER'
#ITEM_PER_PAGE = 24
SEED_LEN = 6
# SYS_NAME='xfce'
TIME_OUT=30

myconfigs = None
noset = False
savecounter=True
q=None


def get_config_file(create):
    home=str(Path.home())
    config_dir=os.path.join(home,'.config/wallhaven/')
    config_file=os.path.join(home,'.config/wallhaven/configs.ini')
    if os.path.isfile(config_file):
        return config_file
    elif create:
        image_folder=os.path.join(home,'WallhavenImgs/')
        store_image_folder=os.path.join(home,'Pictures/Wallpapers')
        subprocess.run(['mkdir', '-p', image_folder])
        subprocess.run(['mkdir', '-p', store_image_folder])
        subprocess.run(['mkdir', '-p', config_dir])
        config_str=DEFAULT_CONFIG_STRING.format(wallpaper_path=image_folder,
                                                store_wallpaper_path=store_image_folder)
        with open(config_file,'w') as f:
            f.write(config_str)
        return config_file
    return None


def clear_folder(folder_path):
    print("Are you sure you want to clear "+folder_path+' ?\n Type y to confirm.')
    ok=input()
    if ok!='y' and ok!='Y':
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

def main():
    global myconfigs, noset,CONFIG_FILE,SECTION_NAME,savecounter,q
    args = parse_cmd_args()
    #if args.init:
    #    wallpaper_path=args.init
    #    config_str=DEFAULT_CONFIG_STRING.format(wallpaper_path=wallpaper_path)
    #    with open('configs.ini','w') as f:
    #        f.write(config_str)
    #    print(f'Init success. \nWallpaper path is {wallpaper_path}. \nSystem is set to gnome. Change it to your '
    #          f'DE if necessary. Now supported DE is "xfce" and "gnome".\n:-) Have fun!')
    #    exit(0)

    if args.generate:
        image_path=os.path.join(str(Path.home()),'WallhavenImgs/')
        store_image_folder=os.path.join(str(Path.home()),'Pictures/Wallpapers')
        if args.image_path:
            image_path=args.image_path
        print(DEFAULT_CONFIG_STRING.format(wallpaper_path=image_path,
                                           store_wallpaper_path=store_image_folder))
        exit(0)

    if args.config:
        CONFIG_FILE = args.config
        if not os.path.isfile(CONFIG_FILE):
            print("The file does not exist.\n Exit.")
            exit(0)
    else:
        CONFIG_FILE = get_config_file(False)
        if not CONFIG_FILE:
            CONFIG_FILE = get_config_file(True)
            image_folder=os.path.join(str(Path.home()),'WallhavenImgs/')
            print(f'It seems it is the first time you run this program.\n'
                  f'I have already created a default configs for you at \n'
                  f'    {CONFIG_FILE}\n'
                  f'and default wallpaper path is set to \n'
                  f'    {image_folder}\n'
                  f'You can change it if necessary\n'
                  f'You can also specify a custom config file with "-c".')
            exit(0)
    if args.open:
        subprocess.run(['vim', CONFIG_FILE])
        exit(0)


    configs = configparser.ConfigParser()
    try:
        configs.read(CONFIG_FILE)
        t=configs[SECTION_NAME]
    except Exception as e:
        print("Config file format error or there is no section "+SECTION_NAME)
        exit(0)

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

    if args.store:
        (_,_,filenames)=next(os.walk(myconfigs['wallpaper path']))
        cur_id=int(myconfigs['current wallpaper'])
        if cur_id<0:
            print("Please use the program to set wallpaper first.")
            exit(0)
        subprocess.run(['cp', os.path.join(myconfigs['wallpaper path'],filenames[cur_id]),
                       os.path.join(myconfigs['store wallpaper path'],filenames[cur_id])])
        print("Save current wallpaper in "+myconfigs['store wallpaper path'])
        exit(0)

    if args.image_path:
        savecounter=False
        myconfigs['current wallpaper'] = '0'
        #print("You have changed the image path, this time it will choose the first image from the folder as the "
        #      "wallpaper. If you want to change it permanently, please change the config file.")
        myconfigs['wallpaper path'] = args.image_path

    if args.cycle:
        myconfigs['cycle']='1'

    if args.clear:
        clear_folder(myconfigs['wallpaper path'])

    if args.api_key:
        myconfigs['api key']=args.api_key
    if args.wallpaper:
        savecounter=False
        myconfigs['current wallpaper']=str(args.wallpaper)
    if args.prev:
        prev_id=int(myconfigs['current wallpaper'])-2
        if prev_id < -1:
            prev_id = -1
        myconfigs['current wallpaper'] = str(prev_id)

    if args.query:
        q=args.query
        noset=True

    if args.categories:
        myconfigs['categories'] = args.categories
        noset = True

    if args.purity:
        myconfigs['purity'] = args.purity
        noset = True
        print("ATTENTION: You have changed the purity. It's better to also change the image_path, or newly downloaded "
              "images will reside in the same folder with your wallpapers and can be picked next time!\n"
              "If your chose the NSFW purity, then you need an api key to fetch images.")
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
        if not myconfigs['api key']:
            print('You need an api key to fetch NSFW images. You can get it from '
                  'https://wallhaven.cc/settings/account')
            exit(0)
        if not args.image_path:
            print('You need to set a temporary folder for NSFW images with "-f".')
            exit(0)
        noset = True
        myconfigs['purity'] = '001'
        myconfigs['categories'] = '011'

    if args.hsetroot:
        myconfigs['hsetroot']='1'
        if args.hse_img_option:
            myconfigs['hsetroot image option']=args.hse_img_option
        elif not myconfigs.get('hsetroot image option'):
            print("No hsetroot image option. No hsetroot effect is added.")
            myconfigs['hsetroot']='0'
        if args.hse_tweak_options:
            myconfigs['hsetroot tweak options']=args.hse_tweak_options
        elif not myconfigs.get('hsetroot tweak options'):
            myconfigs['hsetroot tweak options']=''

    if noset:
        print("Just download images and not change the wallpaper.")
        get_new_wallpapers()
    else:
        print("Changing the wallpaper...")
        set_wallpaper()

    if args.save:
        print("ATTENTION: The configs specified by the command arguments was saved. "
              "Make sure that the configs are WHAT YOU REALLY WANT.")
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
                        help="The config file path. If not given, default is "
                             "~/.config/wallhaven/config.ini")
    parser.add_argument("-t", "--categories", help="Categories represented in the form of binary code.")
    parser.add_argument("-x", "--purity", help="Purity represented in the form of binary code.")
    parser.add_argument("-p", "--page", help="Page number", type=int)
    parser.add_argument("-w", "--wallpaper", help="Wallpaper index in the folder.",type=int)
    parser.add_argument("-q", "--query", help="Query string")
    parser.add_argument("-r", "--reset", help="reset inner state. 0 only resets current wallpaper counter while "
                                              "1 resets both current wallpaper and page counter.", type=int)
    parser.add_argument("-a", "--api_key", help="Your wallhaven account api key")

    parser.add_argument("--open", help="Open current config file", action="store_true")
    parser.add_argument("--prev", help="switch to last wallpaper", action="store_true")
    parser.add_argument("--clear", help="Clear current image folder", action="store_true")
    parser.add_argument("--random", help="Download images with a random seed and page 1.", action="store_true")
    parser.add_argument("--generate", help="Output default configs. Can be combined with '-f'.", action="store_true")
    parser.add_argument("--save", help="Save the command line configs in config file.", action="store_true")
    parser.add_argument("--store", help="Store current wallpaper in the store wallpaper folder.", action="store_true")
    parser.add_argument("--noset", help="Do not set the wallpaper. Just dry run.", action="store_true")
    parser.add_argument("--cycle", help="Just cycle the folder without downloading new images.", action="store_true")
    parser.add_argument("--NSFW", help="Temporarily download NSFW images", action="store_true")
    parser.add_argument("--hsetroot", help="Enable hsetroot", action="store_true")
    parser.add_argument("--hse_img_option", help="Hsetroot image option")
    parser.add_argument("--hse_tweak_options", help="Hsetroot tweak options")
    return parser.parse_args()


def update_configs(configs, file_path):
    with open(file_path, 'w') as f:
        configs.write(f)


def set_wallpaper():
    cur_img = int(myconfigs['current wallpaper'])
    img_folder_path = myconfigs['wallpaper path']
    sys_name = myconfigs['system']
    (_, _, filenames) = next(os.walk(img_folder_path))
    if not filenames:
        print(f'No files in {img_folder_path}.')
        if myconfigs['cycle']=='1':
            exit(0)
        get_new_wallpapers()
        cur_img = -1
    elif cur_img + 1 >= len(filenames):
        print(f"Images in {img_folder_path} ran out.\n")
        #user_input = input()
        #user_input ='Y'
        #if user_input == 'Y' or user_input == 'y':
        if myconfigs['cycle']=='0':
            print("Now clear the folder and download new.\n")
            for file in filenames:
                os.remove(os.path.join(img_folder_path, file))
            get_new_wallpapers()
        else:
            print("Now go through from the beginning again.\n")
        cur_img = -1

    (_, _, filenames) = next(os.walk(img_folder_path))
    cur_img = cur_img + 1
    set_system_wallpaper(sys_name, os.path.join(img_folder_path, filenames[cur_img]))
    myconfigs['current wallpaper'] = str(cur_img)

def hsetroot_process(wallpaper_path):
    cur_path=os.path.join(myconfigs['wallpaper path'],'cur_wallpaper')
    subprocess.run(['cp', wallpaper_path, cur_path])
    command=f'hsetroot {myconfigs["hsetroot image option"]} {cur_path} {myconfigs["hsetroot tweak options"]} -write {cur_path}.png'
    print(command)
    subprocess.run(command.split())
    return cur_path+'.png'

def set_system_wallpaper(sys_name, wallpaper_path):
    wallpaper=wallpaper_path
    if myconfigs['hsetroot']=='1':
        wallpaper=hsetroot_process(wallpaper_path)
    if sys_name == 'xfce':
        xfcesetwallpaper = 'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitoreDP1/workspace0/last-image -s'.split()
        xfcesetwallpaper.append(wallpaper)
        #print(xfcesetwallpaper)
        subprocess.run(xfcesetwallpaper)
    elif sys_name == 'gnome':
        gnomesetwallpaper = f'gsettings set org.gnome.desktop.background picture-uri "file://{wallpaper}"'
        subprocess.run(gnomesetwallpaper.split())
    print('successfully set wallpaper ' + wallpaper_path)


# Not use any more
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
    def timer_handler(response):
        response.close()

    img_folder_path = myconfigs['wallpaper path']
    try:
        with open(os.path.join(img_folder_path, img["id"]), 'wb') as f:
            req = urllib.request.Request(img['path'], headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req,timeout=TIME_OUT) as response:
                timer = Timer(TIME_OUT, timer_handler,[response])
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


def check_progress(maxval, results, rm=False):
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


def random_string(string_length):
    """Generate a random string with the combination of lowercase and uppercase letters """
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(string_length))


def get_wallhaven_url(seed, page):
    res=(f"{BASE_URL}"
            f"?categories={myconfigs['categories']}"
            f"&purity={myconfigs['purity']}"
            f"&atleast={myconfigs['width']}x{myconfigs['height']}"
            f"&sorting={myconfigs['sorting']}"
            f"&order={myconfigs['order']}"
            f"&seed={seed}&page={page}"
            f"&apikey={myconfigs['api key']}")
    if q:
        res=res+f'&q={q}'
    return res


def get_new_wallpapers():
    page = int(myconfigs['page'])
    url = get_wallhaven_url(myconfigs['seed'], page)
    print(url)

    req = urllib.request.Request(url,headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        html = response.read()
    #print(html)
    #soup = BeautifulSoup(html, 'lxml')
    #img_num = int(soup.select_one('h1').text.strip().split()[0].replace(',', ''))

    img_json=json.loads(html)
    #img_num=img_json['meta']
    #print(img_num)

    if page + 1 > int(img_json['meta']['last_page']):
        myconfigs['seed'] = random_string(SEED_LEN)
        myconfigs['page'] = '1'
    else:
        myconfigs['page'] = str(page + 1)

    #fig_as = soup.select('figure .preview')
    #fig_urls = [a['href'] for a in fig_as]
    #imgs = [{'url': img['path'], 'name': img['id'],'resolution': img['resolution']} for img in img_json['data']]

    imgs=img_json['data']

    #print("downloading img src page...")
    #results = ThreadPool(THREAD_NUM).imap_unordered(fetch_img_src, imgs)
    #check_progress(len(imgs), results)

    # print('\nwaiting for 30s to avoid being forbidden ...')
    # time.sleep(5)

    print('\ndownloading imgs...')

    results = ThreadPool(IMG_THREAD_NUM).imap_unordered(fetch_img, imgs)
    img_get = check_progress(len(imgs), results, True)

    print(f'\nfinished. {img_get} images are stored in {myconfigs["wallpaper path"]}')


main()

