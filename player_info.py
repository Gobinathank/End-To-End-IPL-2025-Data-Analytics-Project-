import pandas as pd
from playwright.async_api import async_playwright
import asyncio

team_urls = {
    'Chennai Super Kings': 'https://www.espncricinfo.com/series/ipl-2025-1449924/chennai-super-kings-squad-1458628/series-squads',
    'Delhi Capitals': 'https://www.espncricinfo.com/series/ipl-2025-1449924/delhi-capitals-squad-1458631/series-squads',
    'Gujarat Titans': 'https://www.espncricinfo.com/series/ipl-2025-1449924/gujarat-titans-squad-1458635/series-squads',
    'Kolkata Knight Riders': 'https://www.espncricinfo.com/series/ipl-2025-1449924/kolkata-knight-riders-squad-1458633/series-squads',
    'Lucknow Super Giants': 'https://www.espncricinfo.com/series/ipl-2025-1449924/lucknow-super-giants-squad-1458636/series-squads',
    'Mumbai Indians': 'https://www.espncricinfo.com/series/ipl-2025-1449924/mumbai-indians-squad-1458620/series-squads',
    'Punjab Kings': 'https://www.espncricinfo.com/series/ipl-2025-1449924/punjab-kings-squad-1458637/series-squads',
    'Rajasthan Royals': 'https://www.espncricinfo.com/series/ipl-2025-1449924/rajasthan-royals-squad-1458634/series-squads',
    'Royal Challengers Bengaluru': 'https://www.espncricinfo.com/series/ipl-2025-1449924/royal-challengers-bengaluru-squad-1458630/series-squads',
    'Sunrisers Hyderabad': 'https://www.espncricinfo.com/series/ipl-2025-1449924/sunrisers-hyderabad-squad-1458622/series-squads'
}

player_info = []
seen_profiles = set()

async def scrape_players():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        for team, url in team_urls.items():
            print(f"🔍 Visiting {team}")
            await page.goto(url)
            await page.wait_for_timeout(4000)

            # Use general selector for player profile links
            player_cards = await page.locator('a[href*="/player/"]').all()
            print(f"🧾 Found {len(player_cards)} player links for {team}")

            for card in player_cards:
                player_name = await card.inner_text()
                href = await card.get_attribute('href')
                if not player_name or not href or '/player/' not in href:
                    continue

                profile_url = "https://www.espncricinfo.com" + href
                if profile_url in seen_profiles:
                    continue
                seen_profiles.add(profile_url)

                await page.goto(profile_url)
                await page.wait_for_timeout(3000)

                labels = await page.locator('div.ds-grid span.ds-text-title-s.ds-font-bold').all()
                values = await page.locator('div.ds-grid span.ds-text-title-s.ds-font-bold + span').all()
                data = {await labels[i].inner_text(): await values[i].inner_text() for i in range(min(len(labels), len(values)))}

                player_info.append({
                    'Player Name': player_name,
                    'Team': team,
                    'Role': data.get('Playing role', ''),
                    'Batting Style': data.get('Batting style', ''),
                    'Bowling Style': data.get('Bowling style', ''),
                    'Date of Birth': data.get('Born', ''),
                    'Nationality': data.get('Nationality', ''),
                    'Profile Link': profile_url
                })

        await browser.close()

    df = pd.DataFrame(player_info)
    df.to_excel("ipl_2025_players_info.xlsx", index=False)
    print("✅ Saved to ipl_2025_players_info.xlsx")

if __name__ == "__main__":
    asyncio.run(scrape_players())
