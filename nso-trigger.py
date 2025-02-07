import json
import subprocess

import mitmproxy.http


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

            print("[i] gtoken found!")
            json_data = json.loads(flow.response.get_text())
            if "bulletToken" not in json_data:
                return

            bullet_token = json_data["bulletToken"]
            print("[i] bullet token found!")
            with open("config.txt", "r+", encoding="utf-8") as f:
                config = json.loads(f)
                config['gtoken'] = gtoken
                config['bullettoken'] = bullet_token
                f.write(json.dumps(config))
                # TODO trigger s3s
                subprocess.run(["python", "s3s.py", "-r"])
        except Exception as e:
            print(f"[E] parse bulletToken failed: {e}")
