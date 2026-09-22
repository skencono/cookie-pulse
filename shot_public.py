#!/usr/bin/env python3
"""Screenshot the PUBLIC tunnel URL — proof the deployed app works end to end."""
import asyncio
from playwright.async_api import async_playwright

CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome"
URL = "https://buy-priorities-town-offshore.trycloudflare.com"
OUT = "/home/ubuntu/cookiechain/shots"

async def main():
    import os; os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"])
        pg = await b.new_page(viewport={"width": 1400, "height": 1150},
                              device_scale_factor=1.5)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
        await pg.goto(URL, wait_until="domcontentloaded", timeout=90000)
        await pg.wait_for_timeout(14000)
        vals = await pg.evaluate("""() => ({
            title: document.title,
            slot: document.getElementById('sSlot')?.textContent,
            supply: document.getElementById('sSupply')?.textContent,
            bridged: document.getElementById('bLocked')?.textContent,
            price: document.getElementById('gPrice')?.textContent,
            poolTag: document.getElementById('poolTag')?.textContent,
            chartRows: document.querySelectorAll('#chartOut .row').length,
            txRows: document.querySelectorAll('#actOut .row').length,
            progRows: document.querySelectorAll('#progOut .row').length,
            nftRows: document.querySelectorAll('#nftOut .row').length,
        })""")
        print("=== PUBLIC URL RENDER ===")
        for k, v in vals.items(): print(f"  {k:10} {v}")
        print("  errors:", errs[:3] or "none")
        await pg.screenshot(path=f"{OUT}/public-full.png", full_page=True)
        await pg.screenshot(path=f"{OUT}/public-hero.png")
        await b.close()

asyncio.run(main())
