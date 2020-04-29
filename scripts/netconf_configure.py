from nornir import InitNornir
from nornir.plugins.tasks.networking import netconf_get_config, netconf_edit_config
from nornir.plugins.functions.text import print_result
from nornir.core.filter import F
from nornir.core.task import Result
from datetime import datetime
from pathlib import Path
from typing import Any, Union, Optional

from lxml import etree
from ruamel.yaml import YAML
import xml.dom.minidom

from nr_app import utils

def save_nc_get_config(task):
    with open(f"output/netconf/{task.host.name}.xml", "w") as f:
        result = task.run(task=netconf_get_config, source="running").result
        xml_pretty = xml.dom.minidom.parseString(result).toprettyxml()
        f.write(xml_pretty)


def edit_nc_config_from_yaml(task, config_path: str):
    with open(config_path) as f:
        yaml = YAML(typ="safe")
        data = yaml.load(f)
        xml = utils.dict_to_xml(data, root="config")
        xml_str = etree.tostring(xml).decode('utf-8')
        result = task.run(task=netconf_edit_config, config=xml_str)
        return Result(host=task.host, result=result.result)


def main():
    with InitNornir(config_file="nr-config-local.yaml") as nr:
        # results = nr.run(task=save_nc_get_config)
        # print_result(results)

        results = nr.run(
            task=edit_nc_config_from_yaml,
            config_path="netconf-data/config.yaml",
        )
        # print_result(results)


if __name__ == '__main__':
    main()
