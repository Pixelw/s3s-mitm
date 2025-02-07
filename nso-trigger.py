import json
import subprocess
from datetime import datetime

import mitmproxy.http
import mitmproxy.proxy.layers.tls


class IgnoreTLS:
    def __init__(self) -> None:
        pass

    def tls_clienthello(self, data: mitmproxy.proxy.layers.tls.ClientHelloData):
        if data.context.server.address is None:
            data.ignore_connection = True
            return
        print(data.context.server.address)
        if "api.lp1.av5ja.srv.nintendo.net" not in data.context.server.address[0]:
            data.ignore_connection = True
            return


class Trigger:
    def response(self, flow: mitmproxy.http.HTTPFlow):
        if "api.lp1.av5ja.srv.nintendo.net/api/bullet_tokens" not in flow.request.url:
            return
        print("[i] url hit!")
        try:
            if flow.request.cookies.get("_gtoken") is None:
                return

            gtoken = flow.request.cookies.get("_gtoken")
            if gtoken is None or len(gtoken) == 0:
                return

            print(f"[i] gtoken found!, {gtoken[:10]}...")
            json_data = json.loads(flow.response.get_text())
            if "bulletToken" not in json_data:
                return

            bullet_token = json_data["bulletToken"]
            print(f"[i] bullet token found!, {bullet_token[:10]}...")
            with open("config.txt", "r", encoding="utf-8") as f:
                config = json.load(f)

            config['gtoken'] = gtoken
            config['bullettoken'] = bullet_token
            now = datetime.now()
            config['nso_last_trigger'] = now.strftime("%Y-%m-%d %H:%M:%S %Z")

            with open("config.txt", "w", encoding="utf-8") as w:
                json.dump(config, w, indent=4, ensure_ascii=False)

            # trigger s3s -r
            print("[i] triggering s3s -r")
            subprocess.run(["python", "s3s.py", "-r"])
        except Exception as e:
            print(f"[E] parse bulletToken failed: {e}")


addons = [
    Trigger(),
    IgnoreTLS()
]
