import requests
import re
from datetime import date
from datetime import datetime
import time
from bs4 import BeautifulSoup
import pause
import json
from colorama import Fore

def show_courses(data):
    print("Your courses of today are")
    for i in range(0,len(data),3):
        print(data[i] + " " + data[i+1] + " " + data[i+2])
    print("")

def actual_time():
    return str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

def check_status(webpage):
    soupe_obj = BeautifulSoup(get_presence_page.text, 'html.parser')
    danger_status = soupe_obj.find_all("div", {"class": "alert alert-danger"})
    success_status = soupe_obj.find_all("div", {"class": "alert alert-success"})
    if len(success_status) != 0:
        success_text = success_status[0].get_text(strip=True)
    else:
        success_text = ""
    if len(danger_status) != 0:
        danger_text = danger_status[0].get_text(strip=True)
    else:
        danger_text = ""

    return success_text + " - " + danger_text

def clear_seance_info(seance_info):
    for i in range(len(seance_info)):
        if i % 3 == 0:
            info_seance[i] = seance_info[i].replace(" ", "")




f = open("data.json",mode="r")
credentials = json.load(f)
email = credentials["email"]
password = credentials["password"]
delay = int(credentials["delay"])

s = requests.session()
get_home = s.get(url="https://www.leonard-de-vinci.net/")
print(actual_time() + " - Got home")
login_url = "https://www.leonard-de-vinci.net/ajax.inc.php"
s.headers["content-type"] = "application/x-www-form-urlencoded; charset=UTF-8"

submit_email = s.post(url=login_url,data={"act":"ident_analyse","login":email})
if "location" in submit_email.text:
    portail_link = "https://www.leonard-de-vinci.net/lssop" + re.findall(r'lssop(.*?)"',submit_email.text)[0]
    print(actual_time() + " - Successfuly Submitted First Page")

get_portail = s.get(url=portail_link)
if "Entrez votre ID" in get_portail.text:
    print(actual_time() + " - Successfully Got Portail Page")
    login_post_url = "https://adfs.devinci.fr/adfs" +re.findall(r'action="/adfs(.*?)"',get_portail.text)[0]
login_information = {
    "UserName":email,
    "Password":password,
    "AuthMethod":"FormsAuthentication"
}

login_req = s.post(url=login_post_url,data=login_information)
if "SAMLResponse" in login_req.text:
    print(actual_time() + " - Got SAML response")
    saml_response = re.findall(r'"SAMLResponse" value="(.*?)"',login_req.text)[0]
    relaystate = re.findall(r'RelayState" value="(.*?)"',login_req.text)[0]



saml_post = s.post(url="https://www.leonard-de-vinci.net/include/SAML/module.php/saml/sp/saml2-acs.php/devinci-sp",data = {"SAMLResponse" : saml_response,"RelayState":relaystate})
if "Office 365" in saml_post.text:
    print(actual_time() + " - Successfully Logged in")

print(actual_time() + " - Accessing Presence \n")


#Showing Courses of the day

get_presence = s.get(url="https://www.leonard-de-vinci.net/student/presences/")
info_seance = re.findall(r'<td>(.*?)</td>',get_presence.text)




# Clearing Courses data

clear_seance_info(info_seance)
show_courses(info_seance)

#Starting monitoring

print(actual_time() + " - Starting Monitoring")

while True:
    get_presence = s.get(url="https://www.leonard-de-vinci.net/student/presences/")
    links_presence = re.findall(r'<td><a href="/student/presences/(.*?)"',get_presence.text)


    #Compteur is a random value, assigned to 50 just because you will never have 50 course in a day
    presence_order_in_html = 50


    test = re.findall(r'<tr class="(.*?)"',get_presence.text)
    for i in range(len(test)):
        #Checking if a presence is available to test, and assign it's order number to compteur
        if test[i] == "warning":
            presence_order_in_html = i


    presence_url = "https://www.leonard-de-vinci.net/student/presences/upload.php"

    if presence_order_in_html != 50: #If there is a presence in warning to check
        presence_id = links_presence[presence_order_in_html]
        try:
            time_next_class = re.findall(r'\d+\d+', info_seance[((presence_order_in_html + 1) * 3)])
            next_class_date = datetime(int(datetime.now().year), int(datetime.now().month), int(datetime.now().day),
                                       int(time_next_class[0]), int(time_next_class[1]), 0, 0)
            second_before_next_class = (next_class_date - datetime.now()).total_seconds()
        except IndexError:
            send_presence = s.post(url=presence_url, data={"act": "set_present", "seance_pk": presence_id})
            if "present" in send_presence.text:
                print(Fore.RED + (actual_time() + " - Successfully checked presence for : " + info_seance[
                    presence_order_in_html * 3] + " " + info_seance[presence_order_in_html * 3 + 1] + " " + info_seance[
                          presence_order_in_html * 3 + 2]))
            print("No more class after this one")
            break

        get_presence_page = s.get(url ="https://www.leonard-de-vinci.net/student/presences/" + presence_id)
        send_presence = s.post(url=presence_url, data={"act":"set_present","seance_pk":presence_id})

        #Getting seconds so we can sleep before next class

        if "present" in send_presence.text:
            print(Fore.GREEN +(actual_time() + " - Successfully checked presence for : " + info_seance[presence_order_in_html * 3] + " " + info_seance[presence_order_in_html * 3 + 1] + " " + info_seance[presence_order_in_html * 3 + 2]))

            print(actual_time() + " - Waiting until " + str(next_class_date.hour) +":" + str(next_class_date.minute))
            pause.until(next_class_date)
            #time.sleep(second_before_next_class)
        elif "Validation Impossible":

            print(Fore.RED + (actual_time() + " - Validation Impossible " + check_status(get_presence_page.text)))
            if "clôturé" in check_status(get_presence_page.text) or "noté présent" in check_status(get_presence_page.text):
                print(actual_time() + " - Waiting until " + str(next_class_date.hour) +":" + str(next_class_date.minute))
                pause.until(next_class_date)
                #time.sleep(second_before_next_class)

            else:
                time.sleep(delay)
    else:
        print(actual_time() + " - No Presence Activated - Waiting " + str(delay)+ " seconds")
        time.sleep(delay)












