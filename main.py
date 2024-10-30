import time 
import os
import asyncio

from utils.logo import print_logo
from utils.kick import _kick_
from utils.scanner import main

from rich import print
from rich.prompt import Prompt
from rich.console import Console

console = Console()
input = Prompt.ask

modules = """[bright_white] [1] :mag: Scan for Bluetooth Devices
 [2] :satellite: Kick Out Bluetooth Devices
[red] [Q] :door: Exit (Ctrl + c)
"""

async def Main_Modules():
    print_logo()
    print(modules)

    user_choice = input("[cyan] :question: Enter your choice ")

    if user_choice == "1":
        mac_address = await main()  # testando `await` em vez de `asyncio.run`
        print("Selected MAC address:", mac_address)
        
        scan_again = input("[green] :question: Do you want to perform the scan again (y/n) ").lower() == "y"
        if scan_again:
            await Main_Modules()  # testando recursivamente `await Main_Modules()`

        kick_ard = input("[red] :rocket: Do you want to kick the user ").lower() == "y"
        start_time = input("[red] :question: In how many seconds do you want to start the attack ")
        
        if kick_ard:
            _kick_(mac_address, 600, 10, int(start_time))
        else:
            print(":door: Exiting...")
    elif user_choice == "2":
        mac_address = input("[red] :signal_strength: Enter the Mac Address ")
        start_time = input("[red] :question: In how many seconds do you want to start the attack ")
        _kick_(mac_address, 600, 20, int(start_time))
        
    elif user_choice.lower() == "q":
        console.clear() 
        exit()
    else:
        print("[red] :warning: Invalid Option")
        time.sleep(1)
        await Main_Modules()  # `await` para a recursão

async def main_loop():
    try:
        # Turns Bluetooth Adapter - ON
        os.system("rfkill unblock bluetooth")
        # ----------------------------------
        await Main_Modules() 
    except KeyboardInterrupt:
        console.clear()
        print("[red] :door: User Quit")
        exit()
    except Exception as e:
        console.clear()
        print(f"[red] :warning: ERROR VALUE [{e}]")
        exit()

if __name__ == "__main__":
    asyncio.run(main_loop()) 
