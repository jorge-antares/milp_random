# Run main.py

## 1. Run using uv

### Install and run for n=1000

```bash
uv run main.py 1000
```

## 2. Run using virtual environment

### Install
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip && pip install -r requirements.txt
```

### Run for n=1000
```bash
source .venv/bin/activate
python main.py 1000
```


