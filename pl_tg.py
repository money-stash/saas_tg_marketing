import asyncio
import random
from random import randint
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)
from pyro_funcs.login_funcs import get_full_phone_number, get_login_code
import os
from config import PROXY_FILE


def get_random_proxy():
    with open(PROXY_FILE, "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    return random.choice(lines)


TELEGRAM_URL = "https://web.telegram.org/a/"
LOGIN_BUTTON_TEXT = "Log in by phone Number"
TIMEOUT_BEFORE_CLICK = 10
TIMEOUT_BEFORE_CLOSE = 10


async def handle_telegram_login(
    session_path,
    json_path,
    action="change_image",
    name="New Name",
    last_name="New Last Name",
    bio="This is a new bio",
    username="new_username",
):
    async with async_playwright() as p:
        # proxy = get_random_proxy()
        # ip, port, user, password = proxy.split(":")
        # proxy_server = f"http://{ip}:{port}"
        # proxy_creds = {"server": proxy_server, "username": user, "password": password}
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        session_name = os.path.basename(session_path)

        await page.goto(TELEGRAM_URL)
        await asyncio.sleep(TIMEOUT_BEFORE_CLICK)

        try:
            login_button = page.get_by_text(LOGIN_BUTTON_TEXT)
            await login_button.click()
            print("Clicked login button.")
        except PlaywrightTimeoutError:
            print("Login button not found.")
            await browser.close()
            return

        phone_number = await get_full_phone_number(
            session_path=session_path, json_path=json_path
        )
        if phone_number:
            input_element = await page.wait_for_selector("#sign-in-phone-number")
            await input_element.fill("")
            await input_element.type(phone_number)

            await asyncio.sleep(randint(3, 6))

            next_button = page.get_by_text("Next")
            await next_button.click()
            print("Clicked Next button.")

            await asyncio.sleep(3)

            login_code = await get_login_code(
                session_path=session_path,
                json_path=json_path,
            )

            # если вошли в аккаунт
            if login_code:
                code_input = await page.wait_for_selector("#sign-in-code")
                await code_input.fill("")
                await code_input.type(login_code)

                await asyncio.sleep(randint(3, 6))

                await page.wait_for_selector(
                    "xpath=/html/body/div[2]/div/div[1]/div/div[1]/div/div[1]/button/div[2]",
                    timeout=10000,
                )
                await page.click(
                    "xpath=/html/body/div[2]/div/div[1]/div/div[1]/div/div[1]/button/div[2]"
                )
                await asyncio.sleep(randint(3, 6))
                await page.wait_for_selector(
                    "xpath=/html/body/div[2]/div/div[1]/div/div[1]/div/div[1]/div/div[2]/div[1]",
                    timeout=10000,
                )
                await page.click(
                    "xpath=/html/body/div[2]/div/div[1]/div/div[1]/div/div[1]/div/div[2]/div[1]"
                )

                await page.wait_for_selector(
                    "xpath=/html/body/div[2]/div/div[1]/div[2]/div/div[1]/div[1]/div/button/div",
                    timeout=10000,
                )

                await page.click(
                    "xpath=/html/body/div[2]/div/div[1]/div[2]/div/div[1]/div[1]/div/button/div"
                )
                await asyncio.sleep(randint(3, 6))

                print("Clicked elements for changing")
                await asyncio.sleep(randint(3, 6))

                # ИЗМЕНЯЕМ АВУ
                if action == "change_image":
                    try:
                        await page.set_input_files(
                            "xpath=/html/body/div[2]/div/div[1]/div[2]/div/div[2]/div[2]/div/div[1]/div/div[1]/label/input",
                            "images/avatar.jpg",
                        )

                        await asyncio.sleep(randint(3, 6))
                        await page.click(
                            "xpath=/html/body/div[1]/div[2]/div/div/div[2]/div[2]/div/div[2]/button"
                        )

                    except Exception as e:
                        print(f"Failed to change image: {e}")

                # ИЗМЕНЯЕМ ИМЯ
                elif action == "change_name":
                    try:
                        name_input = await page.wait_for_selector(
                            "xpath=/html/body/div[2]/div/div[1]/div[2]/div/div[2]/div[2]/div/div[1]/div/div[2]/input"
                        )
                        await name_input.click()

                        await name_input.fill("")
                        await name_input.type(name)

                    except Exception as e:
                        print(f"Failed to change name: {e}")

                # ИЗМЕНЯЕМ ФАМИЛИЮ
                elif action == "change_last_name":
                    try:
                        last_name_input = await page.wait_for_selector(
                            "xpath=/html/body/div[2]/div/div[1]/div[2]/div/div[2]/div[2]/div/div[1]/div/div[3]/input"
                        )
                        await last_name_input.click()

                        await last_name_input.fill("")
                        await last_name_input.type(last_name)

                    except Exception as e:
                        print(f"Failed to change last name: {e}")

                # ИЗМЕНЯЕМ БИО
                elif action == "change_bio":
                    try:
                        bio_input = await page.wait_for_selector(
                            "xpath=/html/body/div[2]/div/div[1]/div[2]/div/div[2]/div[2]/div/div[1]/div/div[4]/textarea"
                        )
                        await bio_input.click()

                        await bio_input.fill("")
                        await bio_input.type(bio)

                    except Exception as e:
                        print(f"Failed to change bio: {e}")

                        await last_name_input.fill("")
                        await last_name_input.type(bio)

                    except Exception as e:
                        print(f"Failed to change last name: {e}")
                # ИЗМЕНЯЕМ ЮЗЕРНЕЙМ
                elif action == "change_username":
                    try:
                        username_input = await page.wait_for_selector(
                            "xpath=/html/body/div[2]/div/div[1]/div[2]/div/div[2]/div[2]/div/div[2]/div/div/input"
                        )
                        await username_input.click()

                        await username_input.fill("")
                        await username_input.type(username)

                    except Exception as e:
                        print(f"Failed to change username: {e}")

                        await last_name_input.fill("")
                        await last_name_input.type(username)

                    except Exception as e:
                        print(f"Failed to change last name: {e}")

                await asyncio.sleep(randint(3, 6))
                await page.click(
                    ".Button.FloatingActionButton.revealed.default.primary.round"
                )

            else:
                print("Login code not found. Please check your session and JSON files.")
                await browser.close()
                return

        else:
            print("Phone number not found.")

        await asyncio.sleep(2000)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(
        handle_telegram_login(
            session_path="sessions/179422896",
            json_path="sessions/179422896.json",
            action="change_name",
        )
    )
