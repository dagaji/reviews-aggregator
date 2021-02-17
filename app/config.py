import yaml
from flask import current_app, url_for
import os.path
import pdb

def get_config():
    with open('app.yaml') as handle:
        config = yaml.load(handle, Loader=yaml.FullLoader)
    return config


def get_assets():
    assets = {}
    config = get_config()
    for reviewer_id in config["reviewers"]:
        assets_folder = os.path.join(current_app.static_folder, 'assets', reviewer_id)
        if os.path.exists(assets_folder):
            assets[reviewer_id] = {
                "logo_path": os.path.join(assets_folder, 'logo.html'),
                "styles_url": url_for('static', filename=f'assets/{reviewer_id}/styles.css')
            }
    return assets