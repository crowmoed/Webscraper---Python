import random
import ollama
from seleniumbase import Driver
from selenium.webdriver.common.by import By
import time
import gspread
from google.oauth2.service_account import Credentials

# ‑‑‑‑‑‑‑‑‑‑ CONFIG VARIABLES ‑‑‑‑‑‑‑‑‑‑
START_PAGE = 0      # <‑‑ change this to the page you want to begin on
LAST_PAGE  = 194    # highest page you plan to visit
FANDOM_TAG = "YOUR+FANDOM+TAG" # e.g. 'Original+Work' or specific fandom tag encoded
# -----------------------------------------

scopes = ['https://www.googleapis.com/auth/spreadsheets']
creds  = Credentials.from_service_account_file('credentials.json', scopes=scopes)
client = gspread.authorize(creds)

"""  WARNING, THIS WONT RUN UNLESS YOU CHAT THE API KEY FOR GOOGLE SHEETS IN THE "KEY" FILE  """

with open("key", "r") as f:
    key = f.read().strip()
sheet_id = key

workbook = client.open_by_key(sheet_id)
sheet = workbook.sheet1

example_prompt = (
    "Return 'True' if the summary describes [INSERT YOUR SPECIFIC CRITERIA HERE]. "
    "Return 'False' otherwise."
    "Only respond with 'True' or 'False'. Text: {text}. "
)

def nextpage(next_page, driver):
    """Load the requested page and clear any CAPTCHA."""
    # REPLACED: Generic URL structure with placeholder tag
    url = f'https://archiveofourown.org/works?commit=Sort+and+Filter&work_search%5Bsort_column%5D=revised_at&work_search%5Bother_tag_names%5D=&work_search%5Bexcluded_tag_names%5D=&work_search%5Bcrossover%5D=&work_search%5Bcomplete%5D=&work_search%5Bwords_from%5D=80000&work_search%5Bwords_to%5D=&work_search%5Bdate_from%5D=&work_search%5Bdate_to%5D=&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=&tag_id={FANDOM_TAG}&page={next_page}'
    print(f"\n📄 Moving to page {next_page}…")
    driver.uc_open_with_reconnect(url, 4)
    driver.uc_gui_click_captcha()
    print("✅ CAPTCHA handled")


def random_time():
    delay = random.uniform(10.0, 18.0)
    print(f"⏳ Random delay: {delay:.1f} s")
    return delay


def analyzetext(text: str, prompt_template: str, model: str) -> bool:
    """Ask Ollama whether the snippet matches our criteria."""
    print("\n🔍 Analyzing text snippet…")
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": "Answer with a single word: True or False."},
                {"role": "user",   "content": prompt_template.format(text=text)}
            ],
            options={"temperature": 0, "stop": ["\n"]}
        )
        verdict = response["message"]["content"].strip()
        result = verdict == "True"
        print(f"🤖 Analysis result: {result}")
        return result
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False


# REPLACED: Specific keywords removed for generic placeholder list
target_keywords = [
    "keyword_one",
    "keyword_two",
    "phrase to look for",
    "another criteria",
]


def findkeywordintext(text: str, keywords: list[str]) -> bool:
    # REPLACED: Removed specific print references
    print("\n🔍 Scanning for target keywords...")
    try:
        text_lower = text.lower()
        found_keywords = [kw for kw in keywords if kw.lower() in text_lower]

        if found_keywords:
            print(f"🤖 Found keywords: {', '.join(found_keywords)}")
            return True
        else:
            print("🤖 No keywords detected.")
            return False
    except Exception as e:
        print(f"❌ Error analyzing text: {e}")
        return False


def scraper(given_prompt,model, start_page: int = 1, last_page: int = LAST_PAGE):
    """Main scraping loop (resumable)."""

    prompt= given_prompt

    print("🚀 Starting scraper…")

    # Launch browser
    print("🖥️ Launching browser…")
    driver = Driver(uc=True)

    # Load the first requested page
    # REPLACED: Generic URL structure with placeholder tag
    url = f'https://archiveofourown.org/works?commit=Sort+and+Filter&work_search[sort_column]=revised_at&work_search[other_tag_names]=&work_search[excluded_tag_names]=&work_search[crossover]=&work_search[complete]=&work_search[words_from]=80000&work_search[words_to]=&work_search[date_from]=&work_search[date_to]=&work_search[query]=&work_search[language_id]=&tag_id={FANDOM_TAG}&page={start_page}'
    print(f"🌐 Loading initial page: {url}")
    driver.uc_open_with_reconnect(url, 4)
    driver.uc_gui_click_captcha()
    print("✅ Initial page ready")

    # Iterate from start_page up to last_page (inclusive)
    for page in range(start_page, last_page + 1):
        print(f"\n📖 Processing page {page}…")

        title_list = driver.find_elements(By.CSS_SELECTOR, 'div.header.module')
        desc_list  = driver.find_elements(By.CSS_SELECTOR, '.userstuff.summary')
        print(f"📊 Found {len(title_list)} stories on this page")

        for idx in range(len(desc_list)):
            print(f"\n📚 Story {idx + 1}/{len(desc_list)}")

            title_a = title_list[idx].find_element(By.CSS_SELECTOR, 'h4.heading a')
            title_text = title_a.text

            print(f"📝 Title: {title_text}…")

            if findkeywordintext(desc_list[idx].text, target_keywords):
                if analyzetext(desc_list[idx].text, prompt, model):
                    print("\n🌟 MATCH FOUND!")

                    story_link = title_a.get_attribute('href')
                    sheet.append_row([
                        title_text,
                        desc_list[idx].text,
                        page,
                        story_link
                    ])

        if page < last_page:
            # time.sleep(random_time())  # Optional throttling
            nextpage(page + 1, driver)

    print("\n🏁 Scraping complete!")
    driver.quit()


# Prompt template
# REPLACED: Specific criteria removed



if __name__ == "__main__":
    #model = "phi4-mini:latest"
    model = "phi4"

    print("🛠️ Starting script…")
    try:
        scraper(model, start_page=START_PAGE, last_page=LAST_PAGE)
    except Exception as e:
        print(f"💥 Critical error: {e}")
    finally:
        print("🔚 Script ended")