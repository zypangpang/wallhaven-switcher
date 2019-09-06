## Wallhaven Switcher
A python script tool to download wallhaven images and set them as your desktop wallpaper.
**Linux only yet.** 
Suports *xfce* and *gnome* until now.

```
usage: wallhaven.py [-h] [-f IMAGE_PATH] [-c CONFIG] [-t CATEGORIES]
                    [-x PURITY] [-p PAGE] [-w WALLPAPER] [-q QUERY] [-r RESET]
                    [-a API_KEY] [--open_configs] [--clear] [--random]
                    [--generate] [--save] [--noset] [--NSFW]

optional arguments:
  -h, --help            show this help message and exit
  -f IMAGE_PATH, --image_path IMAGE_PATH
                        The folder path to the wallpaper image. If not given,
                        use the path in config file
  -c CONFIG, --config CONFIG
                        The config file path. If not given, default is
                        ~/.config/wallhaven/config.ini
  -t CATEGORIES, --categories CATEGORIES
                        Categories represented in the form of binary code.
  -x PURITY, --purity PURITY
                        Purity represented in the form of binary code.
  -p PAGE, --page PAGE  Page number
  -w WALLPAPER, --wallpaper WALLPAPER
                        Wallpaper index in the folder.
  -q QUERY, --query QUERY
                        Query string
  -r RESET, --reset RESET
                        reset inner state. 0 only resets current wallpaper
                        counter while 1 resets both current wallpaper and page
                        counter.
  -a API_KEY, --api_key API_KEY
                        Your wallhaven account api key
  --open_configs        Open current config file
  --clear               Clear current image folder
  --random              Download images with a random seed and page 1.
  --generate            Output default configs. Can be combined with '-f'.
  --save                Save the command line configs in config file.
  --noset               Do not set the wallpaper. Just dry run.
  --NSFW                Temporally download NSFW images
```

