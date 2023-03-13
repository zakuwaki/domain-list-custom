#!/usr/bin/env python3


""" Find redundant items in domain lists and remove them.
    e.g. 'bar.foo.com' is redundant for 'foo.com'.
"""


def load(list):
    """Parse conf file & Prepare data structure
    Returns: [ ['abc', 'com'],
               ['bar', 'foo', 'com'],
               ... ]
    """

    results = []
    domains = set()
    with open(list, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            # A domain name is case-insensitive and
            # consists of several labels, separated by a full stop
            domains.add(line)

            domain_labels = line.lower().split(".")
            results.append(domain_labels)

    # Sort results by domain labels' length
    results.sort(key=len)
    return results, domains


def find(from_path, to_path):
    """Find redundant items by a tree of top-level domain label to sub-level.
    `tree` is like { 'com': { 'foo: { 'bar': LEAF },
                              'abc': LEAF },
                     'org': ... }
    """
    labelses, domains = load(from_path)

    tree = {}
    LEAF = 1
    domainRedundant = set()
    for labels in labelses:
        domain = ".".join(labels)
        # Init root node as current node
        node = tree
        while len(labels) > 0:
            label = labels.pop()
            if label in node:
                # If child node is a LEAF node,
                # current domain must be an existed domain or a subdomain of an existed.
                if node[label] == LEAF:
                    print(f"Redundant found: {domain} at {'.'.join(labels)}")
                    domainRedundant.add(domain)
                    break
            else:
                # Create a leaf node if current label is last one
                if len(labels) == 0:
                    node[label] = LEAF
                # Create a branch node
                else:
                    node[label] = {}
            # Iterate to child node
            node = node[label]

    domains = list(domains - domainRedundant)
    domains.sort()

    with open(to_path, "w") as f:
        f.writelines([f"{line}\n" for line in domains])


if __name__ == "__main__":
    import sys

    print(sys.argv[1], sys.argv[2])
    find(sys.argv[1], sys.argv[2])
