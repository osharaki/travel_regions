import csv
from typing import List


def readCSV(path: str) -> List[str]:
    with open(path, newline="", encoding="utf-8",) as csvfile:
        csvReader = csv.reader(csvfile, delimiter=",")
        data: List[str] = []
        for row in csvReader:
            data.append(row)
        return data


def writeCSV(
    data: List[List[str]],
    headers: List[str] = [
        "",
        "community_1",
        "community_2",
        "community_3",
        "community_4",
        "community_5",
        "community_6",
        "country_code",
        "latitude",
        "longitude",
        "place_name",
    ],
    path: str = "output/data.csv",
):
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        csvWriter = csv.writer(csvfile, delimiter=",")
        csvWriter.writerow(headers)
        csvWriter.writerows(data)

