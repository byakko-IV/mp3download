from urllib2 import urlopen, Request, HTTPError, URLError
from bs4 import BeautifulSoup
from getopt import getopt, GetoptError
import sys
import os
import getpass

version = "mp3download 1.0 veta"
listing = 0
automatic = True
directory = "C:\\Users\\"+ getpass.getuser() +"\\Music\\canciones\\"
song = ""
option = 0
opendir = False
playsong = False

def usage():
	print """                             Wellcome to mp3download.py

Usage of mp3download.py: mp3download <options> 

-h --help                                 -Displays this information
-s --song                                 -Song name to download
-l --list                                 -List the number of found items idicated as parameter
-a --automatic                            -This flag enables automatic download  (default option)
-d --directory                            -Indicate a file directory to download (default directory Music)
-o                                        -This parameter indicates a number of the result set to download
-V --version                              -Shows the scripts version 
-O --open                                 -Open the download folder when download is finished
-P --play                                 -Plays the song when the download is finished

Examples:

mp3download.py -s "songs name"
mp3download.py -s "songs name" -l 30
mp3download.py -s "songs name" -o 4 -d "Descargas/"
mp3download.py -s "songs name" -l 10 -P

"""
	sys.exit(0)

def main():
	global version
	global song
	global listing
	global automatic
	global directory
	global option
	global opendir
	global playsong

	if not len(sys.argv[1:]):
		usage()
	try:
		opts, args = getopt(sys.argv[1:], "s:l:ad:o:VhOP", ["song", "list", "automatic", "directory", "version", "help", "open", "play"])
	except GetoptError as err:
		print str(err)
		usage()

	for o,a in opts:
		if o in ("-s", "--song"):
			song = a
		elif o in ("-l", "--list"):
			listing = int(a)
			automatic = False
		elif o in ("-a", "--automatic"):
			automatic = True
			listing = 0
		elif o in ("-d", "--directory"):
			directory = a
		elif o in ('-o'):
			option = int(a) - 1
		elif o in ("-V", "--version"):
			print version
		elif o in ('-h', '--help'):
			usage()
		elif o in ('-O', '--open'):
			opendir = True
		elif o in ('-P', '--play'):
			playsong = True	
		else:
			usage()

	if len(song) and listing < 1 and automatic == True:
		fnd(song)
	elif len(song) and listing > 0:
		fnl(song)

def get_session():
	print "Connecting..."
	try:
		headers = {"User-Agent":"Mozilla 5.10"}
		html = "https://mp3skull.wtf"
		request = Request(html, None, headers)
		response = urlopen(request)
		bsObj = BeautifulSoup(response, 'html.parser')
		nameList = bsObj.find("input", {"name":"fckh"})
	except URLError as err:
		print str(err)

	return nameList['value']

def find(sn):
	result = []

	try:
		session = get_session()
		print "Searching..."
		s = sn
		sn = song.replace(' ', '+')
		headers = {"User-Agent":"Mozilla 5.10"}
		html = "https://mp3skull.wtf/search_db.php?q="+sn+"&fckh="+session
		request = Request(html, None, headers)
		response = urlopen(request)
	except HTTPError as err:
		print str(err)
	except URLError as err:
		print str(err)

	bsObj = BeautifulSoup(response, 'html.parser')
	nameList = bsObj.findAll("div", {"class":"mp3_title"})
	linkList = bsObj.findAll("div", {"class":"download_button"})

	if len(nameList):
		for i in xrange(len(nameList)):
			result.append([nameList[i].get_text(), linkList[i].a.get('href').replace(' ', '%20').encode('utf-8')])
	else:
		return result

	return result

def download(url, name):
	try:
		link = url
		u = urlopen(link)
		f = open(directory+name+".mp3", 'wb')
		meta = u.info()
		file_size = int(meta.getheaders("Content-Length")[0])
		print "Downloading: %s Bytes: %s" % (name, file_size)

		file_size_dl = 0
		block_sz = 8192
		while True:
			buffer = u.read(block_sz)
			if not buffer:
				break

			file_size_dl += len(buffer)
			f.write(buffer)
			status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
			status = status + chr(8)*(len(status)+1)
			if file_size_dl == file_size:
				os.system('color a')
			print status,
		f.close()
		os.system('color f')
		if opendir:
			os.system('explorer '+directory)
		if playsong:
			os.system('explorer '+directory+name+".mp3")
	except HTTPError as e:
		print "Error: The file can't be downloaded"
	except URLError:
		print "Error: Url exception"
	except IOError:
		print "Error: The file %s can't be writen" % name

def fnd(sn):
	resultado = find(sn)

	if len(resultado):
		print "%i results found"  % len(resultado)
		download(resultado[option][1], resultado[option][0])
	else:
		print "0 results found"
		

def fnl(sn):
	global listing
	
	resultado = find(sn)

	if listing > len(resultado):
		listing = len(resultado)

	if len(resultado):
		print "%i results found"  % len(resultado)
	else:
		print "0 results found"
		sys.exit(0)

	for i in range(listing):
		print "[ %i ]- %s" % (i, resultado[i][0].encode('utf-8')[0:80])

	print "_" * 87

	try:
		option = int(raw_input("Pleas select number option: "))
	except ValueError:
		print "No valid option"
		sys.exit(0)

	download(resultado[option][1], resultado[option][0])

main()
