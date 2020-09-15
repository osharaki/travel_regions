import csv
from typing import List

def readData(path: str) -> List[str]:
    with open(path, newline="", encoding="utf-8",) as csvfile:
        csvReader = csv.reader(csvfile, delimiter=",")
        data: List[str] = []
        for row in csvReader:
            data.append(row)
        return data


def writeData(path: str = "output/data.csv"):
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        csvWriter = csv.writer(csvfile, delimiter=" ")
        csvWriter.writerow(["Spam"] * 5 + ["Baked Beans"])
        csvWriter.writerow(["Spam", "Lovely Spam", "Wonderful Spam"])

