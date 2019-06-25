#Import modules
import requests
import time
import datetime
import json
import os
from dotenv import load_dotenv

'''''''''''''''''''''''''''''''''''''''''''''
                SETTINGS
'''''''''''''''''''''''''''''''''''''''''''''
#API account info
load_dotenv()
emailAddress = 'yjcarol@126.co'
apiKey = os.getenv("apiKey")
apiUrl = os.getenv("apiUrl")
mailGun_apiKey = os.getenv("mailGun_apiKey")
mailGun_domain_Name = os.getenv("mailGun_domain_Name")
emailAddress = os.getenv("emailAddress")


#Unit control, please typr "F" or "C"
unit = 'F'
#Set a location
location = {'latitude':38.89511, 
            'longitude':-77.03637
           }

#Define weather fetching methods, no time control, json data will be returned.
def weather_request (latitude, longitude):
    #Unit control
    if (unit == 'F'):
        unitURL = '?units=us'
    else:
        unitURL = '?units=si'

    url = apiUrl+apiKey+'/'+str(latitude)+','+str(longitude)+unitURL
    response = requests.get(url)
    return response.json()

#Define the weather fetching method with a time control, json data will be returned.
def weather_time_request (latitude, longitude, time): 
    #Unit control
    if (unit == 'F'):
        unitURL = '?units=us'
    else:
        unitURL = '?units=si'
        
    url = apiUrl+apiKey+'/'+str(latitude)+','+str(longitude)+unitURL
    response = requests.get(url)
    return response.json()

#Feeling judgement
def feel (temp):
    temp = float(temp)
    if (unit == 'F'):
        if (temp>=86):
            message = 'hot'
        elif (temp >= 64.4 and temp < 86):
            message = 'warm'
        else:
            message = 'cold'
    elif (unit == 'C'):
        if (temp >= 30):
            message = 'hot'
        elif (temp >= 18 and temp <30):
            message = 'warm'
        else:
            message = 'cold'
    else:
        message = "UNIT ERROR."
    return message

def rain (rainChance):
    rainChance = float(rainChance)
    if (rainChance >= 0.5):
        message = 'Please bring your umbrella!'
    elif (rainChance <0.5):
        message = 'No worries about raining today.'
    return message

def timeStamp (t, timeType):
    if (timeType == 'date') :
        return time.strftime('%A, %b %d, %Y',time.localtime(t))
    elif (timeType) == 'time' :
        return time.strftime('%H:%M:%S',time.localtime(t)) 
    elif (timeType) == 'sec':
        t = eval(t)
        #for filling h,m,s parts
        t += (0,0,0,0,0,0)
        return time.mktime(t)
    
#Welcome
print('\n\n\n' + 'LOADING...'.center(60) + '\n\n\n')

#Fetch data from the server
weather = weather_request (location['latitude'], location['longitude'])

currentTemperature = weather['currently']['temperature']
summary = weather['currently']['summary'].lower()
high_Temp = weather['daily']['data'][0]['temperatureHigh']
low_Temp = weather['daily']['data'][0]['temperatureLow']
tempFelling = feel(high_Temp)
rainChance = rain(weather['daily']['data'][0]['precipProbability'])

times = time.strftime("%I%p %b %d, %Y", time.localtime())
#Generate a result

result = times.center(60, '-')
result += '\n' + 'FORECAST'.center(60, '-')
result += '\n' + 'The current tempreture is ' + str(currentTemperature) + unit + ', '
result += summary + ', feeling ' + tempFelling + '.'
result += '\nThe high tempreture is ' + str(high_Temp) + unit + ', the low tempreture is ' + str(low_Temp) + unit + '.'
result += '\n' + rainChance

print(result)
print('\n\n\n' + 'Please wait, the forecast email is being sending to ' + emailAddress + '.')

#Mail via MailGun
mailSubject = time.strftime('%I%p', time.localtime()) + ' Weather forecast: ' + time.strftime('%B %d, %Y', time.localtime()) + '.'
response = requests.post(
        'https://api.mailgun.net/v3/' + str(mailGun_domain_Name) + '/messages',
        auth=('api', mailGun_apiKey),
        data={'from': 'Yang Jing <mailgun@' + str(mailGun_domain_Name) + '>',
              'to': [emailAddress],
              'subject': mailSubject,
              'text': result})
#Read response
data = json.loads(response.text)

if (data['message'] == 'Queued. Thank you.'):
    print('\n' + 'SUCCESS!'.center(60, '-') + '\nThe mail has been sent to ' + emailAddress + ' successfully!')
else:
    print('\n' + 'EMAIL SENT FAILED'.center(60, '-') + '\n' + data['message'])