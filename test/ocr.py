#!/usr/bin/env python
# coding: utf-8

import os, sys
import itertools
import mimetools
import mimetypes
from cStringIO import StringIO
import urllib
import urllib2

class MultiPartForm(object):
	def __init__(self):
		self.form_fields = []
		self.files = []
		self.boundary = mimetools.choose_boundary()
		return

	def get_content_type(self):
		return 'multipart/form-data; boundary=%s' % self.boundary

	def add_field(self, name, value):
		"""Add a simple field to the form data."""
		self.form_fields.append((name, value))

	def add_file(self, fieldname, filename, fileHandle="", mimetype=None):
		"""Add a file to be uploaded."""
		body = fileHandle.read() if fileHandle != "" else ""
		if mimetype is None:
			mimetype = mimetypes.guess_type(filename)[0]
		self.files.append((fieldname, filename, mimetype, body))
		return

	def __str__(self):
		"""Return a string representing the form data, including attached files."""
		parts = []
		part_boundary = '--' + self.boundary

		parts.extend(
				[ part_boundary,
					'Content-Disposition: form-data; name="%s"' % name,
					'',
					value,
				] for name, value in self.form_fields)

		parts.extend(
				[ part_boundary,
					'Content-Disposition: file; name="%s"; filename="%s"' % (field_name, filename),
					'Content-Type: %s' % content_type,
					'',
					body,
				] for field_name, filename, content_type, body in self.files)

		flattened = list(itertools.chain(*parts))
		flattened.append('--' + self.boundary + '--')
		flattened.append('')
		return '\r\n'.join(flattened)

if __name__ == '__main__':
	if len(sys.argv) < 3:
		raise RuntimeError('too few args')

	url = sys.argv[1]
	fpath = sys.argv[2]

	with open(fpath, 'r+b') as f:
		form = MultiPartForm()
		form.add_file('file', fpath, f)
		request = urllib2.Request(url)
		request.add_header('Content-type', form.get_content_type())
		request.add_data(str(form))

		response = urllib2.urlopen(request)
		print "---------- RESPONSE HEAD ----------"
		print response.info()
		print "---------- RESPONSE BODY ----------"
		print response.read()
