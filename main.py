from parseCSV import *
from typing import Dict, List


def main():
    communities: Dict[int, List[List[str]]] = getCommunities(1)
    print([e[-1] for e in communities[2]])


if __name__ == "__main__":
    main()
