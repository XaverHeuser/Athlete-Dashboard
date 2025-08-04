import os

def set_proxy_if_needed():
    """Aktiviert Proxy nur lokal, wenn USE_PROXY=1"""
    if os.getenv("USE_PROXY") == "1":
        os.environ["HTTP_PROXY"] = os.getenv("HTTP_PROXY", "")
        os.environ["HTTPS_PROXY"] = os.getenv("HTTPS_PROXY", "")
        print("[DEBUG] Proxy aktiviert")
    else:
        # Cloud Run / Kein Proxy
        for k in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
            os.environ.pop(k, None)
        print("[DEBUG] Proxy deaktiviert")
