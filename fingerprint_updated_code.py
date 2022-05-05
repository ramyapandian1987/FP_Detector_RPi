'''
This Fingerprint detector code verifies if the given fingerprint template already exists else it creates and stores as a new template.
This code also updates the log file after every fingerprint scan along with an email notification.
'''

import time
import smtplib
from datetime import datetime
from pyfingerprint.pyfingerprint import PyFingerprint

def sensorInit():
    ## Tries to initialize the sensor
    try:
        f = PyFingerprint('/dev/ttyS0', 57600, 0xFFFFFFFF, 0x00000000)
        print(f.verifyPassword())
        #f.clearDatabase()
        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')
        return f
    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        #exit(1)

if __name__ == "__main__":
    f = sensorInit()
    print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

    with open("Logs/logs_new.csv", 'a') as logs:
        logs.write('Template position number|Template characteristics|Accuracy score \n')
        
    while(True):
        
        ## Tries to enroll new finger
        try:
            print('Waiting for finger...')

            while ( f.readImage() == False ):
                pass
            print('Remove finger...')
            ## Converts read image to characteristics and stores it in charbuffer 1
            template = f.convertImage(0x01)
            #print (type(template))
            fp_characteristics = f.downloadCharacteristics()
            #print (fp_characteristics)
            print ('Checking if your fingerprint already exists...')
            
            ## Checks if finger is already enrolled
            result = f.searchTemplate()
            positionNumber = result[0]
            acc_score = result[1]

            if ( positionNumber >= 0 ):
                print('Template already exists at position #' + str(positionNumber))
                with open("Logs/logs_new.csv", 'a') as logs:
                    logs.write(str(positionNumber) + '|' + str(fp_characteristics) + '|' + str(acc_score) + "\n")
                pass
                #exit(0)
            else:
                time.sleep(2)
                print('Waiting for same finger again...')

                ## Wait that finger is read again
                while ( f.readImage() == False ):
                    pass

                ## Converts read image to characteristics and stores it in charbuffer 2
                f.convertImage(0x02)
                #f.downloadImage('FPImages/Image1.png')
                #new_image = f.downloadImage(0x02)
                #print(new_image)

                ## Compares the charbuffers
                fp_characteristics = f.downloadCharacteristics()
                print (fp_characteristics)
                #f.compareCharacteristics
                #print ('The accuracy score is : ' + int(f.compareCharacteristics))
                if ( f.compareCharacteristics() == 0 ):
                    raise Exception('Fingers do not match')

                ## Creates a template
                f.createTemplate()

                ## Saves template at new position number
                positionNumber = f.storeTemplate()
                print('Finger enrolled successfully!')
                print('New template position #' + str(positionNumber))

            gmail_user = '[Enter the sender mail id]'
            gmail_password = '[Enter the password]'

            position = positionNumber

            sent_from = gmail_user
            to = '[Enter the recipient mail id]'
            subject = 'Iot Research Fingerprint Scanner'
            body = 'Finger successfully scanned, position ' + str(position)

            email_text = """\
From: %s
To: %s
Subject: %s

%s
            """ % (sent_from, ", ".join(to), subject, body)
            #print(email_text)
            smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtp_server.ehlo()
            smtp_server.login(gmail_user, gmail_password)
            smtp_server.sendmail(sent_from, to, email_text)
            smtp_server.close()
            print ("Email sent successfully!")
            
        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
                #exit(1)

