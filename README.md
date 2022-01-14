# huobi_turnover
script make automated trades to get a needed amount of turnover

## Setup
1. Create folder:
```sh mkdir huobi_turnover
2. Enter the huobi_turnover folder:
```sh cd the huobi_turnover folder
4. In command line:
```sh sudo apt-get install -y python3-venv && python3 -m venv venv && source venv/bin/activate && pip3 install --upgrade pip && chmod +x main.py && pip3 install -r requirements.txt && pyt="$(pwd)/venv/bin/python3"

## Usage
1. Make turnover up to 1205$:
```sh $pyt main.py -t 1205

2. Make turnover up to 1205$ and print process into the terminal:
```sh $pyt main.py -t 1205 -v debug

