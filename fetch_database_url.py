import json
import requests

from urllib.parse import urlparse
from collections import OrderedDict
from typing import List, Tuple


import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def fetch_support_hosts(url):
    resp = requests.post(url)
    data = resp.content
    data = json.loads(data)
    infos = data.get("detailinfo", [])

    hosts = []
    repeat = set()
    for info in infos:
        if "url" not in info:
            logger.warning("[No Url]: {}".format(info["name"]))
        elif "tag" in info and "免费" in info["tag"]:
            logger.warning("[Pass Free]: {}".format(info["name"]))
        else:
            url_str = info["url"]
            for pair in url_str.split(","):
                url = pair.split("|")[1]
                url_parsed = urlparse(url)
                host = url_parsed.netloc

                if host not in repeat:
                    hosts.append(host)
                    repeat.add(host)

    return hosts


def match(line: str, hosts: List[str]) -> Tuple[str, bool]:
    # 清洗注释
    if "#" in line:
        line = line.split("#")[0]
    # 清洗规则
    if ":" in line:
        line = line.split(":")[1]
    # 清洗空字符
    line = line.strip()

    if not line:
        return "", False

    for host in hosts:
        if line.strip().lower() in host.strip().lower():
            if len(line) <= 6 and f".{line.strip().lower()}." not in host.strip().lower():
                logger.warning(f"[Short Mis-Match]: {line} to {host}")
                return "", False
            return host, True

    logger.warning(f"[Rule Not Match]: {line}")

    return "", False


def main(args):
    hosts = fetch_support_hosts(args.url)
    match_info = OrderedDict()
    for host in hosts:
        match_info[host] = []

    rules = []
    for url in [
        "https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/category-scholar-cn",
        "https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/category-scholar-!cn",
    ]:
        resp = requests.get(url)
        data = resp.content.decode()
        for line in data.split("\n"):
            host, matched = match(line, hosts)
            if matched:
                rules.append(line)
                match_info[host].append(line)
                if len(match_info[host]) > 1:
                    logger.warning(f"Host Multi Match{match_info[host]}")

        for host, list in match_info.items():
            if not list:
                logger.warning(f"[Host Not Match]: {host}")

        with open(args.file, "w") as f:
            f.writelines([rule + "\n" for rule in rules])


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--url", type=str, default="https://www.lib.sjtu.edu.cn/f/database/getsearchdata.shtml")
    parser.add_argument("--file", type=str, default="scholar-database")
    args = parser.parse_args()

    rules = main(args)

