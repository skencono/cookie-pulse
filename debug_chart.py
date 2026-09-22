#!/usr/bin/env python3
"""Check why chartOut stays on 'loading'."""
import asyncio
from playwright.async_api import async_playwright

CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"])
        pg = await b.new_page(viewport={"width": 1440, "height": 1000})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:300]))
        pg.on("console", lambda m: errs.append(f"{m.type}: {m.text[:250]}") if m.type == "error" else None)
        await pg.goto("http://127.0.0.1:8787/", wait_until="domcontentloaded", timeout=60000)
        await pg.wait_for_timeout(10000)
        print("chartOut HTML:", (await pg.evaluate("() => document.getElementById('chartOut').innerHTML"))[:300])
        print("rows:", await pg.evaluate("() => document.querySelectorAll('#chartOut .row').length"))
        # call loadStats manually and see
        r = await pg.evaluate("""async () => {
            try {
              const res = await fetch('http://127.0.0.1:8787/api/stats');
              const d = await res.json();
              return 'analytics days=' + (d.analytics && d.analytics.days ? d.analytics.days.length : 'MISSING');
            } catch(e) { return 'ERR ' + e.message; }
        }""")
        print("manual:", r)
        print("errors:", errs[:6])
        await b.close()

asyncio.run(main())
