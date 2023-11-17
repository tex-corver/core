import logging
import logging.config
import os
import yaml
import pathlib

PROJECT_PATH = pathlib.Path(os.path.abspath(__file__)).parents[1]
os.environ["PROJECT_PATH"] = str(PROJECT_PATH)


def inject_config():
    project_path = os.environ["PROJECT_PATH"]
    config_dir = f"{project_path}/.configs"
    log_config_file = f"{config_dir}/logging.ini"
    logging.config.fileConfig(log_config_file)
    logging.info("--------inject configuration--------")
    config_files = os.walk(config_dir)
    for dir_path, dir_names, files in config_files:
        for file in files:
            file_path = f"{dir_path}/{file}"
            if str(pathlib.Path(file_path).suffix) in [".yaml", ".yml"]:
                logging.info("injected configuration from file %s", file_path)
                with open(file_path, "r") as file:
                    config = yaml.safe_load(file)
                    if config is None:
                        config = {}
                    logging.info(config)
                    for key, val in config.items():
                        os.environ[key.upper()] = val


inject_config()
