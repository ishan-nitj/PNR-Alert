from twilio.rest import TwilioRestClient
from urllib2 import urlopen
import json
import time

#data for authorization for twilio
account_sid = "############"
auth_token = "########"
my_no="###########"#your phone no

#data for authorization for rail api
mykey="#########" #api key for railway api #100 requests per day

#sends the message=content to your phone
def sendmsg(content):
	try:	
	    client = TwilioRestClient(account_sid, auth_token)
	    message = client.messages.create(to=my_no, from_="+12064296289",body=content)
	except Exception as e:
		print "Sorry could not send message due to %s"%((type(e).__name__))

#returns json data for a particular pnr no
def getdata(pnrno):
    url="http://api.railwayapi.com/pnr_status/pnr/"+str(pnrno)+"/apikey/"+mykey+"/"
    response = urlopen(url).read().decode('utf8')
    obj = json.loads(response)
    return obj
    
#processes json data #here interval is the period  in seconds after which you want to check pnr status again
def process(pnrno,interval):
	try:
		data=getdata(pnrno)
		if (len(str(pnrno))!=10):
			print "Enter a valid 10 Digit PNR no"		
		elif data["response_code"]!=200:#There's something wrong
			if data["response_code"]==204:
				print "Empty response. Not able to fetch required data."
			elif data["response_code"]==401:
				print "Authentication Error. You passed an unknown API Key."
			elif data["response_code"]==403:
				print "Quota for the day exhausted. Applicable only for FREE users."
			elif data["response_code"]==405:
				print "Account Expired. Renewal was not completed on time."
			elif data["response_code"]==410:
				print "Flushed PNR / PNR not yet generated"			
			elif data["response_code"]==404:
				print "Service Down / Source not responding"
		else:
			i=1
			totalpassengers=data["total_passengers"]
			pstatus={} #stores present status of each passenger
			print "Current status at time "+str(time.ctime(time.time()))
			for passenger in data["passengers"]:#passenger is a dictionary
				pstatus[i]=passenger["current_status"]
				print "Passenger %s %s"%(i,pstatus[i])
				i+=1
			print "\n"
			#Check after period of one interval 
			while 1:
				cstatus={} #stores current status
				time.sleep(interval)
				data=getdata(pnrno)
				i=1
				for passenger in data["passengers"]:#passenger is a dictionary
					cstatus[i]=passenger["current_status"]
					i+=1	
				#checks whether current status is same after one inteval
				content=""
				for i in range(1,totalpassengers+1):
					if cstatus[i]!=pstatus[i]:
						content+="PNR status changed for passenger %s from %s to %s.\n"%(i,pstatus[i],cstatus[i])
				print "Checking status at "+(str(time.ctime(time.time())))
				time.sleep(2)			
				if len(content)==0:
					print "Sorry no change"
				else:
					print content
					sendmsg(content)
				print "\n"
	except:
		print "Sorry something went wrong.Retrying after 30 seconds....Please check your internet connection."
		time.sleep(30)
		process(pnrno,interval)			
								
pnrno=int(raw_input("Enter your pnr no\n"))#Ex:2648518850
process(pnrno,300)#Checks after interval of 5 minutes(300 s)				
				
			
			
