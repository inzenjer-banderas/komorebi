import os
import suntimes
import datetime


class App:
    def __init__(self):
        self.komorebi_config_file_path = '{}/.Komorebi.prop'.format(os.environ['HOME'])
        self.config_text = None
        self.config_dict = {}
        with open(self.komorebi_config_file_path, 'r') as file:
            self.config_text = file.read().strip()
        self.convert_text_to_dict()

        self.latitude = 43.32472
        self.longitude = 21.90333
        self.altitude = 0  # Not so important
        self.suntimes = suntimes.SunTimes(longitude=self.longitude, latitude=self.latitude, altitude=self.altitude)
        self.wallpaper = self.determine_wallpaper_from_time()
        self.modify_config(wallpaper_name=self.wallpaper)

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
            print('Day')
            return 'proba_vitez'

        # Night
        print('Night')
        return 'proba_betmen'


if __name__ == '__main__':
    App()
    print("The End")
