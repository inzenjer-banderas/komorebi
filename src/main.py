import os
import suntimes
import datetime
import time
import json
import subprocess


class App:
    def __init__(self, latitude, longitude):
        self.komorebi_config_file_path = '{}/.Komorebi.prop'.format(os.environ['HOME'])
        self.config_text = None
        self.config_dict = {}
        self.wallpaper = ''

        self.latitude = latitude
        self.longitude = longitude
        self.altitude = 0  # Not so important
        self.suntimes = suntimes.SunTimes(longitude=self.longitude, latitude=self.latitude, altitude=self.altitude)

        # Run komorebi in the background
        self.komorebi_process_pid = subprocess.Popen(['/System/Applications/komorebi']).pid

        self.run()

    def read_config(self):
        with open(self.komorebi_config_file_path, 'r') as file:
            self.config_text = file.read().strip()
        self.convert_text_to_dict()

    def modify_config(self, wallpaper_name='foggy_sunny_mountain'):
        self.config_dict['WallpaperName'] = wallpaper_name
        self.config_text = self.convert_dict_to_text()
        with open(self.komorebi_config_file_path, 'w') as file:
            file.write(self.config_text)

    def convert_text_to_dict(self):
        key_val_pairs = self.config_text.split(sep='\n')[1:]  # Ignore [KomorebiProperties] line
        self.config_dict = {pair.split('=')[0]: pair.split('=')[1] for pair in key_val_pairs}

    def convert_dict_to_text(self):
        return '\n'.join(['[KomorebiProperties]'] + ['='.join(pair) for pair in self.config_dict.items()])

    def determine_wallpaper_from_time(self):
        date_time = datetime.datetime.now()  # returns local date/time
        rise_time = self.suntimes.riselocal(date_time)
        set_time = self.suntimes.setlocal(date_time)

        date_time = date_time.replace(tzinfo=rise_time.tzinfo)

        if rise_time < date_time < set_time:
            # Day
            return 'day'

        # Night
        return 'night'

    def run(self):
        """
        Main loop of the program, updates the config file approx. every X minutes.
        :return:
        """

        x_minutes = 1

        try:
            while True:
                # Last modification might not have been successful, the real config should be reread
                self.read_config()
                self.wallpaper = self.config_dict.get('WallpaperName', 'foggy_sunny_mountain')

                saved_wallpaper = self.wallpaper
                self.wallpaper = self.determine_wallpaper_from_time()

                if self.wallpaper != saved_wallpaper:
                    # Change the background
                    self.modify_config(self.wallpaper)

                time.sleep(x_minutes * 60)
                # time.sleep(10)

        except KeyboardInterrupt:
            print('User aborted the program, exiting....')
        except Exception as e:
            print('Exception in program:\n{}'.format(str(e)))


if __name__ == '__main__':

    with open('geo_config.json', 'r') as json_file:
        geo_config_dict = json.load(json_file)
    print(geo_config_dict)

    local_latitude = geo_config_dict['latitude']
    local_longitude = geo_config_dict['longitude']

    App(latitude=local_latitude, longitude=local_longitude)

    print("The End")
