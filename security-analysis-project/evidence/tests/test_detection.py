import types

class R:
    def __init__(self, url, code, text="", headers=None, history=None):
        self.url = url
        self.status_code = code
        self.text = text
        self.headers = headers or {}
        self.history = history or []

def fake_session_get(url, allow_redirects=False, timeout=10):
    if url.endswith("/me"):
        return R(url, 401, "login required")
    if url.endswith("/login.html"):
        return R(url, 200, "<title>Login</title><form name=\"username\"></form>")
    return R(url, 200, "ok")

def test_redirect_to_login_is_invalid(monkeypatch):
    from importlib import reload
    import builtins
    import types as _t

    import sys
    if "online_tester" in sys.modules:
        del sys.modules["online_tester"]
    import online_tester as ot

    class S:
        def get(self, *a, **k):
            return fake_session_get(*a, **k)
    ot.session = S()
    ot.BASE_URL = "https://t"

    def ng(x): 
        return " ".join(x.split()).lower()[:20000]
    ot.normalize_body = ng
    ot.login_fp = ot.LoginFingerprint(ot.session, ot.BASE_URL)

    h1 = R("https://t/app", 302, headers={"Location": "/login.html"})
    final = R("https://t/login.html", 200, "<title>Login</title><form name=\"password\"></form>")
    out = ot.classify_result(final, [h1], ot.session, ot.BASE_URL)
    assert out == "invalid"

def test_success_requires_probe(monkeypatch):
    from importlib import reload
    import sys
    if "online_tester" in sys.modules:
        del sys.modules["online_tester"]
    import online_tester as ot
    class S2:
        def get(self, url, allow_redirects=False, timeout=10):
            if url.endswith("/me"):
                return R(url, 200, "welcome user")
            return R(url, 200, "app home")
    ot.session = S2()
    ot.BASE_URL = "https://t"
    ot.login_fp = ot.LoginFingerprint(ot.session, ot.BASE_URL)
    final = R("https://t/home", 200, "home", headers={"Set-Cookie": "session=abc123"})
    out = ot.classify_result(final, [], ot.session, ot.BASE_URL)
    assert out == "success"