from datetime import datetime
from pathlib import Path
import shutil
from typing import Any, Union, Optional

from nornir import InitNornir

# from nornir_netconf.plugins.tasks import netconf_get_config, netconf_edit_config
from nornir_scrapli.tasks import netconf_edit_config, netconf_get_config
from nornir_utils.plugins.functions import print_result
from nornir.core.filter import F
from nornir.core.task import Result
from lxml import etree
from ruamel.yaml import YAML


from nr_app import utils

OUTPUT_DIR = Path("output/netconf")
CONFIG_YAML = Path("netconf-data/config.yaml")


def save_nc_get_config(task):
    with open(f"output/netconf/{task.host.name}.xml", "w") as f:
        cfg_xml = task.run(task=netconf_get_config, source="running").result
        f.write(cfg_xml)


def edit_nc_config_from_yaml(task):
    with open(CONFIG_YAML) as f:
        cfg = utils.yaml_to_xml_str(f.read(), root="config")
        result = task.run(task=netconf_edit_config, config=cfg).result
        return Result(host=task.host, result=result)


def main():
    if OUTPUT_DIR.is_dir():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with InitNornir(config_file="nr-config-local.yaml") as nr:
        # results = nr.run(task=save_nc_get_config)
        # print_result(results)

        results = nr.run(task=edit_nc_config_from_yaml)
        print_result(results)


if __name__ == "__main__":
    main()
