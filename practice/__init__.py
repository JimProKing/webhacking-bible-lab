import os

from practice.mount import mount_practice_app

_BASE = os.path.dirname(os.path.dirname(__file__))
_PROBLEMS = os.path.join(_BASE, "problems")


def register_practice_apps(main_app):
    """문제 01~03 미니 앱을 /practice/01 ~ /practice/03 에 마운트"""
    mounts = [
        ("01-파라미터-변조-기초", "/practice/01"),
        ("02-HTTP-직접-조작-curl-devtools", "/practice/02"),
        ("03-Burp-Repeater-마스터", "/practice/03"),
    ]
    prefixes = []
    for folder, prefix in mounts:
        app_py = os.path.join(_PROBLEMS, folder, "app.py")
        if os.path.exists(app_py):
            prefixes.append(mount_practice_app(main_app, app_py, prefix))
    return prefixes