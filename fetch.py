# coding: utf-8

"""
Fetch JSON data for an ASO race like the Tour de France 2016
"""

import requests
import sys
import json
import csv
import argparse

# URI to the current stage
CURRENT_STAGE = "http://fep-api.dimensiondata.com/race/{race_id}/stages/current"

# URI to the list of stages
STAGES_URI = "http://fep-api.dimensiondata.com/race/{race_id}/stages"

# URI to the list of riders
RIDERS_URI = "http://fep-api.dimensiondata.com/rider/{race_id}"

STAGE_URI_TEMPLATE = "http://fep-api.dimensiondata.com/stages/{stage_id}/classification/overall"

classifications = {
    "General": ["position", "time_gap"],
    "Sprint": ["position", "points"],
    "Mountain": ["position", "points"],
    "Youth": ["position", "time_gap"]
}

# keys on rider data to be deleted
unwanted_keys = [
    "Classification",
    "CombativityClassificationRank",
    "CombinedClassificationRank",
    "GeneralClassification",
    "GeneralClassificationRank",
    "MountainClassification",
    "MountainClassificationRank",
    "SprintClassification",
    "SprintClassificationRank",
    "YoungClassification",
    "YouthClassificationRank",
]

def fetch_riders(race_id):
    """
    Returns a dict of riders, keyed by Bib number
    """
    uri = RIDERS_URI.format(race_id=race_id)
    r = requests.get(uri)
    data = r.json()
    riders = {}
    for item in data:
        for key in item.keys():
            if key in unwanted_keys:
                del item[key]
            if key in ["FirstName", "LastName"]:
                item[key] = item[key].strip()                
        riders[str(item["Id"])] = item
    return riders

def fetch_current_stage(race_id):
    uri = CURRENT_STAGE.format(race_id=race_id)
    r = requests.get(uri)
    return r.json()

def fetch_stages(race_id):
    uri = STAGES_URI.format(race_id=race_id)
    r = requests.get(uri)
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

    parser = argparse.ArgumentParser(description='Fetch grand tour classification data')
    parser.add_argument('race_id', type=int, help='Numeric race ID (6 = Tour def France 2016)')
    args = parser.parse_args()

    riders = fetch_riders(args.race_id)
    current_stage = fetch_current_stage(args.race_id)
    stages = fetch_stages(args.race_id)


    # count real stages (minus rest days)
    num_stages = 0
    for stage in stages:
        if stage["StageNumber"] in ("R1", "R2", "R3"):
            continue
        num_stages += 1

    stagecount = -1

    for stage in stages:

        details = fetch_stage(stage["StageId"])
        if stage["StageNumber"] in ("R1", "R2", "R3"):
            print("Skipping stage '%s'" % stage["StageNumber"])
            continue

        stagecount += 1
        print("Processing stage %d ('%s', ID %s)" % (
            stagecount+1, stage["StageNumber"], stage["StageId"]))

        # map classification development to rider data
        for cl in classifications.keys():
            if cl not in details:
                print("Classification '%s' not available for this race/stage" % cl)
                continue
            # iterate riders
            for rider_cl in details[cl]:
                bib = str(rider_cl["Bib"])
                if "classification" not in riders[bib]:
                    riders[bib]["classification"] = {}
                if cl.lower() not in riders[bib]["classification"]:
                    riders[bib]["classification"][cl.lower()] = {}

                for metric in classifications[cl]:
                    if metric == "position":
                        if metric not in riders[bib]["classification"][cl.lower()]:
                            riders[bib]["classification"][cl.lower()][metric] = [None] * num_stages
                        riders[bib]["classification"][cl.lower()][metric][stagecount] = rider_cl["Position"]
                    elif metric == "time_gap":
                        if metric not in riders[bib]["classification"][cl.lower()]:
                            riders[bib]["classification"][cl.lower()][metric] = [0] * num_stages
                        riders[bib]["classification"][cl.lower()][metric][stagecount] = time_to_seconds(rider_cl["Gap"])
                    elif metric == "points":
                        if metric not in riders[bib]["classification"][cl.lower()]:
                            riders[bib]["classification"][cl.lower()][metric] = [0] * num_stages
                        riders[bib]["classification"][cl.lower()][metric][stagecount] = rider_cl["Points"]

        if stage["StageId"] == current_stage["StageId"]:
            if stagecount < (num_stages-1):
                print("The remaining stages haven't happened yet, so we end here.")
                break

    with open("data/race_%d.json" % args.race_id, "wb") as output:
        output.write(json.dumps(riders, indent=2, sort_keys=True))
