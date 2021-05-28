# Crypto Converter

## setup

```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## run

```shell
xterm +sb -w 0 -title "crypto converter" -geometry 40x15 \
    -e ".venv/bin/python main.py"
```