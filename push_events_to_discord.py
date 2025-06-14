# -*- coding: utf-8 -*-
import os, textwrap, requests, pandas as pd
from io import StringIO
from datetime import datetime, timedelta, timezone

CSV_URL     = os.getenv("CSV_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
TZ = timezone(timedelta(hours=8))        # GMT+8

csv = requests.get(CSV_URL, timeout=10).text
df  = pd.read_csv(StringIO(csv))

df["售票時間"] = pd.to_datetime(
    df["售票時間"].str.extract(r"(\d{4}\.\d{2}\.\d{2}.*?)(?:\\n|$)")[0],
    format="%Y.%m.%d(%a) %H:%M",
    errors="coerce"
).dt.tz_localize(TZ, nonexistent="shift_forward")

now, tomorrow = datetime.now(TZ), datetime.now(TZ) + timedelta(days=1)
today = df[df["售票時間"].between(now, tomorrow)].sort_values("售票時間")

msg = (
    f"今天（{now:%Y-%m-%d}）沒有即將開賣的場次 🎉"
    if today.empty else
    "**今日即將開賣**\n" + "\n".join(
        f"● **{r['售票時間']:%m/%d %H:%M}** | {r['活動名稱']} | {r['售票網址']}"
        for _, r in today.iterrows()
    )
)

for chunk in textwrap.wrap(msg, 2000, break_long_words=False):
    requests.post(WEBHOOK_URL, json={"content": chunk})
