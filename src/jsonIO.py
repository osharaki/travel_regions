from typing import Dict, List, Tuple
import json

def clusterToJSON(data: Dict[str, List[List[float]]], target):
    with open(target, "w") as f:
        json.dump(data, f, indent=4)

def readGeoJSON(path):
    with open(path, "r") as f:
        return json.load(f)['features'][0]