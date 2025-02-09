import os
from playwright.async_api import async_playwright
import random
import asyncio

BOTBROWSER_EXEC_PATH = "/usr/bin/chromium-browser-stable"
EXTENSION_PATH = "./capsolver"

def get_random_proxy():
    # Commented out the ones that don't seems effective
    proxy_list = [
        "gate.nstproxy.io:24125:19FFD234FCF495D8-residential-country_IT-r_10m-s_m8GZ7wAwu3:Eze1pRr5",
        "gate.nstproxy.io:24125:19FFD234FCF495D8-residential-country_IT-r_10m-s_CSi85QDJA7:Eze1pRr5",
        # "gate.nstproxy.io:24125:19FFD234FCF495D8-residential-country_IT-r_10m-s_zpQrMylHJQ:Eze1pRr5",
        # "gate.nstproxy.io:24125:19FFD234FCF495D8-residential-country_IT-r_10m-s_QZ83eBSIwo:Eze1pRr5",
        "gate.nstproxy.io:24125:19FFD234FCF495D8-residential-country_IT-r_10m-s_NN8TTvXFv3:Eze1pRr5",
        # "gate.nstproxy.io:24125:19FFD234FCF495D8-residential-country_IT-r_10m-s_EJzfaqMztX:Eze1pRr5",
        # "gate.nstproxy.io:24125:19FFD234FCF495D8-residential-country_IT-r_10m-s_Fp6hU5XqkE:Eze1pRr5",
        # "gate.nstproxy.io:24125:19FFD234FCF495D8-residential-country_IT-r_10m-s_LFTGsk5dV2:Eze1pRr5",
        # "gate.nstproxy.io:24125:19FFD234FCF495D8-residential-country_IT-r_10m-s_13MbUOb8gA:Eze1pRr5",
        "gate.nstproxy.io:24125:19FFD234FCF495D8-residential-country_IT-r_10m-s_XSZKGJkGQ9:Eze1pRr5"
    ]
    random_proxy = random.choice(proxy_list)
    print(f"Using proxy: {random_proxy}")
    proxy_parts = random_proxy.split(":")
    proxy_server = f"http://{proxy_parts[0]}:{proxy_parts[1]}/"
    proxy_username = proxy_parts[2]
    proxy_password = proxy_parts[3]
    return proxy_server, proxy_username, proxy_password

PROXY_SERVER, PROXY_USERNAME, PROXY_PASSWORD = get_random_proxy()

def choose_random_profile(profile_folder):
    profiles = [f for f in os.listdir(profile_folder) if os.path.isfile(os.path.join(profile_folder, f))]
    if not profiles:
        raise FileNotFoundError(f"No profiles found in {profile_folder}")
    return os.path.join(profile_folder, random.choice(profiles))

BOT_PROFILE_PATH = choose_random_profile("./profiles")

# Specify the path for your persistent profile (user data directory)
USER_DATA_DIR = "./my_profile"

async def populate_history(page):
    await page.goto("https://www.google.com/", wait_until="commit")
    await page.goto("https://www.youtube.com", wait_until="commit")
    await page.goto("https://amazon.com/", wait_until="commit")
    await page.goto("https://www.merriam-webster.com/dictionary/purpose", wait_until="commit")

async def main():
    # Check if the profile directory exists; if not, create it.
    already_profiled = False
    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)
        print(f"Created user data directory: {USER_DATA_DIR}")
    else:
        already_profiled = True
        print(f"User data directory already exists: {USER_DATA_DIR}")

    try:
        async with async_playwright() as p:
            # Launch the browser in persistent context mode using the user data directory.
            # This means your profile (bookmarks, cookies, extensions, etc.) will be stored here.
            context = await p.chromium.launch_persistent_context(
                USER_DATA_DIR,
                headless=False,
                # If you need to use a specific executable (e.g., BotBrowser), uncomment the line below:
                executable_path=BOTBROWSER_EXEC_PATH,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    f"--disable-extensions-except={EXTENSION_PATH}",
                    f"--load-extension={EXTENSION_PATH}",
                    f"--bot-profile={BOT_PROFILE_PATH}",
                ],
                proxy={
                    "server": PROXY_SERVER,
                    "username": PROXY_USERNAME,
                    "password": PROXY_PASSWORD
                }
            )
            print("BROWSER OPENED with persistent profile.")

            page = await context.new_page()
            await page.add_init_script("""
                // @ts-expect-error - Playwright binding will cause leak
                delete window._playwrightbinding_;
                // @ts-expect-error - Playwright binding will cause leak
                delete window.__pwInitScripts;
            """)
            print("Navigating to first target page...")
            if not already_profiled:
                await populate_history(page)
            print("Navigating to second target page...")
            await page.goto("https://antcpt.com/score_detector/")
            await asyncio.sleep(3)
            print("Navigating to third target page...")
            await page.goto("https://job-boards.greenhouse.io/grafanalabs/jobs/5427808004")
            await asyncio.sleep(1000000)
            await context.close()

    except Exception as e:
        print(f"Error: {e}")
        raise
    
if __name__ == "__main__":
    asyncio.run(main())
