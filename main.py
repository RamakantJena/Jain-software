"""
These are the required libraries
"""
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import schedule
import whois
from whois.parser import PywhoisError

def data_collection():
    """
    There is no contact/phone number attribute in WHOIS response
    that's why I didn't add any contact number column in the CSV file.
    :return:
    """

    # Enter any domain name here
    domain = None

    while True:

        print("Enter 'E' to stop entering domain. ")
        domain = str(input("Enter the domain name:> "))

        if domain == 'E' or not domain.__contains__("."):
            print("Successfully exit.")
            return

        response = None
        try:
            response = whois.whois(domain)
        except Exception as e:
            print(e)
            print(f"No match for: {domain}")
            return

        name = None
        domain_name = None
        mail_id = None
        createion_date = None
        try:
            print("Name: ", response.name)
            name = response.name
            if type(response.domain_name) == type([]):
                print("Domain name: ", response.domain_name[1])
                domain_name = response.domain_name[1]
            else:
                print("Domain name: ", response.domain_name)
                domain_name = response.domain_name

            print("Email: ", response.emails[1])
            mail_id = response.emails[1]

            for i in response.creation_date:
                print("Createion date: ", response.creation_date[0])
                createion_date = response.creation_date[0]
                break
        except Exception as e:
            print("Creation date: ", response.creation_date)
            createion_date = response.creation_date

        # print(response)

        if domain_name != None:
            data = {
                'Name': [name],
                'Domain_name': [domain_name],
                'Email': [mail_id],
                'Creation_date': [createion_date]
            }

            # Get the data from CSV file
            csv_data = pd.read_csv("Whoisdata.csv")

            # Check if data already existing or not. It prevents from data duplication.
            if not csv_data['Domain_name'].tolist().__contains__(domain_name):

                # Make data frame of above data
                df = pd.DataFrame(data)
                # append data frame to CSV file
                df.to_csv("Whoisdata.csv", mode="a", index=False, header=False)

                print("Data appended successfully.")
            else:
                print("Data already exist in the file.")
        else:
            print(domain + " is not a valid input \nEnter valid domain.")



# This method used to send mail to specified email.
def sendemail():
    """
    Email details mentioned bellow
    password => password should be app password generated by Google Otherwise, authentication error will occur.
    change the Email id password and receiver mail id to receive and send the data.
    :return:
    """
    sender = "ramakantaj27@gmail.com"
    password = "wkatfwiqtqysfrzh"
    receiver = "contact@sohiljain.com"
    file_name = "Whoisdata.csv"
    subject = "Updated list of newly registered WHOIS."
    body = "New updated data."

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # File attachment codes written bellow
    attchment = open(file_name, 'rb')
    attchment_list = MIMEBase('application', 'octet-stream')
    attchment_list.set_payload(attchment.read())
    encoders.encode_base64(attchment_list)
    attchment_list.add_header('Content_Disposition', 'attachment; filename= ' + file_name)
    msg.attach(attchment_list)

    text = msg.as_string()

    # Mail sending information written bellow.
    try:
        smtpObj = smtplib.SMTP("smtp.gmail.com", 587)
        smtpObj.starttls()
        smtpObj.login(sender, password)
        smtpObj.sendmail(sender, receiver, text)
        print("Successfully sent email")
    except Exception as e:
        print(e)
        print("Error: unable to send email")


"""
All function calls are done here.
"""
data_collection()


"""
This is the scheduler automatically invoked at specified time to send mail daily.
Once script is starts to run it will never stops because a endless loop is required to make scheduler active.
We have stop the script manually to stop the script.
"""
schedule.every().day.at("10:00").do(sendemail)
while True:
    schedule.run_pending()