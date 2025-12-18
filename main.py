import ao3_scraper
import ff_scraper

if __name__ == "__main__":
    #model = "phi4-mini:latest"
    #model = "deepseek-r1:14b"
    model = "phi4"


    prompt = (
        "Return 'True' if the summary describes [INSERT YOUR SPECIFIC CRITERIA HERE]. "
        "Return 'False' otherwise."
        "Only respond with 'True' or 'False'. Text: {text}. "
    )

    print("🛠️ Starting script…")
    try:
        """  WARNING, THIS WONT RUN UNLESS YOU ADD YOUR CREDS FILE AND CHANGE THE URL KEY """

        """ WARNING ESTHER, YOU NEED TO HAVE CHROME INSTALLED"""

        ao3_scraper.FANDOM_TAG = "YOUR+FANDOM+TAG"
        ao3_scraper.scraper(prompt,model, start_page=ao3_scraper.START_PAGE, last_page=ao3_scraper.LAST_PAGE)

        ff_scraper.FANDOM_URL_PART = "YOUR_FANDOM_HERE"
        ff_scraper.scraper(prompt,model, start_page=ff_scraper.START_PAGE, last_page=ff_scraper.LAST_PAGE)

    except Exception as e:
        print(f"💥 Critical error: {e}")
    finally:
        print("🔚 Script ended")
