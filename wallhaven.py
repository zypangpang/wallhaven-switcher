#!/usr/bin/env python
import urllib.request, argparse, json
from functools import partial
from multiprocessing.pool import ThreadPool

from utils import *

# from bs4 import BeautifulSoup
# import time


class Wallhaven:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description="Wallhaven wallpaper switcher",
            usage=f'''{sys.argv[0]} <command> [<args>]
The most commonly used subcommands are:
    download: Download new wallpapers from Wallhaven
    setwp: Set desktop wallpaper
    config: Config file related operations
    wallpaper: Wallpaper file related operations
For each subcommand, use -h to show help
'''
        )
        parser.add_argument("command", help="Subcommand to run")
        args = parser.parse_args(sys.argv[1:2])

        if not hasattr(self, args.command):
            print(f"{sys.argv[1]} is not valid!")
            parser.print_usage()
            exit(1)

        # set config object
        self.__config_set()
        self.q = None
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def download(self):
        parser = argparse.ArgumentParser(
            description='Download wallpaper',
            usage=f"{sys.argv[0]} download [<args>]")

        # prefixing the argument with -- means it's optional
        # parser.add_argument("-c", "--config",
        #                    help="The config file path. If not given, default is "
        #                         "~/.config/wallhaven/config.ini")
        parser.add_argument("-f", "--image_path", help="The folder path to the wallpaper image."
                                                       " If not given, use the path in config file")
        parser.add_argument("-t", "--categories", help="Categories represented in the form of binary code.")
        parser.add_argument("-x", "--purity", help="Purity represented in the form of binary code.")
        parser.add_argument("-p", "--page", help="Page number", type=int)
        parser.add_argument("-q", "--query", help="Query string")
        parser.add_argument("-a", "--api_key", help="Your wallhaven account api key")

        parser.add_argument("--NSFW", help="Temporarily download NSFW images", action="store_true")
        parser.add_argument("--random", help="Download images with a random seed and page 1.", action="store_true")
        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command (git) and the subcommand (commit)
        args = parser.parse_args(sys.argv[2:])

        self.__do_download(args)

    def setwp(self):
        parser = argparse.ArgumentParser(description='Set next desktop wallpaper.',
                                         usage=f"{sys.argv[0]} setwp [<args>]")
        # parser.add_argument("-c", "--config",
        #                    help="The config file path. If not given, default is "
        #                         "~/.config/wallhaven/config.ini")
        parser.add_argument("-w", "--wallpaper", help="Wallpaper index in the folder.", type=int)
        parser.add_argument("-p", "--prev", help="set previous wallpaper", action="store_true")
        parser.add_argument("-c", "--curr", help="reset the current wallpaper", action="store_true")
        parser.add_argument("--hse_img_option", help="Hsetroot image option")
        parser.add_argument("--hse_tweak_options", help="Hsetroot tweak options")
        parser.add_argument("--feh_options", help="feh options")
        args = parser.parse_args(sys.argv[2:])

        self.__do_setwp(args)

    def wallpaper(self):
        parser = argparse.ArgumentParser(description='Wallpaper related operations',
                                         usage=f"{sys.argv[0]} wallpaper [<args>]")
        # parser.add_argument("-c", "--config",
        #                    help="The config file path. If not given, default is "
        #                         "~/.config/wallhaven/config.ini")
        parser.add_argument("-s", "--save", help="Store current wallpaper in the store wallpaper folder.",
                            action="store_true")
        parser.add_argument("-c", "--clear", help="Clear current image folder", action="store_true")

        if len(sys.argv)<=2:
            print("Nothing to do")
        else:
            args = parser.parse_args(sys.argv[2:])
            self.__do_wallpaper(args)

    def config(self):
        parser = argparse.ArgumentParser(
            usage=f"{sys.argv[0]} config [<args>]",
            description='Operate config files')
        # parser.add_argument("-c", "--config",
        #                    help="The config file path. If not given, default is "
        #                         "~/.config/wallhaven/config.ini")
        parser.add_argument("-o", "--open", help="Open current config file", action="store_true")
        parser.add_argument("-g", "--generate", help="Output default configs", action="store_true")
        parser.add_argument("-r", "--reset", help="reset inner state. 0 only resets current wallpaper counter while "
                                                  "1 resets both current wallpaper and page counter.", type=int)
        # parser.add_argument("--save", help="Save the command line configs in config file.", action="store_true")

        if len(sys.argv)<=2:
            print("Nothing to do")
        else:
            args = parser.parse_args(sys.argv[2:])
            self.__do_config(args)

    def __do_config(self, args):
        if args.open:
            subprocess.run(['vim', self.config_file])
            exit(0)
        elif args.generate:
            image_path = os.path.join(str(Path.home()), 'WallhavenImgs/')
            store_image_folder = os.path.join(str(Path.home()), 'Pictures/Wallpapers')
            print(DEFAULT_CONFIG_STRING.format(wallpaper_path=image_path,
                                               store_wallpaper_path=store_image_folder))
        elif args.reset is not None:
            if args.reset == 0:
                self.section['current wallpaper'] = '0'
            if args.reset == 1:
                self.section['current wallpaper'] = '0'
                self.section['page'] = '1'
            update_configs(self.configs, self.config_file)

    def __do_download(self, args):
        myconfigs = self.section
        if args.image_path:
            # print("You have changed the image path, this time it will choose the first image from the folder as the "
            #      "wallpaper. If you want to change it permanently, please change the config file.")
            myconfigs['wallpaper path'] = args.image_path

        if args.api_key:
            myconfigs['api key'] = args.api_key

        if args.query:
            self.q = args.query

        if args.categories:
            myconfigs['categories'] = args.categories

        if args.purity:
            myconfigs['purity'] = args.purity
            print(
                "ATTENTION: You have changed the purity. It's better to also change the image_path, or newly downloaded "
                "images will reside in the same folder with your wallpapers and can be picked next time!\n"
                "If your chose the NSFW purity, then you need an api key to fetch images.")

        if args.page:
            myconfigs['page'] = str(args.page)

        if args.random:
            myconfigs['seed'] = random_string(SEED_LEN)
            myconfigs['page'] = '1'

        if args.NSFW:
            if not myconfigs['api key']:
                print('You need an api key to fetch NSFW images. You can get it from '
                      'https://wallhaven.cc/settings/account')
                exit(0)
            if not args.image_path:
                print('You need to set a temporary folder for NSFW images with "-f".')
                exit(0)
            myconfigs['purity'] = '001'
            myconfigs['categories'] = '011'

        img_folder_path = myconfigs['wallpaper path']
        clear_folder(img_folder_path)
        print(f"Download new wallpapers to {img_folder_path}? Y/N")
        user_input = input()
        if user_input == 'Y' or user_input == 'y':
            print("Downloading...")
            self.__get_new_wallpapers()

        myconfigs['current wallpaper'] = '-1'
        # Only update config without any extra options
        if (len(sys.argv) == 2):
            update_configs(self.configs, self.config_file)

    def __do_setwp(self, args):
        myconfigs = self.section
        if args.wallpaper:
            myconfigs['current wallpaper'] = str(args.wallpaper)
        elif args.prev:
            prev_id = int(myconfigs['current wallpaper']) - 2
            if prev_id < -1:
                prev_id = -1
            myconfigs['current wallpaper'] = str(prev_id)
        elif args.curr:
            prev_id = int(myconfigs['current wallpaper']) - 1
            if prev_id < -1:
                prev_id = -1
            myconfigs['current wallpaper'] = str(prev_id)
        if args.hse_img_option:
            myconfigs['hsetroot image option'] = args.hse_img_option
        if args.hse_tweak_options:
            myconfigs['hsetroot tweak options'] = args.hse_tweak_options
        if args.feh_options:
            myconfigs['feh options'] = args.feh_options

        print("Changing the wallpaper...")
        self.__set_wallpaper()
        update_configs(self.configs, self.config_file)

    def __do_wallpaper(self, args):
        myconfigs = self.section
        if args.save:
            (_, _, filenames) = next(os.walk(myconfigs['wallpaper path']))
            cur_id = int(myconfigs['current wallpaper'])
            if cur_id < 0:
                print("Please use the program to set wallpaper first.")
                exit(0)
            subprocess.run(['cp', os.path.join(myconfigs['wallpaper path'], filenames[cur_id]),
                            os.path.join(myconfigs['store wallpaper path'], filenames[cur_id])])
            print("Save current wallpaper in " + myconfigs['store wallpaper path'])
            exit(0)
        elif args.clear:
            clear_folder(myconfigs['wallpaper path'])

    def __config_set(self):
        # if args.config:
        #    CONFIG_FILE = args.config
        #    if not os.path.isfile(CONFIG_FILE):
        #        print("The file does not exist.\n Exit.")
        #        exit(0)
        # else:
        CONFIG_FILE = get_config_file(False)
        if not CONFIG_FILE:
            CONFIG_FILE = get_config_file(True)
            image_folder = os.path.join(str(Path.home()), 'WallhavenImgs/')
            print(f'It seems it is the first time you run this program.\n'
                  f'I have already created a default configs for you at \n'
                  f'    {CONFIG_FILE}\n'
                  f'and default wallpaper path is set to \n'
                  f'    {image_folder}\n'
                  f'You can change it if necessary\n'
                  f'You can also specify a custom config file with "-c".')

        self.config_file = CONFIG_FILE
        self.configs, self.section = read_config_file(CONFIG_FILE, SECTION_NAME)

    def __get_new_wallpapers(self):
        myconfigs = self.section
        page = int(myconfigs['page'])
        url = self.__get_wallhaven_url(myconfigs['seed'], page)
        print(url)

        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            html = response.read()

        img_json = json.loads(html)

        if page + 1 > int(img_json['meta']['last_page']):
            myconfigs['seed'] = random_string(SEED_LEN)
            myconfigs['page'] = '1'
        else:
            myconfigs['page'] = str(page + 1)

        imgs = img_json['data']

        print('\ndownloading imgs...')

        results = ThreadPool(IMG_THREAD_NUM).imap_unordered(partial(fetch_img, configs=myconfigs), imgs)
        img_get = check_progress(len(imgs), results, myconfigs, True)

        print(f'\nfinished. {img_get} images are stored in {myconfigs["wallpaper path"]}')

    def __get_wallhaven_url(self, seed, page):
        myconfigs = self.section
        res = (f"{BASE_URL}"
               f"?categories={myconfigs['categories']}"
               f"&purity={myconfigs['purity']}"
               f"&atleast={myconfigs['width']}x{myconfigs['height']}"
               f"&ratios={myconfigs['ratios']}"
               f"&sorting={myconfigs['sorting']}"
               f"&order={myconfigs['order']}"
               f"&seed={seed}&page={page}"
               f"&apikey={myconfigs['api key']}")
        if self.q:
            res = res + f'&q={self.q}'
        return res

    def __set_wallpaper(self):
        myconfigs = self.section
        cur_img = int(myconfigs['current wallpaper'])
        img_folder_path = myconfigs['wallpaper path']
        sys_name = myconfigs['system']
        (_, _, filenames) = next(os.walk(img_folder_path))
        try:
            filenames.remove(CUR_WALLPAPER_NAME)
        except:
            pass
        if not filenames:
            print(f'No files in {img_folder_path}. Use -d to download new.')
            exit(0)
            # if myconfigs['cycle']=='1':
            #    exit(0)
            # get_new_wallpapers()
            # cur_img = -1
        elif cur_img + 1 >= len(filenames):
            print(f"Images in {img_folder_path} ran out.\n")
            print("Now go through from the beginning again.\n")
            cur_img = -1

        (_, _, filenames) = next(os.walk(img_folder_path))
        cur_img = cur_img + 1
        set_system_wallpaper(myconfigs, sys_name, os.path.join(img_folder_path, filenames[cur_img]))
        myconfigs['current wallpaper'] = str(cur_img)


if __name__ == '__main__':
    Wallhaven()
