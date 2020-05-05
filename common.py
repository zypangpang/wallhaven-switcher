CUR_WALLPAPER_NAME = 'cur_wallpaper.png'
BASE_URL = 'https://wallhaven.cc/api/v1/search'

DEFAULT_CONFIG_STRING = '''[DEFAULT]
# Folder to store images temporarily
wallpaper path = {wallpaper_path}  
# Folder to store your favorite images with 'wallhaven wallpaper -s'
store wallpaper path = {store_wallpaper_path} 

# Categories: General Anime People
categories = 110 
# Purity: SFW Sketchy NSFW
purity = 100 
# Sorting: date_added, relevance, random, views, favorites, toplist
sorting = toplist 
# Order: desc, asc
order = desc 

# Image width, height, ratio
width = 1920 
height = 1080 
ratios = 16x9,3x2 

# The Wallhaven page to download
page = 1 
# Seed for random sorting
seed = Zypang 

# Current wallpaper counter in the folder
current wallpaper = -1 

# Desktop environment
system = xfce 

# Your api key
api key = 

# hsetroot support
hsetroot image option = -cover
hsetroot tweak options = -tint red

#feh support
feh options = --bg-fill

[USER]
wallpaper path = {wallpaper_path}
store wallpaper path = {store_wallpaper_path}
system = gnome
'''

# THREAD_NUM = 10
IMG_THREAD_NUM = 5
# DEFAULT_CONFIG_PATH='./configs.ini'
# CONFIG_FILE_PATH = '.config/wallhaven/configs.ini'
SECTION_NAME = 'USER'
# ITEM_PER_PAGE = 24
SEED_LEN = 6
# SYS_NAME='xfce'
TIME_OUT = 30
