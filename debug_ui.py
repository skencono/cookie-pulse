#!/usr/bin/env python3
"""Debug why Cookie Pulse JS didn't run."""
import asyncio, os
from playwright.async_api import async_playwright

CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"])
        pg = await b.new_page(viewport={"width": 1440, "height": 1000})
        logs = []
        pg.on("console", lambda m: logs.append(f"CONSOLE {m.type}: {m.text[:300]}"))
        pg.on("pageerror", lambda e: logs.append(f"PAGEERROR: {str(e)[:400]}"))
        pg.on("requestfailed", lambda r: logs.append(f"REQFAIL: {r.url[:110]} :: {r.failure}"))
        await pg.goto("http://127.0.0.1:8787/", wait_until="domcontentloaded", timeout=60000)
        await pg.wait_for_timeout(9000)
        print("=== solanaWeb3 present? ===")
        print(await pg.evaluate("() => typeof window.solanaWeb3"))
        print("=== fetch test from page ===")
        print(await pg.evaluate("""async () => {
            try { const r = await fetch('http://127.0.0.1:8787/api/health');
                  const j = await r.json(); return 'OK ' + JSON.stringify(j).slice(0,120); }
            catch (e) { return 'FETCH ERR ' + e.message; } }"""))
        print("\n=== LOGS ===")
        for l in logs[:25]: print(" ", l)
        await b.close()

asyncio.run(main())
