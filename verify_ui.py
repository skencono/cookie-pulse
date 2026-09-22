#!/usr/bin/env python3
"""Visual verify Cookie Pulse frontend with the local CloakBrowser chromium."""
import asyncio, os
from playwright.async_api import async_playwright

CHROME = "/home/ubuntu/.cloakbrowser/chromium-146.0.7680.177.5/chrome"
OUT = "/tmp/cc-shots"
os.makedirs(OUT, exist_ok=True)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"])
        pg = await b.new_page(viewport={"width": 1440, "height": 1100})
        logs = []
        pg.on("console", lambda m: logs.append(f"{m.type}: {m.text[:200]}"))
        pg.on("pageerror", lambda e: logs.append(f"PAGEERROR: {str(e)[:250]}"))
        await pg.goto("http://127.0.0.1:8787/", wait_until="networkidle", timeout=60000)
        await pg.wait_for_timeout(7000)
        await pg.screenshot(path=f"{OUT}/full.png", full_page=True)
        await pg.screenshot(path=f"{OUT}/top.png")
        # read rendered numbers
        stats = await pg.evaluate("""() => ({
            slot: document.getElementById('sSlot')?.textContent,
            tps: document.getElementById('sTps')?.textContent,
            epoch: document.getElementById('sEpoch')?.textContent,
            supply: document.getElementById('sSupply')?.textContent,
            txcount: document.getElementById('sTxCount')?.textContent,
            bridged: document.getElementById('bLocked')?.textContent,
            price: document.getElementById('gPrice')?.textContent,
            pooldata: document.getElementById('poolTag')?.textContent,
            pools: document.querySelectorAll('#poolPills .pill').length,
            progrows: document.querySelectorAll('#progOut .row').length,
            feeds: document.querySelectorAll('#actOut .row').length,
            nfts: document.querySelectorAll('#nftOut .row').length,
            chart: document.querySelectorAll('#chartOut .row').length,
            toast: document.getElementById('toast')?.textContent,
        })""")
        print("=== RENDERED VALUES ===")
        for k, v in stats.items():
            print(f"  {k:10} {v}")
        print("\n=== CONSOLE ===")
        for l in logs[:15]:
            print("  ", l)
        await b.close()

asyncio.run(main())
