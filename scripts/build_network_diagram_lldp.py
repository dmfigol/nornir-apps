import logging
import logging.config
import time
from queue import Queue
from typing import TYPE_CHECKING, Dict, Any, Tuple, List, Set

import colorama
from colorama import Fore
import httpx
import matplotlib.pyplot as plt
import networkx as nx
from nornir import InitNornir

from nr_app import constants
from nr_app import utils
from nr_app.link import Link
from nr_app.interface import Interface

if TYPE_CHECKING:
    from nornir.core.inventory import Host

logger = logging.getLogger(__name__)


def fetch_and_parse_lldp_neighbors(task, links_q: Queue):
    lldp_data = fetch_lldp_neighbors(task.host)
    parse_lldp_neighbors(host=task.host, data=lldp_data, links_q=links_q)


def fetch_lldp_neighbors(host: "Host"):
    url = constants.RESTCONF_ROOT + constants.OPENCONFIG_LLDP_NEIGHBORS_ENDPOINT
    url = url.format(host=host.hostname)
    response = httpx.get(
        url,
        headers=constants.RESTCONF_HEADERS,
        auth=(host.username, host.password),
        verify=False,
    )
    response.raise_for_status()
    response_data = response.json()["openconfig-lldp:interface"]
    return response_data


def parse_lldp_neighbors(host, data: Dict[str, Any], links_q: Queue) -> None:
    device_name = host.name
    host_interfaces = {}
    host.data["interfaces"] = host_interfaces
    for interface_info in data:
        interface_name = interface_info["name"]
        interface = Interface(interface_name, device_name)
        neighbors = interface_info.get("neighbors")
        if not neighbors:
            continue

        link_interfaces: List["Interface"] = [interface]
        for neighbor_info in neighbors["neighbor"]:
            neighbor_state = neighbor_info["state"]
            remote_interface_name = neighbor_state["port-description"]
            remote_device_fqdn = neighbor_state["system-name"]
            remote_device_name = utils.extract_hostname_from_fqdn(remote_device_fqdn)
            remote_interface = Interface(remote_interface_name, remote_device_name)
            link_interfaces.append(remote_interface)

        link = Link(interfaces=link_interfaces)
        links_q.put(link)

        host_interfaces[interface.name] = interface


def build_graph(
    nodes: List[str], links: Set[Link]
) -> Tuple[nx.Graph, List[Dict[Tuple[str, str], str]]]:
    edge_labels: List[Dict[Tuple[str, str], str]] = [{}, {}]
    graph = nx.Graph()
    graph.add_nodes_from(nodes)

    for link in links:
        if not link.is_point_to_point:
            continue

        edge: Tuple[str, str] = tuple(
            interface.device_name for interface in link.interfaces
        )  # type: ignore
        for i, interface in enumerate(link.interfaces):
            edge_labels[i][edge] = interface.short_name
        graph.add_edge(*edge)
    logger.info("The network graph was built")
    return graph, edge_labels


def draw_and_save_topology(
    graph: nx.Graph, edge_labels: List[Dict[Tuple[str, str], str]]
) -> None:
    # plt.figure(1, figsize=(12, 12))
    fig, ax = plt.subplots(figsize=(14, 9))
    fig.tight_layout()
    pos = nx.spring_layout(graph)
    nx.draw_networkx(graph, pos, node_size=1500, node_color="orange")
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels[0], label_pos=0.8)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels[1], label_pos=0.2)
    filename = "output/topology.png"
    plt.savefig(filename)
    logger.info("The network topology diagram has been saved to %r", filename)
    # plt.draw()


def main() -> None:
    start_time = time.time()
    links_q: Queue = Queue()
    with InitNornir(config_file="nr-config-local.yaml") as nr:
        nr.run(fetch_and_parse_lldp_neighbors, links_q=links_q)

    milestone = time.time()
    time_to_run = milestone - start_time
    print(
        f"{Fore.RED}It took {time_to_run:.2f} seconds to get and parse LLDP details"
        f"{Fore.RESET}"
    )

    links = set(links_q.queue)
    nodes = [host.name for host in nr.inventory.hosts.values()]
    graph, edge_labels = build_graph(nodes=nodes, links=links)
    draw_and_save_topology(graph, edge_labels)

    new_milestone = time.time()
    time_to_run = new_milestone - milestone
    print(
        f"{Fore.RED}It took additional {time_to_run:.2f} seconds to draw the diagram"
        f"{Fore.RESET}"
    )
    plt.show()


if __name__ == "__main__":
    # matplotlib.use("TkAgg")
    logging.config.dictConfig(constants.LOGGING_DICT)
    # urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    colorama.init()
    main()
