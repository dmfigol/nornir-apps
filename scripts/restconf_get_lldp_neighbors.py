import logging
import logging.config
from typing import TYPE_CHECKING, Dict, Any, Tuple, List, Set

import urllib3
import httpx
from nornir import InitNornir
from nornir.core.task import Result
from nornir.plugins.functions.text import print_result

from nr_app import constants


if TYPE_CHECKING:
    from nornir.core.inventory import Host

logger = logging.getLogger(__name__)


def parse_lldp_neighbors_data(device_name: str, data: List[Dict[str, Any]]) -> List[str]:
    neighbors: List[str] = []
    for lldp_entry in data:
        local_int = lldp_entry["local-interface"]
        remote_int = lldp_entry["connecting-interface"]
        remote_device_fqdn = lldp_entry["device-id"]
        remote_device, _, _ = remote_device_fqdn.partition('.')
        neighbor_str = f"{device_name}:{local_int} <-> {remote_device}:{remote_int}"
        neighbors.append(neighbor_str)
    return neighbors


def fetch_and_parse_lldp_neighbors(task):
    url = f"https://{task.host.hostname}/restconf/data/Cisco-IOS-XE-lldp-oper:lldp-entries"
    headers = {
        "Accept": "application/yang-data+json"
    }
    response = httpx.get(
        url,
        headers=headers,
        auth=(task.host.username, task.host.password),
        verify=False,
    )
    lldp_data = response.json()["Cisco-IOS-XE-lldp-oper:lldp-entries"]["lldp-entry"]
    neighbors = parse_lldp_neighbors_data(task.host.name, lldp_data)
    result = "\n".join(neighbors)
    return Result(host=task.host, result=result)


def main() -> None:
    with InitNornir(config_file="nr-config-local.yaml") as nr:
        results = nr.run(fetch_and_parse_lldp_neighbors)
        print_result(results)


if __name__ == "__main__":
    logging.config.dictConfig(constants.LOGGING_DICT)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
