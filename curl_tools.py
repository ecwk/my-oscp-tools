import argparse
import sys
from argparse import RawTextHelpFormatter

usage = """python curl_tools.py -u <url> -t <...tools> -s <powershell|cmd|bash> [--one-liner]"""
examples = """EXAMPLES:
python curl_tools.py -t nc.exe winPEASx64.exe:winPEAS.exe -s powershell
(WIP) python curl_tools.py -t tools.txt -s cmd
"""


def main():
    parser = argparse.ArgumentParser(
        description="Print curl commands to download tools",
        usage=usage,
        epilog=examples,
        formatter_class=RawTextHelpFormatter,
    )

    parser.add_argument("-u", "--url", required=True, help="URL to download tools from")
    parser.add_argument(
        "-t", "--tools", required=True, help="Tools to download, separated by colon"
    )
    parser.add_argument(
        "-s",
        "--shell",
        help="Shell to use (powershell, cmd, bash)\n[default: powershell]",
        default="powershell",
    )
    parser.add_argument(
        "--one-liner",
        help="Print commands in one line",
        action="store_true",
        default=False,
    )

    args = parser.parse_args()

    match args.shell:
        case "powershell":
            get_command_str = (
                lambda tool, path: f"Invoke-WebRequest -Uri {args.url.rstrip('/')}/{tool} -OutFile {path}"
            )
        case "cmd":
            get_command_str = (
                lambda tool, path: f"curl {args.url.rstrip('/')}/{tool} -o {path}"
            )
        case "bash":
            get_command_str = (
                lambda tool, path: f"curl {args.url.rstrip('/')}/{tool} -o {path}"
            )
        case _:
            print("Invalid shell")
            sys.exit(1)

    tools = args.tools.split(",")
    string = ""
    for i, tool in enumerate(tools):
        tool, path = tool.split(":") if ":" in tool else (tool, tool.split("/")[-1])

        if args.one_liner:
            string += get_command_str(tool, path)
            if i != len(tools) - 1:
                string += " && "
        else:
            string += get_command_str(tool, path) + "\n"

    print(string)


if __name__ == "__main__":
    main()
