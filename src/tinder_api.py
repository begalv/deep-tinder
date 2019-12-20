import re
import robobrowser
import requests
import json
from person import Person
from config import CONFIG



username = CONFIG['fb_login']['username']
password = CONFIG['fb_login']['password']

TINDER_URL = "https://api.gotinder.com"

class Tinder_API():

    def __init__(self, fb_email, fb_passwd):
        self.__fb_email = fb_email
        self.__fb_passwd = fb_passwd
        self.__token = self.__login()



    def __get_fb_acess(self):
        agent = "Tinder/7.5.3 (iPhone; iOS 10.3.2; Scale/2.00)"
        fb_auth_url = "https://www.facebook.com/v2.6/dialog/oauth?redirect_uri=fb464891386855067%3A%2F%2Fauthorize%2F&display=touch&state=%7B%22challenge%22%3A%22IUUkEUqIGud332lfu%252BMJhxL4Wlc%253D%22%2C%220_auth_logger_id%22%3A%2230F06532-A1B9-4B10-BB28-B29956C71AB1%22%2C%22com.facebook.sdk_client_state%22%3Atrue%2C%223_method%22%3A%22sfvc_auth%22%7D&scope=user_birthday%2Cuser_photos%2Cuser_education_history%2Cemail%2Cuser_relationship_details%2Cuser_friends%2Cuser_work_history%2Cuser_likes&response_type=token%2Csigned_request&default_audience=friends&return_scopes=true&auth_type=rerequest&client_id=464891386855067&ret=login&sdk=ios&logger_id=30F06532-A1B9-4B10-BB28-B29956C71AB1&ext=1470840777&hash=AeZqkIcf-NEW6vBd"

        browser = robobrowser.RoboBrowser(user_agent=agent, parser="lxml")
        browser.open(fb_auth_url)
        login_form = browser.get_form()
        login_form["email"].value = self.__fb_email
        login_form["pass"].value = self.__fb_passwd
        browser.submit_form(login_form)
        login_form = browser.get_form()
        try:
            browser.submit_form(login_form, submit=login_form.submit_fields['__CONFIRM__'])
            access_token = re.search(r"access_token=([\w\d]+)", browser.response.content.decode()).groups()[0]
            print("access_token")
            return access_token
        except requests.exceptions.InvalidSchema as browserAddress:
            access_token = re.search(r"access_token=([\w\d]+)", str(browserAddress)).groups()[0]
            return access_token
        except Exception as e:
            msg = "Facebook access token could not be retrieved. Check your email and password."
            print(msg)
            error_data = {
                "message": msg,
                "error": e
                }
            return error_data



    def __login(self):
        fb_token = self.__get_fb_acess()
        tinder_auth_url = TINDER_URL + '/v2/auth/login/facebook'
        fb_data = {"token": fb_token}

        try:
            req = requests.post(tinder_auth_url, headers = {'app_version': '6.9.4','platform': 'ios',"content-type": "application/json","User-agent": "Tinder/7.5.3 (iPhone; iOS 10.3.2; Scale/2.00)","Accept": "application/json"},
            json = fb_data)
            res = req.json()
            token = res['data']['api_token']
            print("Login was a success.")
            return token
        except Exception as e:
            msg = "We could not log you in."
            print(msg)
            error_data = {
                "message": msg,
                "error": e
            }
            return error_data



    def scan_people(self):
        url = TINDER_URL + "/v2/recs/core"
        people = []
        try:
            scan_data = requests.get(url, headers = {"X-Auth-Token": self.__token}).json()["data"]
            for person_data in scan_data['results']:
                person_data['user'].update({"distance_mi":person_data["distance_mi"]})
                people.append(Person(person_data['user']))
            return people
        except Exception as e:
            msg = "Something went wrong. Could not scan for people."
            print("{}\nError: {}".format(msg, e))
            error_data = {
                "message": msg,
                "error": e
            }
            return error_data



    def get_person(self, person_id):
        url = TINDER_URL + "/user/" + person_id
        try:
            person_data = requests.get(url, headers = {"X-Auth-Token": self.__token}).json()["results"]
            return Person(person_data)
        except Exception as e:
            msg = "Something went wrong. Could not get person's data."
            print("{}\nError: {}".format(msg, e))
            error_data = {
                "message": msg,
                "error": e
            }
            return error_data


    def like(self, person):
        url = TINDER_URL + "/like/" + person.get_id()
        try:
            response = requests.get(url, headers = {"X-Auth-Token": self.__token}).json()
            like_data = {
                "is_match": response["match"],
                "remaining": response["likes_remaining"]
                }
            print("Liked: {}".format(person))
            return like_data
        except Exception as e:
            msg = "Something went wrong. Could not like."
            print("{}\nError: {}".format(msg, e))
            error_data = {
                "message": msg,
                "error": e
            }
            return error_data



    def super_like(self, person):
        url = TINDER_URL  + "/like/{}/super".format(person.get_id())
        try:
            response = requests.post(url, headers = {"X-Auth-Token": self.__token}).json()
            super_like_data = {
                "is_match": response["match"],
                "remaining": response["super_likes"]["remaining"]
            }
            print("Super liked: {}".format(person))
            return super_like_data
        except Exception as e:
            msg = "Something went wrong. Could not super like."
            print("{}\nError: {}".format(msg, e))
            error_data = {
                "message": msg,
                "error": e
            }
            return error_data



    def dislike(self, person):
        url = TINDER_URL + "/pass/" + person.get_id()
        try:
            response = requests.get(url, headers = {"X-Auth-Token": self.__token}).json()
            print("Disliked: {}".format(person))
            return True
        except Exception as e:
            msg = "Something went wrong. Could not dislike."
            print("{}\nError: {}".format(msg, e))
            error_data = {
                "message": msg,
                "error": e
            }
            return error_data





api = Tinder_API(username, password)
person = api.get_person('53e246d714084a6e7949ff96')
