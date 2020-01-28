#!/usr/bin/env python3
import logging
import logging.config
import time
from typing import List, Dict, Tuple

from colorama import Fore
from nornir import InitNornir
from nornir.core.inventory import Host
import colorama
import matplotlib.pyplot as plt
import networkx as nx
import requests
import urllib3

import constants
from interface import Interface

logger = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def extract_hostname_from_fqdn(fqdn: str) -> str:
    """Extracts hostname from fqdn-like string

    For example, R1.cisco.com -> R1,  sw1 -> sw1"
    """
    return fqdn.split(".")[0]


def parse_cdp_neighbors(task):
    url = constants.RESTCONF_ROOT + constants.CDP_NEIGHBORS_ENDPOINT
    url = url.format(host=task.host.hostname)
    response = requests.get(
        url,
        headers=constants.HEADERS,
        auth=(task.host.username, task.host.password),
        verify=False,
    )
    response.raise_for_status()
    cdp_entries = response.json().get("Cisco-IOS-XE-cdp-oper:cdp-neighbor-detail", [])
    device_name = task.host.name
    host_interfaces = {}
    task.host.data["interfaces"] = host_interfaces
    for cdp_entry in cdp_entries:
        interface_name = cdp_entry["local-intf-name"]
        if interface_name in host_interfaces:
            interface = host_interfaces[interface_name]
        else:
            interface = Interface(interface_name, device_name)
            host_interfaces[interface_name] = interface

        remote_interface_name = cdp_entry["port-id"]
        remote_device_fqdn = cdp_entry["device-name"]
        remote_device_name = extract_hostname_from_fqdn(remote_device_fqdn)
        remote_interface = Interface(remote_interface_name, remote_device_name)
        interface.neighbors.append(remote_interface)


def build_graph(hosts: List[Host]) -> Tuple[nx.Graph, List[Dict[Tuple[str, str], str]]]:
    edge_labels: List[Dict[Tuple[str, str], str]] = [{}, {}]
    links = set([
        interface.link_from_neighbors()
        for host in hosts
        for interface in host.data["interfaces"].values()
    ])
    graph = nx.Graph()
    graph.add_nodes_from([host.name for host in hosts])

    for link in links:
        if not link.is_point_to_point:
            continue

        edge: Tuple[str, str] = tuple(
            interface.device_name
            for interface in link.interfaces
        )
        for i, interface in enumerate(link.interfaces):
            edge_labels[i][edge] = interface.short_name
        graph.add_edge(*edge)
    logger.info("The network graph was built")
    return graph, edge_labels   