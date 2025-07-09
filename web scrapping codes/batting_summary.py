import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import asyncio

# Load CSV file
df = pd.read_csv('espncricinfo.csv')
scorecard_links = df['SCORECARD'].dropna().tolist()

# Store results
batting_data = []

async def scrape_batting_summary():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # show browser for debugging
        page = await browser.new_page()

        for url in scorecard_links:
            try:
                print(f"Scraping: {url}")
                await page.goto(url, timeout=60000)

                # Give JS enough time to render
                await page.wait_for_timeout(5000)

                # Print HTML content to debug what is loaded
                html = await page.content()
                print("\n=== HTML Preview ===")
                print(html[:1000])  # print first 1000 chars of page HTML

                soup = BeautifulSoup(html, 'html.parser')
                tables = soup.find_all('table', class_='ci-scorecard-table')

                for table in tables:
                    team_tag = table.find_previous('span', class_='ds-text-title-xs ds-font-bold ds-capitalize')
                    team_name = team_tag.text.strip() if team_tag else 'Unknown Team'

                    rows = table.select('tbody tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 8:
                            player = cols[0].text.strip()
                            runs = cols[2].text.strip()
                            balls = cols[3].text.strip()
                            fours = cols[5].text.strip()
                            sixes = cols[6].text.strip()
                            sr = cols[7].text.strip()

                            batting_data.append({
                                'Team': team_name,
                                'Player': player,
                                'Runs': runs,
                                'Balls': balls,
                                '4s': fours,
                                '6s': sixes,
                                'SR': sr,
                                'Match Link': url
                            })

            except Exception as e:
                print(f"Error in {url}: {e}")

        await browser.close()

    # Save to Excel
    batting_df = pd.DataFrame(batting_data)
    batting_df.to_excel('batting_summary.xlsx', index=False)
    print("Saved to 'batting_summary.xlsx'")

# Entry point
if __name__ == "__main__":
    asyncio.run(scrape_batting_summary())
