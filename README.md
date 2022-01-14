# huobi_turnover
script make automated trades to get a needed amount of turnover

## Setup
1. clone repo
```sh
cd ~/ && git clone git@github.com:tamnan/huobi_turnover.git
```
2. Enter the huobi_turnover folder:
```sh
cd huobi_turnover
```
3. In command line: 
```sh
sudo apt-get install -y python3-venv && python3 -m venv venv && source venv/bin/activate && pip3 install --upgrade pip && pip3 install -r requirements.txt
```

## Usage

BEFORE USING make sure you have ```settings.txt``` with huobi api keys in the same folder (pls see example)

1. Make turnover up to 1205$:
```~/houbi_turnover/venv/bin/python3 ~/houbi_turnover/main.py -t 1205```

2. Make turnover up to 1205$ and print process into the terminal:
```~/houbi_turnover/venv/bin/python3 ~/houbi_turnover/main.py -t 1205 -v debug```

