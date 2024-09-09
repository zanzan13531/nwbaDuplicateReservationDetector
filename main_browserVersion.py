import json
# import requests
from webbot import Browser

zCalendarPage = "https://northwestbadmintonacademy.sites.zenplanner.com/calendar.cfm"
zLoginPage = "https://northwestbadmintonacademy.sites.zenplanner.com/login.cfm"
zTestPage = "https://northwestbadmintonacademy.sites.zenplanner.com/calendar.cfm?DATE=2022%2D08%2D07&VIEW=LIST"
zUserProfilePage = "https://northwestbadmintonacademy.sites.zenplanner.com/person.cfm"
zFamilyPage = "https://northwestbadmintonacademy.sites.zenplanner.com/family.cfm"

urlDate = "?DATE="
urlEnd = "&VIEW=LIST"
urlCalendar = "&calendarType="
urlCalendarPerson = "&calendarType=PERSON:"
urlPerson = "&personId="

# def getUserEndlink(name, browser):

#     link = ""
#     browser.go_to(zFamilyPage)

#     if (browser.exists(name)):
#         browser.click(name)
#         link = browser.get_current_url()
#         return(link[link.index("=") + 1:])

#     else:
#         print("Family member not found: " + name + ".")


username = ""
password = ""

with open("login.json", "r") as f:
    data = json.load(f)
    username = data["username"]
    password = data["password"]

web = Browser()

print("Navigating to zenplanner.")

web.go_to(zCalendarPage)
web.go_to(zLoginPage)


if (web.exists("Log In")):
    print("Not logged in, logging in...")
    web.go_to(zLoginPage)
    web.type(username , into='username', id='idUsername')
    web.type(password , into='Password' , id='idPassword')
    web.click('Log In' , tag='input')

if (web.exists("My Profile")):
    print("Successfully logged in.")

else:
    print("An error occurred.")
    quit()


# https://northwestbadmintonacademy.sites.zenplanner.com/calendar.cfm?date=2024-09-08&calendarType=

weekdayReservations = {}
weekendReservations = {}

calendarLink = zCalendarPage + urlDate + "2024-09-08" + urlCalendar

web.go_to(calendarLink)

# for times in weekdays:

#     if (web.exists(time)):
#         web.click(time)

#         for users:
#             if (user not in weekdayReservations):
#                 weekdayReservations[user] = [time]
#             else:
#                 weekdayReservations[user].append(time)

# for times in weekends:

#     if (web.exists(time)):
#         web.click(time)

#         for users:
#             if (user not in weekendReservations):
#                 weekendReservations[user] = [time]
#             else:
#                 weekendReservations[user].append(time)

# for user in weekdayReservations:
#     if (len(weekdayReservations[user]) > 2 || reservationsOnSameDay(weekdayReservations[user])):
#         print(user + " has reservations at: ")
#         print(weekdayReservations[user])

# for user in weekendReservations:
#     if (len(weekendReservations[user]) > 2 || reservationsOnSameDay(weekendReservations[user])):
#         print(user + " has reservations at: ")
#         print(weekendReservations[user])



web.quit()