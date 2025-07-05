import pandas as pd
import asyncio
from playwright.async_api import async_playwright

async def scrape_all_info_blocks():
    team_url = "https://www.espncricinfo.com/team/chennai-super-kings-335974"
    player_data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(team_url)
        await page.wait_for_timeout(3000)

        # Player list from team page
        player_links = await page.locator(
            "#main-container > div.ds-relative > div > div.ds-flex.ds-space-x-5 > div.ds-grow > div.ds-w-full.ds-bg-fill-content-prime.ds-overflow-hidden.ds-rounded-xl.ds-border.ds-border-line.ds-mb-4 > div > div > div:nth-child(2) > ul > li > a"
        ).all()

        selected = []
        for anchor in player_links:
            name = await anchor.inner_text()
            href = await anchor.get_attribute("href")
            if not name or not href or "/cricketers/" not in href:
                continue
            url = href if href.startswith("http") else "https://www.espncricinfo.com" + href
            selected.append((name.strip(), url))

        for name, profile_url in selected:
            print(f"🔍 {name} → {profile_url}")
            await page.goto(profile_url)

            try:
                await page.wait_for_selector(
                    r"div.ds-grid.lg\:ds-grid-cols-3.ds-grid-cols-2.ds-gap-4.ds-mb-8", timeout=5000
                )
            except:
                print(f"⚠️ Info grid not found for {name}, skipping.")
                continue

            info_items = []
            for i in range(1, 20):  # check up to 20 blocks to be safe
                block_selector = f'div.ds-grid.lg\\:ds-grid-cols-3.ds-grid-cols-2.ds-gap-4.ds-mb-8 > div:nth-child({i})'
                try:
                    text = await page.locator(block_selector).all_inner_texts()
                    if text:
                        info_items.append(text[0].strip())
                except:
                    continue

            player_data.append({
                "Player Name": name,
                "Info Blocks": info_items,
                "Profile Link": profile_url
            })

        await browser.close()

    pd.DataFrame(player_data).to_excel("ipl_2025_csk_all_players_raw_info.xlsx", index=False)
    print("✅ Saved to ipl_2025_csk_all_players_raw_info.xlsx")

# Run
if __name__ == "__main__":
    asyncio.run(scrape_all_info_blocks())
