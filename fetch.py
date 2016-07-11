"""
Fetch JSON data for the Tour de France 2016
"""

import requests
import sys
import json
import csv


# This is, funnily, the URI for TdF 2016. Change the '6' to
# something else to find other ASO stage races.
STAGES_URI = "http://fep-api.dimensiondata.com/race/6/stages"

STAGE_URI_TEMPLATE = "http://fep-api.dimensiondata.com/stages/{stage_id:02d}/overallridersclassification"


def fetch_stages():
    r = requests.get(STAGES_URI)
    return r.json()

def fetch_stage(stage_id):
    uri = STAGE_URI_TEMPLATE.format(stage_id=stage_id)
    r = requests.get(uri)
    return r.json()

def time_to_seconds(string):
    h, m, s = string.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)

def export_rider_csv(riders, num_stages):
    """
    Creates several tabular CSV exports of riders and classements
    """
    export_formats = (
        ("general", "rank"),
        ("general", "time_delta"),
        ("general", "time_absolute"),
        ("sprint", "rank"),
        ("sprint", "points"),
        ("mountain", "rank"),
        ("mountain", "points"),
        ("youth", "rank"),
    )
    for (classif, metric) in export_formats:
        filename = "data/%s_%s.csv" % (classif, metric)
        with open(filename, 'wb') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            headers = ["id", "first_name", "last_name", "country", "birth_date", "team"]
            for n in range(num_stages):
                headers.append("stage_%d" % (n+1))
            writer.writerow(headers)
            for rider_id in sorted(riders.keys()):
                row = []
                # rider base data
                row.append(rider_id)
                row.append(riders[rider_id]["first_name"].encode("utf8"))
                row.append(riders[rider_id]["last_name"].encode("utf8"))
                row.append(riders[rider_id]["country"])
                row.append(riders[rider_id]["birth_date"])
                row.append(riders[rider_id]["team"])

                for n in range(len(riders[rider_id]["classification"]["general"]["rank"])):
                    # classification data
                    val = riders[rider_id]["classification"][classif][metric][n]
                    if val is None:
                        val = ""
                    row.append(str(val))

                writer.writerow(row)


if __name__ == "__main__":

    classification_data = []

    stages = fetch_stages()

    with open("data/stages.json", "wb") as stagesfile:
        stagesfile.write(json.dumps(stages, indent=2, sort_keys=True))

    for stage in stages:
        details = fetch_stage(stage["StageId"])
        if details[0]["StageId"] != stage["StageId"]:
            # this stage hasn't happened yet
            break

        # clean up data
        for n in range(len(details)):

            for key in ["SprintClassification", "MountainClassification"]:
                if key in details[n]:
                    rank, points = details[n][key].split(", ")
                    details[n][key] = {
                        "rank": int(rank),
                        "points": int(points)
                    }
                    if key + "Rank" in details[n]:
                        del details[n][key + "Rank"]

            if "GeneralClassification" in details[n]:
                rank, delta, absolute = details[n]["GeneralClassification"].split(", ")
                details[n]["GeneralClassification"] = {
                    "rank": int(rank),
                    "time_delta": time_to_seconds(delta),
                    "time_absolute": time_to_seconds(absolute)
                }
                if "GeneralClassificationRank" in details[n]:
                    del details[n]["GeneralClassificationRank"]

            if "DateOfBirth" in details[n]:
                details[n]["DateOfBirth"] = details[n]["DateOfBirth"][0:10]

        classification_data.append(details)

        filename = "data/stage_classification_{stage_num:02d}.json".format(stage_num=int(stage["StageNumber"]))
        with open(filename, "wb") as stage_details_file:
            stage_details_file.write(json.dumps(details, indent=2, sort_keys=True))


    # create tabular data per rider
    riders = {}

    num_stages = len(stages)

    stage_num = 0

    for stage in classification_data:
        for rider in stage:
            rider_id = str(rider["Id"])

            # rider base data
            if rider_id not in riders:
                riders[rider_id] = {
                    "first_name": rider["FirstName"],
                    "last_name": rider["LastName"],
                    "country": rider["CountryCode"],
                    "birth_date": rider["DateOfBirth"],
                    "team": rider["TeamCode"],
                    "classification": {
                        "general": {
                            "rank": [None] * num_stages,
                            "time_delta": [None] * num_stages,
                            "time_absolute": [None] * num_stages,
                        },
                        "mountain": {
                            "rank": [None] * num_stages,
                            "points": [None] * num_stages
                        },
                        "sprint": {
                            "rank": [None] * num_stages,
                            "points": [None] * num_stages
                        },
                        "youth": {
                            "rank": [None] * num_stages
                        }
                    }
                }

            if "GeneralClassification" in rider:
                riders[rider_id]["classification"]["general"]["rank"][stage_num] = rider["GeneralClassification"]["rank"]
                riders[rider_id]["classification"]["general"]["time_delta"][stage_num] = rider["GeneralClassification"]["time_delta"]
                riders[rider_id]["classification"]["general"]["time_absolute"][stage_num] = rider["GeneralClassification"]["time_absolute"]
            if "SprintClassification" in rider:
                riders[rider_id]["classification"]["sprint"]["rank"][stage_num] = rider["SprintClassification"]["rank"]
                riders[rider_id]["classification"]["sprint"]["points"][stage_num] = rider["SprintClassification"]["points"]
            if "MountainClassification" in rider:
                riders[rider_id]["classification"]["mountain"]["rank"][stage_num] = rider["MountainClassification"]["rank"]
                riders[rider_id]["classification"]["mountain"]["points"][stage_num] = rider["MountainClassification"]["points"]
            if "YouthClassificationRank" in rider:
                riders[rider_id]["classification"]["youth"]["rank"][stage_num] = rider["YouthClassificationRank"]


        stage_num += 1

    with open("data/riders.json", "wb") as riders_file:
        riders_file.write(json.dumps(riders, indent=2, sort_keys=True))

    export_rider_csv(riders, stage_num)
