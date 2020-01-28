import logging
import logging.config
from typing import TYPE_CHECKING, Dict, Any, Tuple, List, Set


import urllib3
import requests
from nornir import InitNornir
from nornir.core.task import Result
from nornir.plugins.functions.text import print_result

from nr_app import constants


if TYPE_CHECKING:
    from nornir.core.inventory import Host

logger = logging.getLogger(__name__)



def fetch_and_parse_lldp_neighbors(task):
    url = f"https://{task.host.hostname}/restconf/data/Cisco-IOS-XE-lldp-oper:lldp-entries"
    headers = {
        "Accept": "application/yang-data+json"
    }
    response = requests.get(
        url,
        headers=headers,
        auth=(task.host.username, task.host.password),
        verify=False,
    )
    neighbors = []
    for lldp_entry in response.json()["Cisco-IOS-XE-lldp-oper:lldp-entries"]["lldp-entry"]:
        local_int = lldp_entry["local-interface"]
        remote_int = lldp_entry["connecting-interface"]
        remote_device = lldp_entry["device-id"]
        neighbor_str = f"{local_int} <-> {remote_device}:{remote_int}"
        neighbors.append(neighbor_str)
    result = "\n".join(neighbors)
    return Result(host=task.host, result=result)



def main() -> None:
    with InitNornir(config_file="nr-config.yaml") as nr:
        results = nr.run(fetch_and_parse_lldp_neighbors)
        print_result(results)

if __name__ == "__main__":
    logging.config.dictConfig(constants.LOGGING_DICT)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
