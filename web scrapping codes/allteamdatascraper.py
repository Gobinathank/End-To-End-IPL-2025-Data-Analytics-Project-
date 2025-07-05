
import pandas as pd
import asyncio
from playwright.async_api import async_playwright

# All 10 IPL 2025 team URLs
team_urls = {
    "Chennai Super Kings": "https://www.espncricinfo.com/team/chennai-super-kings-335974",
    "Delhi Capitals": "https://www.espncricinfo.com/team/delhi-capitals-335975",
    "Gujarat Titans": "https://www.espncricinfo.com/team/gujarat-titans-1298769",
    "Kolkata Knight Riders": "https://www.espncricinfo.com/team/kolkata-knight-riders-335971",
    "Lucknow Super Giants": "https://www.espncricinfo.com/team/lucknow-super-giants-1298768",
    "Mumbai Indians": "https://www.espncricinfo.com/team/mumbai-indians-335978",
    "Punjab Kings": "https://www.espncricinfo.com/team/punjab-kings-335973",
    "Rajasthan Royals": "https://www.espncricinfo.com/team/rajasthan-royals-335977",
    "Royal Challengers Bengaluru": "https://www.espncricinfo.com/team/royal-challengers-bengaluru-335970",
    "Sunrisers Hyderabad": "https://www.espncricinfo.com/team/sunrisers-hyderabad-628333"
}

async def scrape_all_teams_players():
    player_data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        for team_name, team_url in team_urls.items():
            print(f"\n🏏 Visiting {team_name}")
            try:
                await page.goto(team_url)
                await page.wait_for_timeout(3000)
            except:
                print(f"❌ Failed to load team page: {team_url}")
                continue

            # Get player links
            try:
                player_links = await page.locator(
                    "#main-container > div.ds-relative > div > div.ds-flex.ds-space-x-5 > div.ds-grow > div.ds-w-full.ds-bg-fill-content-prime.ds-overflow-hidden.ds-rounded-xl.ds-border.ds-border-line.ds-mb-4 > div > div > div:nth-child(2) > ul > li > a"
                ).all()
            except:
                print(f"⚠️ Could not find player list on {team_name}")
                continue

            selected = []
            for anchor in player_links:
                name = await anchor.inner_text()
                href = await anchor.get_attribute("href")
                if not name or not href or "/cricketers/" not in href:
                    continue
                url = href if href.startswith("http") else "https://www.espncricinfo.com" + href
                selected.append((name.strip(), url))

            for name, profile_url in selected:
                print(f"   🔍 {name} → {profile_url}")
                await page.goto(profile_url)

                try:
                    await page.wait_for_selector(
                        r"div.ds-grid.lg\:ds-grid-cols-3.ds-grid-cols-2.ds-gap-4.ds-mb-8", timeout=5000
                    )
                except:
                    print(f"   ⚠️ Info grid not found for {name}, skipping.")
                    continue

                info_items = []
                for i in range(1, 20):  # safe range for block count
                    block_selector = f'div.ds-grid.lg\\:ds-grid-cols-3.ds-grid-cols-2.ds-gap-4.ds-mb-8 > div:nth-child({i})'
                    try:
                        text = await page.locator(block_selector).all_inner_texts()
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

    pd.DataFrame(player_data).to_excel("ipl_2025_all_teams_players_info.xlsx", index=False)
    print("\n✅ All player info saved to ipl_2025_all_teams_players_info.xlsx")

# Run
if __name__ == "__main__":
    asyncio.run(scrape_all_teams_players())
