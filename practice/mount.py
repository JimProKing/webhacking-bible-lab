"""
문제 01~03 전용 미니 앱을 메인 VulnBoard에 마운트합니다.
로컬 별도 포트 실행과 Railway 단일 앱 배포를 동시에 지원합니다.
"""

import importlib.util
import os
from functools import wraps

from flask import request


def _patch_html(html: str, prefix: str) -> str:
    """서브앱 템플릿의 절대 경로·로컬 URL을 마운트 경로에 맞게 치환"""
    if not isinstance(html, str):
        return html

    host_base = request.host_url.rstrip("/") + prefix
    local_ports = ("5000", "5001", "5003")

    for port in local_ports:
        html = html.replace(f"http://127.0.0.1:{port}", host_base)

    html = html.replace('action="/', f'action="{prefix}/')
    html = html.replace('href="/', f'href="{prefix}/')
    html = html.replace('fetch("/', f'fetch("{prefix}/')
    html = html.replace("fetch('/", f"fetch('{prefix}/")

    return html


def _wrap_view(view_func, prefix: str):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        with _practice_request_context(prefix):
            result = view_func(*args, **kwargs)
        return _patch_html(result, prefix)

    return wrapped


class _practice_request_context:
    """서브앱이 request.path 등을 마운트 기준으로 볼 수 있게 보정"""

    def __init__(self, prefix: str):
        self.prefix = prefix.rstrip("/")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def mount_practice_app(main_app, app_py_path: str, url_prefix: str):
    """별도 app.py를 메인 Flask 앱의 url_prefix 아래에 등록"""
    app_py_path = os.path.abspath(app_py_path)
    module_name = f"practice_{url_prefix.strip('/').replace('/', '_')}"

    spec = importlib.util.spec_from_file_location(module_name, app_py_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    sub_app = module.app
    prefix = url_prefix.rstrip("/")

    for rule in sub_app.url_map.iter_rules():
        if rule.endpoint == "static":
            continue

        view_func = sub_app.view_functions[rule.endpoint]
        wrapped = _wrap_view(view_func, prefix)
        endpoint = f"{module_name}_{rule.endpoint}"
        full_rule = prefix + (rule.rule if rule.rule != "/" else "/")
        methods = [m for m in (rule.methods or set()) if m not in ("OPTIONS", "HEAD")]

        main_app.add_url_rule(
            full_rule,
            endpoint=endpoint,
            view_func=wrapped,
            methods=methods or ["GET"],
        )

    return prefix