import asyncio
import argparse
import json
import os.path
import subprocess
import socket

from mitmproxy.tools.dump import DumpMaster
from mitmproxy.options import Options
import nsotrigger
import configparser
import s3s


async def start_mitmproxy(port: int, upstream_proxy: str, show_only=False):
    if len(upstream_proxy) != 0:
        print(f"upstream proxy set to {upstream_proxy}")
        options = Options(listen_host="0.0.0.0", listen_port=port, mode=[f"upstream:{upstream_proxy}"])
    else:
        options = Options(listen_host="0.0.0.0", listen_port=port)

    master = DumpMaster(options, with_dumper=False, with_termlog=True)
    master.addons.add(nsotrigger.Trigger(show_only))
    master.addons.add(nsotrigger.IgnoreOther())
    await master.run()
    return master


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def write_si_key(key):
    global _new_config
    config = {"api_key": "", "acc_loc": "", "gtoken": "", "bullettoken": "", "session_token": "",
              "f_gen": "https://api.imink.app/f"}
    if os.path.exists("config.txt"):
        with open("config.txt", "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        _new_config = True
    config['api_key'] = key
    with open("config.txt", "w", encoding="utf-8") as w:
        json.dump(config, w, indent=4, ensure_ascii=False)


def main(conf_file: str = None):
    parser = argparse.ArgumentParser(
        description="Automatically get token when you open splt3 app, then trigger s3s upload.")
    parser.add_argument("-k", "--si-key", type=str, help="API key for stat.ink, needed for first run")
    parser.add_argument("-c", "--conf", type=str, help="Configuration INI file, override settings when set")
    parser.add_argument("-p", "--port", type=int, help="Port of proxy, for phone connection, default is 8888")
    parser.add_argument("-u", "--upstream", type=str,
                        help="Upstream proxy, like http://127.0.0.1:8080, default is none")
    parser.add_argument("-s", "--show-only", action="store_true",
                        help="Show tokens only instead of running s3s, default false")
    args = parser.parse_args()
    if conf_file is not None:
        args.conf = conf_file
    _port = 8888
    _u_proxy = ""
    _new_config = False
    if args.port:
        _port = args.port
    if args.upstream:
        _u_proxy = args.upstream
    if args.si_key:
        write_si_key(args.si_key)
    if args.conf:
        ini_reader = configparser.ConfigParser()
        if os.path.exists(args.conf):
            with open(args.conf) as stream:
                ini_reader.read_string("[top]\n" + stream.read())
            if ini_reader.has_option("top", "si_key"):
                write_si_key(ini_reader.get("top", "si_key"))

            if ini_reader.has_option("top", "port"):
                _port = ini_reader.getint("top", "port")

            if ini_reader.has_option("top", "upstream"):
                _u_proxy = ini_reader.get("top", "upstream")
        else:
            print(f"{args.conf} not found.")
            exit(1)
    if _new_config:
        print("First run, setting up s3s...")
        subprocess.run(["python", "s3s.py", "-r"])
    _ip = get_host_ip()
    print(f"start mitmproxy at {_ip}:{_port}\n==================\n\nIf this is your first run:"
          f"\n1. Setup proxy on your phone,\n2. Trust SSL certificate in http://mitm.it ,\n3. Open the NSO app.")
    asyncio.run(start_mitmproxy(_port, _u_proxy, args.show_only))


if __name__ == "__main__":
    main()
