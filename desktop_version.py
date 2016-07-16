from urllib2 import urlopen
import json
import time
import pynotify
pynotify.init('my apps')

exceptioncount=0#Shows desktop notification when exception count exceeds 5(5,10,15 etc)

def shownotif(content):
	try:
		n=pynotify.Notification('Hi there!',content)
		n.show()
	except:
		"Sorry could not show notification.Trying again...."
		shownotif(content)

#data for authorization
mykey=" #######" #api key for railway api #100 requests per day

#returns json data for a particular pnr
def getdata(pnrno):
    url="http://api.railwayapi.com/pnr_status/pnr/"+str(pnrno)+"/apikey/"+mykey+"/"
    response = urlopen(url).read().decode('utf8')
    obj = json.loads(response)
    return obj
    
#processes json data #here interval is the period  in seconds after which you want to check pnr status again
def process(pnrno,interval):
	global exceptioncount
	try:
		data=getdata(pnrno)
		if (len(str(pnrno))!=10):
			print "Enter a valid 10 Digit PNR no"		
		elif data["response_code"]!=200:#Ther's something wrong
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
					shownotif(content)
				print "\n"
	except:
		print "Sorry something went wrong.Retrying after 30 seconds....Please check your internet connection."
		time.sleep(30)
		exceptioncount+=1
		if exceptioncount%5==0:
			shownotif("Something went wrong.Please check your internet connection")
		process(pnrno,interval)
											
pnrno=int(raw_input("Enter your pnr no\n"))
process(pnrno,300)#Checks after interval of 5 minutes(300 s)			
		
