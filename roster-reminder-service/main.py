;
import sheets as sh
import email as em
import datetime

#get last modified date, a datetime.date object
last_modified_date_db = db.get_last_modified_date()
last_modified_date_sh = sh.get_last_modified_date()

if last_modified_date_db != last_modified_date_sh :
    db.wipe_roster()
    duties = sh.get_duties() #list of something
    for duty in duties:
        db.insert_duty(duty['date'], duty['duty'], duty['name'])

#send out emails
db.get_notifications()

for note in notifications:
    em.send_email(note['email_address'], \
                  note['name'],\
                  note['duty'],\
                  note['date'])
