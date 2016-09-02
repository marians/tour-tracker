# tour-tracker

Track the general classification development of some _Grand Tours_ organised by ASO, like the Tour De France, stage over stage.

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

## Race IDs

Here are some race IDs that have worked so far:

- 5: Critérium du Dauphiné 2016
- 6: Tour de France 2016
- 7: Vuelta a España 2016
