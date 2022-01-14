# huobi_turnover
script make automated trades to get a needed amount of turnover

## Setup
1. Create folder: ```mkdir huobi_turnover```
2. Enter the huobi_turnover folder:```cd the huobi_turnover folder```
3. In command line: ```sudo apt-get install -y python3-venv && python3 -m venv venv && source venv/bin/activate && pip3 install --upgrade pip && chmod +x main.py && pip3 install -r requirements.txt && pyt="$(pwd)/venv/bin/python3"```

## Usage

BEFORE USING make sure you have ```settings.txt``` with huobi api keys in the same folder (pls see example)

1. Make turnover up to 1205$:
```~/houbi_turnover/venv/bin/python3 ~/houbi_turnover/main.py -t 1205```

2. Make turnover up to 1205$ and print process into the terminal:
```~/houbi_turnover/venv/bin/python3 ~/houbi_turnover/main.py -t 1205 -v debug```

