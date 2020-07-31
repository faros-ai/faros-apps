"""
This is module builds and deploys a given list of apps to the Faros system or
all the apps iterating through all the app sub-directories. Leverages the faros
CLI commands to build the app zip then uploads to the api

Examples
-------
To deploy a list of apps:
    $ python deploy_apps.py --app_ids appId1,appId2

To deploy all apps:
    $ python deploy_apps.py --app_ids __ALL__

Notes
-----
    To run locally, install the faros cli and script requirements:
        $ npm install -g @faros-ai/cli
        $ pip install -r requirements.txt
"""

import argparse
import base64
import hashlib
import logging
import os
import requests
import ruamel.yaml as yaml
import subprocess

from pathlib import Path

logging.basicConfig(level=logging.INFO)

API_BASE_URL = "https://api.faros.ai/v0/apps"
FAROS_BUILD_FOLDER = ".faros/build"


def get_all_app_subdirectories(dir_path):
    """
    Get all app sub directories from the apps root folder, filtering only for
    those that have the app faros yaml file
    :param dir_path: apps root directory
    :return: list of app sub directories
    :rtype: list
    """

    return [
        path
        for path, sub_dirs, files in os.walk(dir_path)
        if "faros.yaml" in files and not path.endswith(FAROS_BUILD_FOLDER)
    ]


def build_app_zip(app_dir):
    """
    Builds the zip to deploy using the faros cli
    :param app_dir:
    :return: the name of zip and the path to the zip file
    :rtype: tuple(str, str)
    """
    os.chdir(app_dir)
    build = subprocess.Popen(['faros', 'app', 'build'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    output, error = build.communicate()
    if error:
        err = str(error, "utf-8")
        raise RuntimeError(f"Building app in {app_dir} failed with {err}")

    logging.info(str(output, "utf-8"))
    zip_name = f"{app_info['appId']}.zip"
    zip_path = os.path.join(app_dir, FAROS_BUILD_FOLDER, zip_name)
    return zip_name, zip_path


def get_presigned_url(file_name, creds):
    """
    Get pre-signed url to upload app zip to s3

    :param file_name: name of the file to upload
    :param creds: credentials to authenticate into faros api

    :return: presigned url and key
    :rtype: dict
    """
    data = {"fileName": file_name}
    # TODO - Streamline app deployment with CLI: See
    #  https://github.com/faros-ai/cli/issues/166
    response = requests.post(url=f"{API_BASE_URL}/content", json=data,
                             headers=creds)
    response.raise_for_status()
    return response.json()


def deploy_app(app_dir, zip_name, zip_path, app_info, api_key):
    """
    Deploys an app to the Faros system
    :param app_dir: the dir path with app data
    :param zip_name: name of the app zip that was built
    :param zip_path: path to the app zip file
    :param app_info: app metadata from app yaml
    :param api_key: api key used to authenticate to faros system
    :return:
    """
    app_id = app_info['appId']
    logging.info(f"Deploying app {app_id} to Faros")
    auth = {"Authorization": api_key, "Content-Type": "application/json"}

    presigned_url = get_presigned_url(zip_name, auth)
    zip_hash = upload_zip(presigned_url["uploadUrl"], zip_path)

    app_info["contents"] = {
        "key": presigned_url["key"],
        "hash": zip_hash
    }

    response = requests.post(url=API_BASE_URL, json=app_info, headers=auth)

    # Getting around https://github.com/faros-ai/poseidon/issues/439
    if response.status_code == 400 and response.reason:
        logging.warning("App already exists, overriding")
        response = requests.put(url=f"{API_BASE_URL}/{app_id}",
                                json=app_info, headers=auth)

    response.raise_for_status()
    logging.info(f"Successfully deployed app {app_id}")


def upload_zip(url, zip_path):
    """
    Uploads app zip file to the location provided in url and generate
    hash for the uploaded file
    :param url: url to upload the app zip file
    :param zip_path: path to the zip file
    :return: hash of the zip file
    :rtype: str
    """
    logging.info(f"Uploading file {zip_path}")
    with open(zip_path, "rb") as f:
        response = requests.put(url, data=f)
        zip_hash = get_file_hash(f)

    response.raise_for_status()
    return zip_hash


def get_file_hash(file):
    """
    Create a hash string of the app zip file
    :param file: file to read
    :return: hash of the file
    :rtype: str
    """
    digest = hashlib.sha1(file.read()).digest()
    encoded = base64.b64encode(digest)
    zip_hash = encoded.decode(encoding='UTF-8')
    return zip_hash


if __name__ == '__main__':
    api_key = os.environ.get("FAROS_API_KEY")
    if not api_key:
        raise RuntimeError("Faros API Key not found in environment variables")

    parser = argparse.ArgumentParser(description="Get appIds to deploy")
    parser.add_argument("--app_ids", required=True,
                        help="comma separated list of app_ids to deploy")
    args = parser.parse_args()

    base_dir = Path(os.path.abspath(__file__)).parent.parent.resolve()
    apps_dir = os.path.join(base_dir, "apps")
    apps_to_deploy = []
    if args.app_ids == "__ALL__":
        apps_to_deploy = get_all_app_subdirectories(apps_dir)
        logging.info(f"Deploying all {len(apps_to_deploy)} apps")
    elif args.app_ids:
        app_ids = set(args.app_ids.split(","))
        logging.info(f"Deploying apps {app_ids}")
        for app_id in app_ids:
            app_dir = f"{apps_dir}/{app_id.strip()}"
            if not os.path.isdir(app_dir):
                raise RuntimeError(f"App directory for appId {app_id} not "
                                   f"found in apps/{app_id}. Please ensure "
                                   f"the app exists or follows directory "
                                   f"structure.")
            apps_to_deploy.append(app_dir)
    else:
        raise RuntimeError("parameter app_ids should be a non empty string")

    for app in apps_to_deploy:
        logging.info(f"Starting process to deploy app in {app}")
        with open(f"{app}/faros.yaml", 'r') as stream:
            app_info = yaml.safe_load(stream)

        zip_name, zip_path = build_app_zip(app)
        deploy_app(app, zip_name, zip_path, app_info, api_key)

    logging.info(f"Successfully deployed {len(apps_to_deploy)} app(s)")
