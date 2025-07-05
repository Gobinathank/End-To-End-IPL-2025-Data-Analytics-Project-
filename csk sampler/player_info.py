import pandas as pd
import asyncio
from playwright.async_api import async_playwright

async def scrape_filtered_player_fields():
    team_url = "https://www.espncricinfo.com/team/chennai-super-kings-335974"
    player_data = []

    REQUIRED_FIELDS = [
        "Full Name", "Born", "Age", "Batting style", "Bowling style", "Playing role"
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(team_url)
        await page.wait_for_timeout(3000)

        # Get list of players
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
            if len(selected) == 4:
                break

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

            data = {field: "nil" for field in REQUIRED_FIELDS}

            for i in range(1, 20):  # look through first 20 blocks
                selector = f'div.ds-grid.lg\\:ds-grid-cols-3.ds-grid-cols-2.ds-gap-4.ds-mb-8 > div:nth-child({i})'
                try:
                    block = page.locator(selector)
                    spans = await block.locator("span").all()
                    if len(spans) >= 2:
                        label = (await spans[0].inner_text()).strip()
                        value = (await spans[1].inner_text()).strip()
                        if label in data:
                            data[label] = value
                except:
                    continue

            player_data.append({
                "Player Name": name,
                "Full Name": data["Full Name"],
                "Born": data["Born"],
                "Age": data["Age"],
                "Batting Style": data["Batting style"],
                "Bowling Style": data["Bowling style"],
                "Playing Role": data["Playing role"],
                "Profile Link": profile_url
            })

        await browser.close()

    pd.DataFrame(player_data).to_excel("ipl_2025_csk_4players_filtered.xlsx", index=False)
    print("✅ Saved cleaned info to ipl_2025_csk_4players_filtered.xlsx")

# Run
asyncio.run(scrape_filtered_player_fields())
