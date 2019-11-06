## Wallhaven Switcher
A python script tool to download wallhaven images and set them as your desktop wallpaper.

**Linux only yet.** 

Supports *xfce* and *gnome* until now.

A config example is shown by `wallhaven --generate`.

```
usage: wallhaven [-h] [-f IMAGE_PATH] [-c CONFIG] [-t CATEGORIES] [-x PURITY]
                 [-p PAGE] [-w WALLPAPER] [-q QUERY] [-r RESET] [-a API_KEY]
                 [--open] [--prev] [--clear] [--random] [--generate] [--save]
                 [--store] [--noset] [--cycle] [--NSFW] [--hsetroot]
                 [--hse_img_option HSE_IMG_OPTION]
                 [--hse_tweak_options HSE_TWEAK_OPTIONS]

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
  --open                Open current config file
  --prev                switch to last wallpaper
  --clear               Clear current image folder
  --random              Download images with a random seed and page 1.
  --generate            Output default configs. Can be combined with '-f'.
  --save                Save the command line configs in config file.
  --store               Store current wallpaper in the store wallpaper folder.
  --noset               Do not set the wallpaper. Just dry run.
  --cycle               Just cycle the folder without downloading new images.
  --NSFW                Temporarily download NSFW images
  --hsetroot            Enable hsetroot
  --hse_img_option HSE_IMG_OPTION
                        Hsetroot image option
  --hse_tweak_options HSE_TWEAK_OPTIONS
                        Hsetroot tweak options
```
