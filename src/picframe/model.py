import os, time, yaml, logging, locale
from picframe import geo_reverse, image_cache, import_photos

DEFAULT_CONFIGFILE = "~/picframe_data/config/configuration.yaml"
DEFAULT_CONFIG = {
    'viewer': {
        'blur_amount': 12,
        'blur_zoom': 1.0,
        'blur_edges': False,
        'edge_alpha': 0.5,
        'fps': 20.0,
        'background': [0.2, 0.2, 0.3, 1.0],
        'blend_type': "blend",                           # {"blend":0.0, "burn":1.0, "bump":2.0}
        'font_file': '~/picframe_data/data/fonts/NotoSans-Regular.ttf',
        'shader': '~/picframe_data/data/shaders/blend_new',
        'show_text_fm': '%b %d, %Y',
        'show_text_tm': 20.0,
        'show_text_sz': 40,
        'show_text': "name location",
        'text_justify': 'L',
        'text_bkg_hgt': 0.25,
        'text_opacity': 1.0,
        'fit': False,
        'video_fit_display': True,
        'kenburns': False,
        'display_x': 0,
        'display_y': 0,
        'display_w': None,
        'display_h': None,
        'display_power': 2,
        'use_glx': False,                                # default=False. Set to True on linux with xserver running
        'use_sdl2': True,
        'test_key': 'test_value',
        'mat_images': True,
        'mat_type': None,
        'outer_mat_color': None,
        'inner_mat_color': None,
        'outer_mat_border': 75,
        'inner_mat_border': 40,
        'inner_mat_use_texture': False,
        'outer_mat_use_texture': True,
        'mat_resource_folder': '~/picframe_data/data/mat',
        'show_clock': False,
        'clock_justify': "R",
        'clock_text_sz': 120,
        'clock_format': "%I:%M",
        'clock_opacity': 1.0,
        'clock_top_bottom': "T",
        'clock_wdt_offset_pct': 3.0,
        'clock_hgt_offset_pct': 3.0,
        'menu_text_sz': 40,
        'menu_autohide_tm': 10.0,
        'geo_suppress_list': [],
    },
    'model': {
        'pic_dir': '~/Pictures',
        'no_files_img': '~/picframe_data/data/no_pictures.jpg',
        'follow_links': False,
        'subdirectory': '',
        'recent_n': 3,
        'reshuffle_num': 1,
        'time_delay': 20.0,
        'fade_time': 5.0,
        'shuffle': True,
        'sort_cols': 'fname ASC',
        'image_attr': ['PICFRAME GPS'],                  # image attributes send by MQTT, Keys are taken from exifread library, 'PICFRAME GPS' is special to retrieve GPS lon/lat # noqa: E501
        'load_geoloc': True,
        'locale': 'en_US.utf8',
        'key_list': [['tourism', 'amenity', 'isolated_dwelling'],
                     ['suburb', 'village'],
                     ['city', 'county'],
                     ['region', 'state', 'province'],
                     ['country']],
        'geo_key': 'this_needs_to@be_changed',           # use your email address
        'db_file': '~/picframe_data/data/pictureframe.db3',
        'deleted_pictures': '~/DeletedPictures',
        'update_interval': 2.0,
        'log_level': 'WARNING',
        'log_file': '',
        'location_filter': '',
        'tags_filter': '',
    },
    'mqtt': {
        'use_mqtt': False,                               # Set tue true, to enable mqtt
        'server': '',
        'port': 8883,
        'login': '',
        'password': '',
        'tls': '',
        'device_id': 'picframe',                         # unique id of device. change if there is more than one picture frame
        'device_url': '',
    },
    'http': {
        'use_http': False,
        'path': '~/picframe_data/html',
        'port': 9000,
        'use_ssl': False,
        'keyfile': "/path/to/key.pem",
        'certfile': "/path/to/fullchain.pem"
    },
    'peripherals': {
        'input_type': None,                              # valid options: {None, "keyboard", "touch", "mouse"}
        'buttons': {
            'pause': {'enable': True, 'label': 'Pause', 'shortcut': ' '},
            'display_off': {'enable': True, 'label': 'Display off', 'shortcut': 'o'},
            'location': {'enable': False, 'label': 'Location', 'shortcut': 'l'},
            'exit': {'enable': False, 'label': 'Exit', 'shortcut': 'e'},
            'power_down': {'enable': False, 'label': 'Power down', 'shortcut': 'p'}
        },
    },
    'aspect': {
        'enable': True,                                  # Set to True for Aspect frames 
        'import_dir': '~/picframe_data/imports',         # location for imported photos before processing
        'import_interval': 900,                          # secsonds between checks for updates from cloud default: 900 (15 min)
        'process_interval': 300,                         # secsonds between checks for files to process defsult: 300 (5 min)
        'min_rotation_interval': 30,                     # minimum time in seconds between rotations
        'set_size': 10,                                  # number of images in each orientation  
        'width': 2894,                                   # width of the visible display in pixels
        'height': 2160,                                  # height of the visible display in pixels
        'sources': {
            'nixplay': { 'enable': True, 'login_url': 'https://api.nixplay.com/www-login/', 'acct_name': 'user', 'acct_pwd': 'password', 'playlist_url': 'https://api.nixplay.com/v3/playlists', 'aspect_identifier': 'OLED' }, 
            'google_photos': { 'enable': False, 'media_url': 'https://photoslibrary.googleapis.com/v1/mediaItems', 'acct_id': 'id', 'acct_pwd': 'password', 'aspect_identifier': 'OLED'  }, 
            'flickr': { 'enable': False, 'api_url': 'https://api.flickr.com/services/rest/', 'api_id': 'id', 'api_key': 'key', 'aspect_identifier': 'OLED'  }, 
            'apple_photos': { 'enable': False, 'playlist_url': 'https://photos.apple.com/api/v1/playlists', 'acct_name': 'user', 'acct_pwd': 'password', 'aspect_identifier': 'OLED' }
        },
        'services': {
            'random_org': {
                            'enable': True, 'api_url': 'https://api.random.org/json-rpc/4/invoke', 
                            'api_key1': '6ce1241d-4e32-4e54-8c7a-02654e36f6fc', 'key1_name': 'aspect_dev1',
                            'api_key2': '4403e4be-5ad6-48db-bfac-5b65e57c505a', 'key2_name': 'aspect_dev2',
                            'api_key3': '168ae04d-1044-4eb5-8af8-8e89b70847cc', 'key3_name': 'aspect_dev3',
                            'daily_limit': 1000,         # requests per day
                            'rate_limit ': 10            # requests per second
            },
            'croppola':   { 'enable': False , 'api_url': 'https://cropolla.com/api/a', 'api_id': 'id', 'api_key': 'key', 'max_crop': 0.25 }
        }
    }
}

class Pic:                                               # TODO could this be done more elegantly with namedtuple

    def __init__(self, fname, last_modified, file_id, orientation=1, exif_datetime=0,
                 f_number=0, exposure_time=None, iso=0, focal_length=None,
                 make=None, model=None, lens=None, rating=None, latitude=None,
                 longitude=None, width=0, height=0, is_portrait=0, location=None, title=None,
                 caption=None, tags=None, nix_caption=None):
        self.fname = fname
        self.last_modified = last_modified
        self.file_id = file_id
        self.orientation = orientation
        self.exif_datetime = exif_datetime
        self.f_number = f_number
        self.exposure_time = exposure_time
        self.iso = iso
        self.focal_length = focal_length
        self.make = make
        self.model = model
        self.lens = lens
        self.rating = rating
        self.latitude = latitude
        self.longitude = longitude
        self.width = width
        self.height = height
        self.is_portrait = is_portrait
        self.location = location
        self.tags = tags
        self.caption = caption
        self.title = title
        self.nix_caption = nix_caption
        

class Model:

    def __init__(self, configfile=DEFAULT_CONFIGFILE):
        logging.basicConfig(level=logging.DEBUG)
        self.__logger = logging.getLogger(__name__)
        self.__config = DEFAULT_CONFIG
        self.__last_file_change = 0.0
        configfile = os.path.expanduser(configfile)
        with open(configfile, 'r') as stream:
            try:
                conf = yaml.safe_load(stream)
                for section in ['viewer', 'model', 'mqtt', 'http', 'peripherals','aspect']:
                    if section not in conf:
                       pass 
                       self.__logger.warning("Config file %s does not contain section '%s'. Skipping sec.", configfile, section)
                    else:
                        self.__config[section] = {**DEFAULT_CONFIG[section], **conf[section]}
                        self.__logger.debug('config data = %s', self.__config)
            except yaml.YAMLError as exc:
                self.__logger.error("Can't parse yaml config file: %s: %s", configfile, exc)
        model_config = self.get_model_config()           # alias for brevity as used several times below
        aspect_config = self.get_aspect_config()         # alias for brevity as used several times below
        self.__logger.setLevel(model_config['log_level']) # set model logger
        root_logger = logging.getLogger()
        level = getattr(logging, self.get_model_config()['log_level'].upper(), logging.WARNING)
        root_logger.setLevel(level)
        log_file = self.get_model_config()['log_file']
        if log_file != '':
            filehandler = logging.FileHandler(log_file)  # NB default appending so needs monitoring
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            filehandler.setFormatter(formatter)
            for hdlr in root_logger.handlers[:]:         # remove the existing file handlers
                if isinstance(hdlr, logging.FileHandler):
                    root_logger.removeHandler(hdlr)
            root_logger.addHandler(filehandler)          # set the new handler

        self.__file_list = None                          # NO LONGER a list of tuples
        self.__number_of_files = 0                       # this is shortcut for len(__file_list)
        self.__reload_files = True
        self.__file_index = 0                            # pointer to next position in __file_list
        self.__current_pic = None 
        self.__num_run_through = 0

        try:
            locale.setlocale(locale.LC_TIME, model_config['locale'])
        except Exception:
            self.__logger.error("error trying to set locale to {}".format(model_config['locale']))

        self.__pic_dir = os.path.expanduser(model_config['pic_dir'])
        self.__subdirectory = os.path.expanduser(model_config['subdirectory'])
        self.__load_geoloc = model_config['load_geoloc']
        self.__geo_reverse = geo_reverse.GeoReverse(model_config['geo_key'],
                                                    key_list=self.get_model_config()['key_list'])
        self.__image_cache = image_cache.ImageCache(self.__pic_dir,
                                                    model_config['follow_links'],
                                                    os.path.expanduser(model_config['db_file']),
                                                    self.__geo_reverse,
                                                    model_config['update_interval'])
        self.__deleted_pictures = model_config['deleted_pictures']
        self.__no_files_img = os.path.expanduser(model_config['no_files_img'])
        self.__sort_cols = model_config['sort_cols']
        self.__col_names = None
        self.__where_clauses = {}                        # init where clauses through setters
        self.location_filter = model_config['location_filter']
        self.tags_filter = model_config['tags_filter']

        if aspect_config['enable']:
            self.__logger.info("Aspect mode enabled")
            self.__aspect_enabled = True
            self.__import_interval = aspect_config['import_interval']
            self.__process_interval = aspect_config['process_interval']
            self.__min_rotation_interval = aspect_config['min_rotation_interval']
            self.__set_size = aspect_config['set_size']
            self.__width = aspect_config['width']
            self.__height = aspect_config['height']
            self.__import_dir = os.path.expanduser(aspect_config['import_dir'])
            self.__import_sources = aspect_config['sources']
            self.__import_services = aspect_config['services']
        

    def get_viewer_config(self):
        return self.__config['viewer']

    def get_model_config(self):
        return self.__config['model']

    def get_mqtt_config(self):
        return self.__config['mqtt']

    def get_http_config(self):
        if 'auth' in self.__config['http'] and self.__config['http']['auth'] and self.__config['http']['password'] is None:
            http_parent = os.path.abspath(os.path.join(self.__config['http']['path'], os.pardir))
            password_path = os.path.join(http_parent, 'basic_auth.txt')
            if not os.path.exists(password_path):
                new_password = self.__generate_random_string(64)
                with open(password_path, "w") as f:
                    f.write(new_password)
            with open(password_path, "r") as f:
                password = f.read()
                self.__config['http']['password'] = password
        return self.__config['http']

    def get_peripherals_config(self):
        return self.__config['peripherals']
    
    def get_aspect_config(self):
        return self.__config.setdefault('aspect', {})
    
    @property
    def fade_time(self):
        return self.__config['model']['fade_time']

    @fade_time.setter
    def fade_time(self, time):
        self.__config['model']['fade_time'] = time

    @property
    def time_delay(self):
        return self.__config['model']['time_delay']

    @time_delay.setter
    def time_delay(self, time):
        self.__config['model']['time_delay'] = time

    @property
    def subdirectory(self):
        return self.__subdirectory

    @subdirectory.setter
    def subdirectory(self, dir):
        _, root = os.path.split(self.__pic_dir)
        actual_dir = root
        if self.subdirectory != '':
            actual_dir = self.subdirectory
        if actual_dir != dir:
            if root == dir:
                self.__subdirectory = ''
            else:
                self.__subdirectory = dir
            self.__logger.info("Set subdirectory to: %s", self.__subdirectory)
            self.__reload_files = True

    @property
    def EXIF_TO_FIELD(self):                             # bit convoluted TODO hold in config? not really configurable
        return self.__image_cache.EXIF_TO_FIELD

    @property
    def update_interval(self):
        return self.__config['model']['update_interval']

    @property
    def shuffle(self):
        return self.__config['model']['shuffle']

    @shuffle.setter
    def shuffle(self, val: bool):
        self.__config['model']['shuffle'] = val          # TODO should this be altered in config?
        self.__reload_files = True

    @property
    def location_filter(self):
        return self.__config['model']['location_filter']

    @location_filter.setter
    def location_filter(self, val):
        self.__config['model']['location_filter'] = val
        if len(val) > 0:
            self.set_where_clause("location_filter", self.__build_filter(val, "location"))
        else:
            self.set_where_clause("location_filter")     # remove from where_clause
        self.__reload_files = True

    @property
    def tags_filter(self):
        return self.__config['model']['tags_filter']

    @tags_filter.setter
    def tags_filter(self, val):
        self.__config['model']['tags_filter'] = val
        if len(val) > 0:
            self.set_where_clause("tags_filter", self.__build_filter(val, "tags"))
        else:
            self.set_where_clause("tags_filter")         # remove from where_clause
        self.__reload_files = True

    def __build_filter(self, val, field):
        if val.count("(") != val.count(")"):
            self.__logger.error("Unbalanced brackets in filter: %s", val)
            self.__logger.error("Filter not applied") 
            return None
        val = val.replace(";", "").replace("'", "").replace("%", "").replace('"', '')  # SQL scrambling
        tokens = ("(", ")", "AND", "OR", "NOT")          # now copes with NOT
        val_split = val.replace("(", " ( ").replace(")", " ) ").split()  # so brackets not joined to words
        filter = []
        last_token = ""
        for s in val_split:
            s_upper = s.upper()
            if s_upper in tokens:
                if s_upper in ("AND", "OR"):
                    if last_token in ("AND", "OR"):
                        return None                      # must have a non-token between
                    last_token = s_upper
                filter.append(s)
            else:
                if last_token is not None:
                    filter.append("{} LIKE '%{}%'".format(field, s))
                else:
                    filter[-1] = filter[-1].replace("%'", " {}%'".format(s))
                last_token = None
        return "({})".format(" ".join(filter))           # if OR outside brackets will modify the logic of rest of where clauses

    def set_where_clause(self, key, value=None):
        if (value is None or len(value) == 0):           # value must be a string for later join()
            if key in self.__where_clauses:
                self.__where_clauses.pop(key)
            return
        self.__where_clauses[key] = value

    def pause_looping(self, val):
        self.__image_cache.pause_looping(val)

    def stop_image_cache(self):
        self.__image_cache.stop()

    def purge_files(self):
        self.__image_cache.purge_files()

    def create_valid_folder_name(string):
        """Converts a string to a valid folder name."""
        string = re.sub(r'[\\/:*?"<>|]', '_', string)    # Replace invalid characters with underscores
        string = string.strip()                          # Remove leading/trailing whitespace        

        return string
    
    def get_directory_list(self):
        _, root = os.path.split(self.__pic_dir)
        actual_dir = root
        if self.subdirectory != '':
            actual_dir = self.subdirectory
        follow_links = self.get_model_config()['follow_links']
        subdir_list = next(os.walk(self.__pic_dir, followlinks=follow_links))[1]
        subdir_list[:] = [d for d in subdir_list if not d[0] == '.']
        if not follow_links:
            subdir_list[:] = [d for d in subdir_list if not os.path.islink(self.__pic_dir + '/' + d)]
        subdir_list.insert(0, root)
        return actual_dir, subdir_list

    def force_reload(self):
        self.__reload_files = True

    def set_next_file_to_previous_file(self):
        if self.__number_of_files > 0:
            self.__file_index = (self.__file_index - 2) % self.__number_of_files
        else:
            self.__file_index = 0                        # reset to zero if no files available
            self.__logger.warning("No files available, setting file index to 0") 
            
    def get_next_file(self):                             # MAIN LOOP: keep getting next file  
        missing_images = 0
        self.__logger.debug("get_next_file called, number of files:  %s. File Index: %s", self.__number_of_files, self.__file_index)
        while True:                                      # loop until we acquire a valid image set
            pic = None
            if self.__reload_files:                      # Reload the playlist if requested
                self.__logger.debug("Reloading files from image cache")
                for _i in range(5):                      # give image_cache chance on first load if a large directory
                    self.__get_files()
                    missing_images = 0
                    if self.__number_of_files > 0:
                        break
                    time.sleep(0.5)

            # If we don't have any files to show, prepare the "no images" image
            # Also, set the reload_files flag so we'll check for new files on the next pass...
            if self.__number_of_files == 0 or missing_images >= self.__number_of_files:
                pic = Pic(self.__no_files_img, 0, 0)
                self.__logger.warning("No Images. Reload requested")
                self.__reload_files = True
                break

            # If we've displayed all images...
            #   If it's time to shuffle, set a flag to do so
            #   Loop back, which will reload and shuffle if necessary
            if self.__file_index == self.__number_of_files:
                self.__num_run_through += 1
                if self.shuffle and self.__num_run_through >= self.get_model_config()['reshuffle_num']:
                    self.__logger.info("Reshuffling files after {} runs through".format(self.__num_run_through))
                    self.__reload_files = True
                    self.__file_index = 0
                    continue

            file_id = self.__file_list[self.__file_index][0]   # Load the current image
            self.__logger.debug("Loading file: %s", file_id)
            pic_row = self.__image_cache.get_file_info(file_id)
            self.__logger.debug("pic_row: %s", pic_row)
            pic = Pic(**pic_row) if pic_row is not None else None
            
            if pic and not os.path.isfile(pic.fname):    # Verify the image actually exists on disk
                pic = None
            
            self.__file_index += 1                       # Increment the image index for next time

            if pic:                                      # If pic is valid here, everything is OK. Break out of the loop and return the set
                break

            # Here, pic is undefined. That's a problem. Loop back and get another image.
            # Track the number of times we've looped back so we can abort if we don't have *any* images to display
            missing_images += 1

        self.__current_pic = pic
        return self.__current_pic

    def get_number_of_files(self):
        return sum(
                    sum(1 for pic in pics if pic is not None)
                    for pics in self.__file_list
                )

    def get_current_pic(self):
        return self.__current_pic

    def delete_file(self):                               # delete the current pic.
        pic = self.__current_pic
        if pic is None:
            return None
        f_to_delete = pic.fname
        move_to_dir = os.path.expanduser(self.__deleted_pictures)
        # TODO should these os system calls be inside a try block
        # in case the file has been deleted after it started to show?
        if not os.path.exists(move_to_dir):
            os.system("mkdir {}".format(move_to_dir))    # problems with ownership using python func
        os.system("mv '{}' '{}'".format(f_to_delete, move_to_dir))  # and with SMB drives
        for i, file_rec in enumerate(self.__file_list):  # find and delete record from __file_list
            if file_rec[0] == pic.file_id:               # database id TODO check that db tidies itself up
                self.__file_list.pop(i)
                self.__number_of_files -= 1
                break

    def __get_files(self):
        if self.subdirectory != "":
            self.__logger.debug("Using subdirectory: %s", self.subdirectory)
            picture_dir = os.path.join(self.__pic_dir, self.subdirectory)  # TODO catch, if subdirecotry does not exist
        else:
            picture_dir = self.__pic_dir
        where_list = ["fname LIKE '{}/%'".format(picture_dir)]  # TODO / on end to stop 'test' also selecting test1 test2 etc  # noqa: E501
        self.__logger.debug("Using picture directory: %s", picture_dir)
        self.__logger.debug("Using where clauses: %s", self.__where_clauses)
        where_list.extend(self.__where_clauses.values())

        if len(where_list) > 0:
            where_clause = " AND ".join(where_list)       # TODO now always true - remove unreachable code
        else:
            where_clause = "1"

        sort_list = []
        recent_n = self.get_model_config()["recent_n"]
        if recent_n > 0:
            sort_list.append("last_modified < {:.0f}".format(time.time() - 3600 * 24 * recent_n))

        if self.shuffle:
            sort_list.append("RANDOM()")
        else:
            if self.__col_names is None:
                self.__col_names = self.__image_cache.get_column_names()  # do this once
            for col in self.__sort_cols.split(","):
                colsplit = col.split()
                if colsplit[0] in self.__col_names and (len(colsplit) == 1 or colsplit[1].upper() in ("ASC", "DESC")):
                    sort_list.append(col)
            sort_list.append("fname ASC")                # always finally sort on this in case nothing else to sort on or sort_cols is "" # noqa: E501
        sort_clause = ",".join(sort_list)

        self.__file_list = self.__image_cache.query_cache(where_clause, sort_clause)
        self.__number_of_files = len(self.__file_list)
        self.__file_index = 0
        self.__num_run_through = 0
        self.__reload_files = False

    def __generate_random_string(self, length):
        random_bytes = os.urandom(length // 2)
        random_string = ''.join('{:02x}'.format(ord(chr(byte))) for byte in random_bytes)
        return random_string
