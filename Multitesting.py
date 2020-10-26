#!/usr/bin/python3
#A script to test multiple multiprocessing libraries to determine which is fastest.

import multiprocessing
import json
import requests
import asyncio
import aiohttp
import threading
from queue import Queue
import sys

url = ''	#Front of the url sandwich. Expects string.
end = ''	#Back of the url sandwich. Expects string.
filechosen = ''	#Variable in the url sandwich. Expects file of variables.

#Multiprocessing
def multipooltest(urls):
	response = requests.get(urls)
	return response.text

#Asyncio
async def asyncget(sem, session, link):
	async with sem:
		async with session.get(link) as resp:
			return await resp.text()

async def aioreq(urls):
	sem = asyncio.Semaphore(3)
	async with aiohttp.ClientSession() as session:
		response = await asyncio.gather(
			*[asyncget(sem, session, i) for i in urls]
		)
		return response

#threading
def threadtest(q, result):
	while not q.empty():
		work = q.get()
		response = requests.get(work[1])
		result[work[0]] = response.text
		q.task_done()
	return True

#URL Construction
def urlsget():
	with open(filechosen, 'r') as r:
		query = []
		for line in r:
			line = line.rstrip()
			if end:
				link = url + line + end
			else:
				link = url + line
			query.append(link)
	return query

choice = []
choice = sys.argv
choice = int(choice[1])
urls = urlsget()
print(urls)
q = Queue(maxsize=0)
numthreads = min(50, len(urls))

if choice == 1:	#Multiprocessing, Pool
	pool = multiprocessing.Pool()
	results = pool.map(multipooltest, urls)
	pool.close()
	pool.join()
	print(results)

elif choice == 2: #asyncio
	results = asyncio.run(aioreq(urls))
	print(results)

elif choice == 3: #thread
	results = [{} for x in urls]
	threads = []
	for i in range(len(urls)):
		q.put((i,urls[i]))

	for i in range(numthreads):
		process = threading.Thread(target=threadtest, args=(q, results))
		process.setDaemon(True)
		process.start()

	q.join()
	print(results)

else:
	print('No result.')
