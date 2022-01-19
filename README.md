1st step: BTCIDR -> asks
2nd step: ETHBTC -> asks
3rd step: ETHIDR -> bids

formula = (ETHIDR/ETHBTC)/BTCIDR*100% > 100,5%

---

1. buat venv: `py -m venv venv`
2. activate venv-nya: `/venv/Script/activate`
3. kalau udah activate, install requiremnts: `pip install -r requirements.txt`
4. buat file `.env` isinya 

```
KEY_ID=<keyid dari luno>
KEY_SECRET=<keysecret dari luno>
```

5. run: `py app.py`
