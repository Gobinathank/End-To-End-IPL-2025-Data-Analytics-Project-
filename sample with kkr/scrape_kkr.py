import pandas as pd
import asyncio
from playwright.async_api import async_playwright

async def scrape_kkr_squad_players():
    squad_url = "https://www.espncricinfo.com/series/ipl-2025-1449924/kolkata-knight-riders-squad-1458633/series-squads"
    player_data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(squad_url)
        await page.wait_for_timeout(3000)

        # Get all player anchor tags under the player grid
        anchors = await page.locator("div.ds-p-0 a").all()
        all_players = []
        for anchor in anchors:
            name = await anchor.inner_text()
            href = await anchor.get_attribute("href")
            if name and href and "/cricketers/" in href:
                full_url = href if href.startswith("http") else "https://www.espncricinfo.com" + href
                all_players.append((name.strip(), full_url))

        print(f"✅ Found {len(all_players)} player links")
        all_players = all_players[:4]  # limit to 4 players

        for name, profile_url in all_players:
            print(f"🔍 Visiting {name} → {profile_url}")
            await page.goto(profile_url)

            try:
                await page.wait_for_selector(
                    "div.ds-grid.lg\\:ds-grid-cols-3.ds-grid-cols-2.ds-gap-4.ds-mb-8",
                    timeout=5000
                )
            except:
                print(f"⚠️ Info grid not found for {name}, skipping.")
                continue

            info_items = []
            for i in range(1, 20):
                sel = f"div.ds-grid.lg\\:ds-grid-cols-3.ds-grid-cols-2.ds-gap-4.ds-mb-8 > div:nth-child({i})"
                try:
                    text = await page.locator(sel).all_inner_texts()
                    if text:
                        info_items.append(text[0].strip())
                except:
                    continue

            player_data.append({
                "Team": "Kolkata Knight Riders",
                "Player Name": name,
                "Info Blocks": info_items,
                "Profile Link": profile_url
            })

        await browser.close()

    pd.DataFrame(player_data).to_excel("ipl_2025_kkr_4players_test.xlsx", index=False)
    print("✅ Saved KKR player info to ipl_2025_kkr_4players_test.xlsx")

# Run
if __name__ == "__main__":
    asyncio.run(scrape_kkr_squad_players())
