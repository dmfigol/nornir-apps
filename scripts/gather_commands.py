from datetime import datetime
from pathlib import Path

from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
# from nornir.core.filter import F


COMMANDS = [
    "show version",
    "show ip int br",
    "show ip arp",
    "show platform resources",
]


def gather_commands(task, commands):
    dt = datetime.now()
    dt_str = dt.strftime('%Y-%m-%dT%H:%M:%S')
    file_path = Path("output/text") / f"{task.host.name}_{dt_str}.txt"
    with open(file_path, "w") as f:
        for command in commands:
            output = task.run(netmiko_send_command, command_string=command)
            f.write(f"===== {command} ======\n{output.result}\n\n")


def main():
    with InitNornir(config_file="nr-config.yaml") as nr:
        # lisbon = nr.filter(F(groups__contains="Lisbon"))
        nr.run(gather_commands, commands=COMMANDS)


if __name__ == '__main__':
    main()
