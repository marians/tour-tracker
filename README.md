# tour-tracker

Track the general classification development of some _Grand Tours_ organised by ASO, like the Tour De France, stage over stage.

Currently this repository provides a tool to fetch and clean up the classification data, as well as the archived data for past some races.

## Installing dependencies

```
pip install requests
```

## Usage

To fetch up to date data, call the script with the ID of the race you are interested in. For example, this will fetch the classification development of the Tour de France 2016:

```nohighlight
python fetch.py 6
```

As result, a JSON file `data/race_<race_id>.json` will be written.

## Race IDs and data

These are the races available so far. The leading number is the numeric ID used by the source, also useful to identify the race data file in the `data/` folder.

| ID | Race                            |
|----|---------------------------------|
| 1  | Critérium du Dauphiné 2015
| 2  | Tour de France 2015
| 4  | Amgen Tour of California 2016
| 5  | Critérium du Dauphiné 2016
| 6  | Tour de France 2016
| 7  | Vuelta a España 2016
