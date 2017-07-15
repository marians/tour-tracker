# tour-tracker

Track the general classification development of some _Grand Tours_ organised by ASO, like the Tour De France, stage over stage.

Currently this repository provides a tool to fetch and clean up the classification data, as well as the archived data for some past races.

## Installing dependencies

```
pip install requests
```

## Usage

To fetch up to date data, call the script with the ID of the race you are interested in. For example, this will fetch the classification development of the **Tour de France 2017**:

```nohighlight
python fetch.py 19
```

As result, several files will be written to the `data/` directory:

- a JSON file `race_<race_id>.json` with lots of details per rider.
- one CSV file for each classification and metric:
  - `race_<race_id>_general_position.csv`: General classification (yellow jersey) by positions/ranks
  - `race_<race_id>_general_time_gap.csv`: General classification (yellow jersey) by time offset in seconds. The leader has 0 seconds offset.
  - `race_<race_id>_mountain_position.csv`: Mountains classification (polka dots jersey, KOM) by position/rank
  - `race_<race_id>_mountain_position.csv`: Mountains classification by points
  - `race_<race_id>_sprint_position.csv`: Sprint classification (green jersey) by position/rank
  - `race_<race_id>_sprint_points.csv`: Sprint classification by points
  - `race_<race_id>_youth_position.csv`: Youth classification (white jersey, best young rider) by position/rank

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
| 19 | Tour de France 2017
