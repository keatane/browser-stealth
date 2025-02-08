import time
from playwright.sync_api import sync_playwright

BOTBROWSER_EXEC_PATH = "/usr/bin/chromium-browser-stable"
BOT_PROFILE_PATH = "/home/keat/Desktop/profile.json"

PROXY_SERVER = "http://gate.nstproxy.io:24125/"
PROXY_USERNAME = "DC359BAB64CBE705-residential-country_DE-r_10m-s_m96z2ohF1u"
PROXY_PASSWORD = "QGOxzBTs"
EXTENSION_PATH = "/home/keat/Desktop/capsolver"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            executable_path=BOTBROWSER_EXEC_PATH,  # Percorso dell'eseguibile di BotBrowser
            args=[
                f"--bot-profile={BOT_PROFILE_PATH}",  # Pass bot profile as an argument
            ],
            # proxy={
            #     "server": PROXY_SERVER,
            #     "username": PROXY_USERNAME,
            #     "password": PROXY_PASSWORD
            # }
        )
        print("BROWSER OPENED")
        page = browser.new_page()
        print("PRE-SCRIPT")
        # page.add_init_script("""
        #     // @ts-expect-error - Playwright binding will cause leak
        #     delete window._playwrightbinding_;
        #     // @ts-expect-error - Playwright binding will cause leak
        #     delete window.__pwInitScripts;
        # """)
        page.goto("https://antcpt.com/score_detector/")
        time.sleep(100000)
        browser.close()

if __name__ == "__main__":
    main()