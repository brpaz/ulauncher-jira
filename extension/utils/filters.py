from ulauncher.config import CONFIG_DIR
from memoization import cached
import shutil
import os
import yaml


class Filters(object):

    extension_id: str

    def __init__(self, extension_id=""):
        self.extension_id = extension_id
        self.create_default_filters_file()

    def get_config_folder_path(self):
        return os.path.join(CONFIG_DIR, self.extension_id)

    def get_custom_filters_file_path(self):
        return os.path.join(self.get_config_folder_path(), 'filters.yaml')

    def create_default_filters_file(self):

        config_dir = self.get_config_folder_path()
        if not os.path.exists(config_dir):
            os.mkdir(config_dir)

        filters_file = self.get_custom_filters_file_path()
        template_file = os.path.join(os.path.dirname(__file__), '..', '..',
                                     'data', 'filters.yaml')

        if not os.path.isfile(filters_file):
            shutil.copy(template_file, filters_file)

    @cached(ttl=15)
    def load(self):
        file_path = self.get_custom_filters_file_path()
        data = {"filters": []}
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

        return data["filters"]
