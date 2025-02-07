import asyncio
import argparse
import json

from mitmproxy.tools.dump import DumpMaster
from mitmproxy.options import Options
import nsotrigger


async def start_mitmproxy(port: int, upstream_proxy: str, show_only=False):
    if len(upstream_proxy) != 0:
        options = Options(listen_host="0.0.0.0", listen_port=port, mode=[f"upstream:{upstream_proxy}"])
    else:
        options = Options(listen_host="0.0.0.0", listen_port=port)

    master = DumpMaster(options, with_dumper=False, with_termlog=True)
    master.addons.add(nsotrigger.Trigger(show_only))
    master.addons.add(nsotrigger.IgnoreOther())
    await master.run()
    return master


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Automatically get token when you open splt3 app, then trigger s3s upload.")
    parser.add_argument("-k", "--si-key", type=str, help="API key for stat.ink, needed for first run")
    parser.add_argument("-c", "--conf", type=str, help="Configuration INI file, override settings below when set")
    parser.add_argument("-p", "--port", type=int, help="Port of proxy, for phone connection")
    parser.add_argument("-u", "--upstream", type=str, help="Upstream proxy, like http://127.0.0.1:8080")
    parser.add_argument("-s", "--show-only", action="store_true", help="Show tokens only instead of running s3s")
    args = parser.parse_args()

    _port = 8888
    _u_proxy = ""

    if args.port:
        _port = args.port
    if args.upstream:
        _u_proxy = args.upstream
    if args.si_key:
        with open("config.txt", "r", encoding="utf-8") as f:
            config = json.load(f)

        config['api_key'] = args.si_key

        with open("config.txt", "w", encoding="utf-8") as w:
            json.dump(config, w, indent=4, ensure_ascii=False)

    if args.conf:  # todo parse config
        pass

    asyncio.run(start_mitmproxy(_port, _u_proxy, args.show_only))
