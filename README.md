# huobi_turnover
script makes automated trades to get a needed amount of turnover. It trades solusdt pair. So your initial balance must be in solusdt or usdt, make sure you have it

## Setup
1. clone repo
```sh
cd ~/ && git clone git@github.com:tamnan/huobi_turnover.git
```
2. Enter the huobi_turnover folder:
```sh
cd ~/huobi_turnover
```
3. In command line: 
```sh
sudo apt-get install -y python3-venv && python3 -m venv venv && source venv/bin/activate && pip3 install --upgrade pip && pip3 install -r requirements.txt
```

## Usage

BEFORE USING make sure you have ```settings.txt``` with huobi api keys in the same folder (pls see example)

FOR PROPER trading you must give current solana price to the script as an argument -p:

1. ```cd ~/huobi_turnover```

2. Make turnover up to 1205$ trading by solusdt pair, keeping in mind solana price 145$:
```venv/bin/python3 main.py -t 1205 -p 145```

2. Make turnover up to 1205$ with solusdt current price equal to 145$ and print process into the terminal:
```venv/bin/python3 main.py -t 1205 -p 145 -v debug```

