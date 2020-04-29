from datetime import datetime
from pathlib import Path

from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
# from nornir.core.filter import F
from nornir_scrapli.tasks import send_command as scrapli_send_command


COMMANDS = [
    "show version",
    "show ip int br",
    "show ip arp",
    "show platform resources",
]

OUTPUT_DIR = Path("output/commands")


def gather_commands(task, commands):
    dt = datetime.now()
    dt_str = dt.strftime('%Y-%m-%dT%H:%M:%S')

    file_path = OUTPUT_DIR / f"{task.host.name}_{dt_str}.txt"
    with open(file_path, "w") as f:
        for command in commands:
            # gather commands using netmiko
            # output = task.run(netmiko_send_command, command_string=command)
            # gather commands using scrapli w/ libssh2
            output = task.run(scrapli_send_command, command=command)
            f.write(f"===== {command} ======\n{output.result}\n\n")


def main():
    with InitNornir(config_file="nr-config-local.yaml") as nr:
        # lisbon = nr.filter(F(groups__contains="Lisbon"))
        nr.run(gather_commands, commands=COMMANDS)


if __name__ == '__main__':
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    main()
