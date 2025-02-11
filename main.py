import os
import random
import asyncio
from rebrowser_playwright.async_api import async_playwright


async def get_random_proxy():
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

async def choose_random_profile(profile_folder):
    profiles = [f for f in os.listdir(profile_folder) if os.path.isfile(os.path.join(profile_folder, f))]
    if not profiles:
        raise FileNotFoundError(f"No profiles found in {profile_folder}")
    return os.path.join(profile_folder, random.choice(profiles))

async def load_links(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines()]

async def populate_history(page, history):
    for link in history:
        print(f"Visiting {link}...")
        await page.goto(link, wait_until="commit")
        await asyncio.sleep(random.randint(1, 10)) 

async def main():
    BOTBROWSER_EXEC_PATH = "/usr/bin/chromium-browser-stable"
    EXTENSION_PATH = "./capsolver"
    HISTORY = await load_links("histories/italian.txt")
    PROXY_SERVER, PROXY_USERNAME, PROXY_PASSWORD = await get_random_proxy()
    BOT_PROFILE_PATH = await choose_random_profile("./profiles")
    USER_DATA_DIR = "./my_profile"
    
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
                    f"--disable-extensions-except={EXTENSION_PATH}",
                    f"--load-extension={EXTENSION_PATH}",
                    f"--bot-profile={BOT_PROFILE_PATH}",
                    "--start-maximized",
                    "--disable-blink-features=AutomationControlled"
                ],
                proxy={
                    "server": PROXY_SERVER,
                    "username": PROXY_USERNAME,
                    "password": PROXY_PASSWORD
                }
            )
            print("BROWSER OPENED with persistent profile.")

            context.set_default_navigation_timeout(60000)
            context.set_default_timeout(60000)
            page = await context.new_page()
            await page.evaluate("navigator.webdriver = undefined")
            await page.evaluate("""() => {
                Object.defineProperty(navigator, 'webdriver', {get: () => [false]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
            }""")
            await page.evaluate("""() => {
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Intel';
                    if (parameter === 37446) return 'Intel HD Graphics';
                    return getParameter(parameter);
                };
            }""")
            await page.add_init_script("""
                // @ts-expect-error - Playwright binding will cause leak
                delete window._playwrightbinding_;
                // @ts-expect-error - Playwright binding will cause leak
                delete window.__pwInitScripts;
            """)
            if not already_profiled:
                await populate_history(page, HISTORY)
            print("Navigating to first target page...")
            await page.goto("https://antcpt.com/score_detector/")
            await asyncio.sleep(4)
            print("Navigating to second target page...")
            # await page.goto("https://jobs.lever.co/BTSE/72f4e7a1-7e8f-4a62-ae89-87cc457423ce")
            await page.goto("https://job-boards.greenhouse.io/grafanalabs/jobs/5373283004")
            await asyncio.sleep(1000000)
            await context.close()

    except Exception as e:
        print(f"Error: {e}")
        raise
    
if __name__ == "__main__":
    asyncio.run(main())
