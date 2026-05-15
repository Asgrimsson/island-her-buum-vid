
from __future__ import annotations

import json
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any

import requests
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


DEFAULT_HEADERS = {
    "User-Agent": "Vallaskoli-Live-Lab/2.1 educational realtime dashboard",
    "Accept": "application/json, text/xml, application/xml, text/plain, */*",
}


@dataclass
class FetchResult:
    ok: bool
    url: str
    kind: str
    data: Any | None
    error: str = ""
    elapsed_ms: int = 0
    verify_ssl: bool = True


def _parse_response(url: str, text: str, content_type: str, elapsed: int, verify_ssl: bool) -> FetchResult:
    content_type = (content_type or "").lower()
    stripped = (text or "").strip()

    if "json" in content_type or stripped.startswith(("{", "[")):
        try:
            return FetchResult(True, url, "json", json.loads(text), elapsed_ms=elapsed, verify_ssl=verify_ssl)
        except Exception as e:
            return FetchResult(False, url, "json", None, f"JSON parse villa: {e}", elapsed, verify_ssl)

    if "xml" in content_type or stripped.startswith("<"):
        return FetchResult(True, url, "xml", text, elapsed_ms=elapsed, verify_ssl=verify_ssl)

    try:
        return FetchResult(True, url, "json", json.loads(text), elapsed_ms=elapsed, verify_ssl=verify_ssl)
    except Exception:
        return FetchResult(True, url, "text", text, elapsed_ms=elapsed, verify_ssl=verify_ssl)


def fetch_url(url: str, timeout: int = 10, verify_ssl: bool = True) -> FetchResult:
    start = time.time()
    try:
        r = requests.get(url, timeout=timeout, headers=DEFAULT_HEADERS, verify=verify_ssl)
        elapsed = int((time.time() - start) * 1000)
        r.raise_for_status()
        return _parse_response(url, r.text or "", r.headers.get("content-type", ""), elapsed, verify_ssl)
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        return FetchResult(False, url, "error", None, str(e), elapsed, verify_ssl)


def fetch_first(urls: list[str], timeout: int = 10, allow_insecure_retry: bool = True) -> tuple[FetchResult | None, list[FetchResult]]:
    """
    Tries each endpoint. If SSL certificate verification fails, tries the same URL once with verify_ssl=False.
    This is only used for public open-data endpoints in this educational prototype.
    """
    results: list[FetchResult] = []

    for url in urls:
        result = fetch_url(url, timeout=timeout, verify_ssl=True)
        results.append(result)
        if result.ok:
            return result, results

        ssl_problem = "certificate" in result.error.lower() or "ssl" in result.error.lower()
        if allow_insecure_retry and ssl_problem and url.startswith("https://"):
            retry = fetch_url(url, timeout=timeout, verify_ssl=False)
            results.append(retry)
            if retry.ok:
                return retry, results

    return None, results


def xml_children_as_dicts(xml_text: str, wanted_tag: str | None = None) -> list[dict]:
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return []

    if wanted_tag:
        nodes = root.findall(f".//{wanted_tag}")
    else:
        nodes = []
        for node in root.iter():
            children = list(node)
            if children and all(len(list(c)) == 0 for c in children):
                nodes.append(node)

    rows: list[dict] = []
    for node in nodes:
        row = {}
        for child in list(node):
            tag = child.tag.split("}")[-1]
            row[tag] = (child.text or "").strip()
        if row:
            rows.append(row)
    return rows


def xml_all_rows(xml_text: str) -> list[dict]:
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return []

    rows = []
    for node in root.iter():
        children = list(node)
        if not children:
            continue
        row = {}
        for child in children:
            tag = child.tag.split("}")[-1]
            txt = (child.text or "").strip()
            if txt:
                row[tag] = txt
        if len(row) >= 2:
            rows.append(row)
    return rows


def result_summary(results: list[FetchResult]) -> str:
    if not results:
        return "Engar tilraunir."

    parts = []
    for r in results:
        icon = "✅" if r.ok else "❌"
        ssl = "" if r.verify_ssl else " — SSL fallback"
        if r.ok:
            parts.append(f"{icon} {r.url} ({r.kind}, {r.elapsed_ms} ms{ssl})")
        else:
            parts.append(f"{icon} {r.url} — {r.error}{ssl}")
    return "\n".join(parts)
