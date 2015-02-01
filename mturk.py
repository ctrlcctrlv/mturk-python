#!/usr/bin/env python2
import time
import hmac
import hashlib
import base64
import json
import requests
import logging
import xmltodict
import collections
from datetime import datetime

#Convenient flags for qualification types.
P_SUBMITTED = "00000000000000000000"
P_ABANDONED = "00000000000000000070"
P_RETURNED = "000000000000000000E0"
P_APPROVED = "000000000000000000L0"
P_REJECTED = "000000000000000000S0"
N_APPROVED = "00000000000000000040"
LOCALE = "00000000000000000071"
ADULT = "00000000000000000060"
S_MASTERS = "2ARFPLSP75KLA8M8DH1HTEQVJT3SY6"
MASTERS = "2F1QJWKUDD8XADTFD2Q0G6UTO95ALH"
S_CATMASTERS = "2F1KVCNHMVHV8E9PBUB2A4J79LU20F"
CATMASTERS = "2NDP2L92HECWY8NS8H3CK0CP5L9GHO"
S_PHOTOMASTERS = "2TGBB6BFMFFOM08IBMAFGGESC1UWJX"
PHOTOMASTERS = "21VZU98JHSTLZ5BPP4A9NOBJEK3DPG"

class MechanicalTurk(object):
	def __init__(self,mturk_config_dict=None):
		"""Try to set config variables with a file called 'mturkconfig.json' if no argument is passed to the class instance. Else get our config from the argument passed."""
		if mturk_config_dict is None:
			mturk_config_dict = json.load(open("mturkconfig.json"))
		if not mturk_config_dict.get("stdout_log"):
			logging.getLogger('requests').setLevel(logging.WARNING)

		self.sandbox = mturk_config_dict.get("use_sandbox") == True # Use sandbox?
		self.verify_mturk_ssl = mturk_config_dict.get("verify_mturk_ssl") == True
		self.aws_key = mturk_config_dict["aws_key"]
		self.aws_secret_key = str(mturk_config_dict["aws_secret_key"])

	def _generate_timestamp(self, gmtime):
		return time.strftime("%Y-%m-%dT%H:%M:%SZ", gmtime)

	def _generate_signature(self, operation, timestamp, secret_access_key):
		my_sha_hmac = hmac.new(secret_access_key, 'AWSMechanicalTurkRequester' + operation + timestamp, hashlib.sha1)
		my_b64_hmac_digest = base64.encodestring(my_sha_hmac.digest()).strip()
		return my_b64_hmac_digest

	def _flatten(self, obj, inner=False):
		if isinstance(obj, collections.Mapping):
			if inner: obj.update({'':''})
			iterable = obj.items()
		elif isinstance(obj, collections.Iterable) and not isinstance(obj, basestring):
			iterable = enumerate(obj, start=1)
		else:  
			return {"": obj}

		rv = {}
		for key, value in iterable:
			for inner_key, inner_value in self._flatten(value, inner=True).items():
				if inner_value != '':
					rv.update({("{}.{}" if inner_key else "{}{}").format(key, inner_key): inner_value})
		return rv

	def request(self, operation, request_parameters={}):
		"""Create a Mechanical Turk client request. Unlike other libraries (thankfully), my help ends here. You can pass the operation (view the list here: http://docs.amazonwebservices.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_OperationsArticle.html) as parameter one, and a dictionary of arguments as parameter two. To send multiple of the same argument (for instance, multiple workers to notify in NotifyWorkers), you can send a list."""
		self.operation = operation

		if self.sandbox:
			self.service_url='https://mechanicalturk.sandbox.amazonaws.com/?Service=AWSMechanicalTurkRequester'
		else:
			self.service_url='https://mechanicalturk.amazonaws.com/?Service=AWSMechanicalTurkRequester'
		# create the operation signature
		timestamp = self._generate_timestamp(time.gmtime())
		signature = self._generate_signature(operation, timestamp, self.aws_secret_key)

		# Add common parameters to request dict
		request_parameters.update({"Operation":operation,"Version":"2014-08-15","AWSAccessKeyId":self.aws_key,"Signature":signature,"Timestamp":timestamp})

		self.flattened_parameters = self._flatten(request_parameters)

		request = requests.post(self.service_url, data=self.flattened_parameters, verify=self.verify_mturk_ssl)
		request.encoding = 'utf-8'
		xml = request.text # Store XML response, might need it
		response = xmltodict.parse(xml.encode('utf-8'), dict_constructor=dict)
		return MechanicalTurkResponse(response, xml=xml)
	
	def externalFormAction(self):
		"""Return URL to use in the External question and HTML question form submit action."""
		if self.sandbox:
			return 'https://workersandbox.mturk.com/mturk/externalSubmit'
		else:
			return 'https://www.mturk.com/mturk/externalSubmit'

class MechanicalTurkResponse(dict):
	def __init__(self, response, xml=None):
		dict.__init__(self, response)
		self.response = response
		self.xml = xml
		req = self.get_response_element("Request")
		self.valid = req.get("IsValid") == "True" if req else False

	def _find_item(self, obj, key):
		if key in obj: return obj[key]
		for k, v in obj.items():
			if isinstance(v, dict):
				item = self._find_item(v, key)
				if item is not None:
					return item

	def get_response_element(self, element):
		return self._find_item(self.response, element)	
