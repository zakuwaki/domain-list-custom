import json
import requests

from urllib.parse import urlparse
from typing import List


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
            logger.warning("[NO URL]: {}".format(info["name"]))
        elif "tag" in info and "免费" in info["tag"]:
            logger.warning("[PASS FREE]: {}".format(info["name"]))
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


def is_match(line: str, hosts: List[str]) -> bool:
    # 清洗注释
    if "#" in line:
        line = line.split("#")[0]
    # 清洗规则
    if ":" in line:
        line = line.split(":")[1]
    # 清洗空字符
    line = line.strip()

    if not line:
        return False

    for host in hosts:
        if line.strip().lower() in host.strip().lower():
            return True

    logger.warning(f"[Rule Not Match]: {line}")

    return False


def main(args):
    hosts = fetch_support_hosts(args.url)

    rules = []
    for url in [
        "https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/category-scholar-cn",
        "https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/category-scholar-!cn",
    ]:
        resp = requests.get(url)
        data = resp.content.decode()
        for line in data.split("\n"):
            if is_match(line, hosts):
                rules.append(line)

        with open(args.file, "w") as f:
            f.writelines([rule + "\n" for rule in rules])


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--url", type=str, default="https://www.lib.sjtu.edu.cn/f/database/getsearchdata.shtml")
    parser.add_argument("--file", type=str, default="scholar-database")
    args = parser.parse_args()

    rules = main(args)

