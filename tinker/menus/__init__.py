import os
import json

def get_menu_items():
    menus_folder = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    menus_file = os.path.join(menus_folder, 'menu_system.json')
    with open(menus_file) as f:
            data = json.load(f)
    return data['menu_system']