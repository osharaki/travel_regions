import json

def clusterToJSON(polygons, clusters, target):
    data = {}
    data['polygons'] = polygons
    data['clusters'] = clusters
    with open(target, 'w') as f:
        json.dump(data, f)
    """
    {
        polygons: []
    }
    """