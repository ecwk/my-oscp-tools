import argparse
import sys
import glob
import subprocess
from argparse import RawTextHelpFormatter

usage = """python curl_tools.py -u <url> -t <...tools> [-s <powershell|cmd|bash> -d <tools_dir> -v --one-liner --copy-to-clipboard]"""
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
        "-t",
        "--tools",
        required=True,
        help="Tools to download, separated by commas. Format: <tool_name>:<save_as>. Globbing supported e.g. 'nc.exe' or 'nc*.exe'.",
    )
    parser.add_argument(
        "-s",
        "--shell",
        help="Shell to use (powershell, cmd, bash)\n[default: powershell]",
        default="powershell",
    )
    parser.add_argument(
        "-d", "--directory", help="Directory to search for tools in", default="."
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Enable verbose output\n[default: disabled]",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--one-liner",
        help="Print commands in one line\n[default: disabled]",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--copy-to-clipboard",
        help="Copy commands to clipboard. Requires xsel to be installed\n[default: disabled]",
        action="store_true",
        default=False,
    )

    args = parser.parse_args()

    match args.shell:
        case "powershell":
            get_command_str = (
                lambda tool_path, save_as: f"Invoke-WebRequest -Uri {args.url.rstrip('/')}/{tool_path} -OutFile {save_as}"
            )
        case "cmd":
            get_command_str = (
                lambda tool_path, save_as: f"curl {args.url.rstrip('/')}/{tool_path} -o {save_as}"
            )
        case "bash":
            get_command_str = (
                lambda tool_path, save_as: f"curl {args.url.rstrip('/')}/{tool_path} -o {save_as}"
            )
        case _:
            print("Invalid shell")
            sys.exit(1)

    tools = args.tools.split(",")
    string = ""
    for i, tool in enumerate(tools):
        tool_name, save_as = (
            tool.split(":") if ":" in tool else (tool, tool.split("/")[-1])
        )

        tool_paths = glob.glob(f"{args.directory}/**/{tool_name}", recursive=True)

        if not tool_paths:
            print(f"\n[!] Tool '{tool_name}' not found in '{args.directory}'")
            sys.exit(1)

        if len(tool_paths) > 1:
            print(f"\n[*] Multiple paths found for '{tool_name}': {tool_paths}")
            print(f"[*] Selecting the first one '{tool_paths[0]}'")

        tool_path = tool_paths[0]

        if args.one_liner:
            string += get_command_str(tool_path, save_as)
            if i != len(tools) - 1:
                string += " && "
        else:
            string += get_command_str(tool_path, save_as) + "\n"

    print()
    print("----------------------------------------------------------------")
    print(string)
    print("----------------------------------------------------------------")

    if args.copy_to_clipboard:
        try:
            subprocess.run(
                ["echo", "-n", string.strip()],
                stdout=subprocess.PIPE,
                check=True,
            )
            subprocess.run(
                ["xsel", "--clipboard"],
                input=string.strip().encode(),
                check=True,
            )
            print("\n[*] Copied to clipboard!")
        except subprocess.CalledProcessError as e:
            print("\n[!] Error copying to clipboard:", e)
            sys.exit(1)


if __name__ == "__main__":
    main()
