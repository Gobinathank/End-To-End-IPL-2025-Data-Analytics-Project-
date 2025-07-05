
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import asyncio

# Load CSV file
df = pd.read_csv('espncricinfo.csv')
scorecard_links = df['SCORECARD'].dropna().tolist()


# Store results
bowling_data = []

async def scrape_bowling_summary():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # show browser for debugging
        page = await browser.new_page()

        for url in scorecard_links:
            try:
                print(f"Scraping: {url}")
                await page.goto(url, timeout=60000)
                await page.wait_for_timeout(5000)

                html = await page.content()
                print("\n=== HTML Preview ===")
                print(html[:1000])  # show sample HTML to debug

                soup = BeautifulSoup(html, 'html.parser')

                # Use your precise selector to target the second bowling table
                bowling_tables = soup.select("table:nth-of-type(2)")
                print(f"Found {len(bowling_tables)} bowling table(s)")

                for table in bowling_tables:
                    team_tag = table.find_previous('span', class_='ds-text-title-xs ds-font-bold ds-capitalize')
                    team_name = team_tag.text.strip() if team_tag else 'Unknown Team'

                    rows = table.select('tbody tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 6:
                            bowler = cols[0].text.strip()
                            overs = cols[1].text.strip()
                            maidens = cols[2].text.strip()
                            runs = cols[3].text.strip()
                            wickets = cols[4].text.strip()
                            econ = cols[5].text.strip()

                            bowling_data.append({
                                'Team': team_name,
                                'Bowler': bowler,
                                'Overs': overs,
                                'Maidens': maidens,
                                'Runs': runs,
                                'Wickets': wickets,
                                'Economy': econ,
                                'Match Link': url
                            })

            except Exception as e:
                print(f"Error in {url}: {e}")

        await browser.close()

    # Save to Excel
    bowling_df = pd.DataFrame(bowling_data)
    bowling_df.to_excel('bowling_summary.xlsx', index=False)
    print("✅ Saved to 'bowling_summary.xlsx'")

# Entry point
if __name__ == "__main__":
    asyncio.run(scrape_bowling_summary())
