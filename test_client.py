from multiprocessing import Pool
from time import sleep

from Client import Client
from DFClient import DFEKeyExchange


def start_async_rounds(process_count):
    # Each process needs to start with a slight delay to prevent race conditions
    sleepmap = [0.1 * x for x in range(0, process_count)]
    start_delay = max(sleepmap) + 0.1
    args = [(s, start_delay) for s in sleepmap]
    p = Pool(processes=process_count)
    pmap = p.map_async(start_game, args)
    return pmap.get()


def start_game(args):
    sleeptime, start_delay = args
    sleep(sleeptime)
    cli = Client(DFEKeyExchange)

print("arync")
start_async_rounds(2)
