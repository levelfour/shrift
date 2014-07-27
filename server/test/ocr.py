#!/usr/bin/env python
# coding: utf-8

import sys
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2

if __name__ == '__main__':
	if len(sys.argv) < 3:
		raise RuntimeError('too few args')

	# Register streaming http handlers to urllib2 global object
	register_openers()

	with open(sys.argv[2], "rb") as f:
		# Start the multipart/form-data encoding of the file
		# @headers: necessary Content-Type and Content-Length
		# @datagen: generator yielding the encoded parameters
		datagen, headers = multipart_encode({"file": f})

		request = urllib2.Request(sys.argv[1], datagen, headers)
		response = urllib2.urlopen(request)
		print "---------- RESPONSE HEAD ----------"
		print response.info()
		print "---------- RESPONSE BODY ----------"
		print response.read()
