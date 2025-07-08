import pandas as pd
import asyncio
from playwright.async_api import async_playwright
# load only two team links at a time
#loading all will lead to access denial from the website
team_urls = {
    "Chennai Super Kings": "https://www.espncricinfo.com/series/ipl-2025-1449924/chennai-super-kings-squad-1458628/series-squads",
    "Delhi Capitals": "https://www.espncricinfo.com/series/ipl-2025-1449924/delhi-capitals-squad-1458631/series-squads",
    "Gujarat Titans": "https://www.espncricinfo.com/series/ipl-2025-1449924/gujarat-titans-squad-1458635/series-squads",
    "Kolkata Knight Riders": "https://www.espncricinfo.com/series/ipl-2025-1449924/kolkata-knight-riders-squad-1458633/series-squads",
    "Lucknow Super Giants": "https://www.espncricinfo.com/series/ipl-2025-1449924/lucknow-super-giants-squad-1458636/series-squads",
    "Mumbai Indians": "https://www.espncricinfo.com/series/ipl-2025-1449924/mumbai-indians-squad-1458620/series-squads",
    "Punjab Kings": "https://www.espncricinfo.com/series/ipl-2025-1449924/punjab-kings-squad-1458637/series-squads",
    "Rajasthan Royals": "https://www.espncricinfo.com/series/ipl-2025-1449924/rajasthan-royals-squad-1458634/series-squads",
    "Royal Challengers Bengaluru": "https://www.espncricinfo.com/series/ipl-2025-1449924/royal-challengers-bengaluru-squad-1458630/series-squads",
    "Sunrisers Hyderabad": "https://www.espncricinfo.com/series/ipl-2025-1449924/sunrisers-hyderabad-squad-1458622/series-squads"
}

async def scrape_all_teams_players():
    player_data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        for team_name, squad_url in team_urls.items():
            print(f" Visiting {team_name} squad page !!")
            await page.goto(squad_url)
            try:
                await page.wait_for_selector("div.ds-p-0", timeout=8000)
            except:
                print(f"!!! Could not load squad section for {team_name}")
                continue

            all_players = []
            for i in range(1, 5):  # squad blocks
                selector = f"div.ds-p-0 > div:nth-child({i}) div.ds-grid.lg\\:ds-grid-cols-2 > div a"
                anchors = await page.locator(selector).all()
                for anchor in anchors:
                    name = await anchor.inner_text()
                    href = await anchor.get_attribute("href")
                    if name and href and "/cricketers/" in href:
                        url = href if href.startswith("http") else "https://www.espncricinfo.com" + href
                        all_players.append((name.strip(), url))

            print(f" {team_name}: Found {len(all_players)} players")

            for name, profile_url in all_players:
                print(f" Visiting {name} → {profile_url} !!")
                await page.goto(profile_url)
                try:
                    await page.wait_for_selector(
                        "div.ds-grid.lg\\:ds-grid-cols-3.ds-grid-cols-2.ds-gap-4.ds-mb-8", timeout=5000
                    )
                except:
                    print(f"!! Info grid not found for {name}, skipping.")
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
                    "Team": team_name,
                    "Player Name": name,
                    "Info Blocks": info_items,
                    "Profile Link": profile_url
                })

        await browser.close()

    pd.DataFrame(player_data).to_excel("ipl_2025_all_team_players_raw.xlsx", index=False)
    print(" Saved to ipl_2025_all_team_players_raw.xlsx")

if __name__ == "__main__":
    asyncio.run(scrape_all_teams_players())
