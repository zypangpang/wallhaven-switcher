#!/usr/bin/env python
import configparser
import urllib.request
from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
import time
import os, sys, string, random, subprocess,argparse

THREAD_NUM=10
IMG_THREAD_NUM=7
CONFIG_FILE='./configs.ini'
SECTION_NAME='ZYPANG'
ITEM_PER_PAGE=24
SEED_LEN=6
#SYS_NAME='xfce'


configs=configparser.ConfigParser()
configs.read(CONFIG_FILE)

myconfigs=configs[SECTION_NAME]

IMG_FOLDER_PATH=myconfigs['wallpaper path']
SEED = myconfigs['seed']
SYS_NAME = myconfigs['system']

def parse_cmd_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--image-path",help="The folder path to the wallpaper image. If not given, use the path in config file")
    parser.add_argument("-c","--config",help="The config file path. If not given, default is ~/.config/wallhaven/config")
    parser.add_argument("--NSFW",help="Temporally download NSFW images",action="store_true")
    args=parser.parse_args()
    if args.NSFW:
        print("NSFW")

parse_cmd_args()
exit(0)

def update_configs(configs,file_path):
    with open(file_path,'w') as f:
        configs.write(f)

def set_wallpaper():
    cur_img = int(myconfigs['current wallpaper'])
    (_, _, filenames) = next(os.walk(IMG_FOLDER_PATH))
    if not filenames:
        print(f'No files in {IMG_FOLDER_PATH}.')
        get_new_wallpapers()
        cur_img=-1
    elif cur_img+1>=len(filenames):
        print(f"Images in {IMG_FOLDER_PATH} ran out.\n"
              f"Type 1 to clear and download new.\n"
              f"Type anything else to go through again.")
        user_input=input()
        if user_input == '1':
            for file in filenames:
                os.remove(os.path.join(IMG_FOLDER_PATH,file))
            get_new_wallpapers()
        cur_img=-1

    (_, _, filenames) = next(os.walk(IMG_FOLDER_PATH))
    if cur_img < 0:
        set_system_wallpaper(SYS_NAME,os.path.join(IMG_FOLDER_PATH,filenames[0]))
        cur_img=0
    else:
        cur_img=cur_img+1
        set_system_wallpaper(SYS_NAME,os.path.join(IMG_FOLDER_PATH,filenames[cur_img]))
    myconfigs['current wallpaper']=str(cur_img)

def set_system_wallpaper(sys_name,wallpaper_path):
    if sys_name == 'xfce':
        xfcesetwallpaper='xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitoreDP1/workspace0/last-image -s'.split()
        xfcesetwallpaper.append(wallpaper_path)
        print(xfcesetwallpaper)
        subprocess.run(xfcesetwallpaper)
    elif sys_name == 'gnome':
        gnomesetwallpaper=f'gsettings set org.gnome.desktop.background picture-uri "file://{wallpaper_path}"'
        subprocess.run(gnomesetwallpaper.split())
    print('successfully set wallpaper '+wallpaper_path)

def fetch_img_src(img):
    try:
        req=urllib.request.Request(img['url'],headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            soup = BeautifulSoup(response.read(),'lxml')
        img_obj=soup.select_one("#wallpaper")
        img['url']=img_obj['src']
        img['width']=img_obj['data-wallpaper-width']
        img['height']=img_obj['data-wallpaper-height']
        #print(img['name']+" done")
        return img,None
    except Exception as e:
        return img, e

def fetch_img(img):
    try:
        f=open(os.path.join(IMG_FOLDER_PATH,img["name"]),'wb')
        req=urllib.request.Request(img['url'],headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            f.write(response.read())
        f.close()
        #print(f"{img['name']} done.")
        return img,None
    except Exception as e:
        return img,e


def check_progress(results,rm=False):
    i=1
    j=0
    for img, error in results:
        print_progress(len(results),i)
        i=i+1
        if error is not None:
            print(f" !{img['name']} error: {error}")
            if rm:
                os.remove(os.path.join(IMG_FOLDER_PATH,img['name']))
        else:
            j=j+1
    return j


def print_progress(maxval,i):
    sys.stdout.write('\r')
    # the exact output you're looking for:
    sys.stdout.write("[%-24s] %d/%d" % ('='*i, i, maxval))
    sys.stdout.flush()

def randomString(stringLength):
    """Generate a random string with the combination of lowercase and uppercase letters """
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))


def get_wallhaven_url(seed,page):
    return (f"{myconfigs['baseurl']}"
            f"?categories={myconfigs['categories']}"
            f"&purity={myconfigs['purity']}"
            f"&atleast={myconfigs['width']}x{myconfigs['height']}"
            f"&sorting={myconfigs['sorting']}"
            f"&order={myconfigs['order']}"
            f"&seed={seed}&page={page}")


def get_new_wallpapers():
    page=int(myconfigs['page'])
    url=get_wallhaven_url(SEED,page)

    req=urllib.request.Request(url,headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        html=response.read()
    soup = BeautifulSoup(html,'lxml')
    img_num=int(soup.select_one('h1').text.strip().split()[0].replace(',',''))

    if (page+1)*ITEM_PER_PAGE >= img_num:
        myconfigs['seed']=randomString(SEED_LEN)
        myconfigs['page']='1'
    else:
        myconfigs['page']=str(page+1)

    fig_as=soup.select('figure .preview')
    fig_urls=[a['href'] for a in fig_as]
    imgs=[{'url':url,'name':url[url.rfind('/')+1:]} for url in fig_urls]

    print("downloading img src page...")
    results = ThreadPool(THREAD_NUM).imap_unordered(fetch_img_src, imgs)
    check_progress(results)

    #print('\nwaiting for 30s to avoid being forbidden ...')
    #time.sleep(5)

    print('\ndownloading imgs...')

    results = ThreadPool(IMG_THREAD_NUM).imap_unordered(fetch_img, imgs)
    img_get=check_progress(results,True)

    print(f'\nfinished. {img_get} images are stored in {IMG_FOLDER_PATH}')


set_wallpaper()
update_configs(configs,CONFIG_FILE)

