# Author
# Pedro Silva

import configparser
import argparse
import nexmo
import pandas

class Notify(object):
    """
    Notify contacts

    Allows for pushing sms information to a set of contatct people.
    It is capable of populating the list of clients by
    parsing the contents of an excel file

    Attributes:

        nexmo (obj) : provider's object
        api_key (str) : Nexmo's API KEY
        api_secret (str) : Nexmo's API secret
        sender (str) : Sender's name

        fromaddr (str) : email's sender
        smtp_pwd (str) : email's user password
        smtp_server (str) : smtp server location
        smtp_port (int) : smtp port

        clients ([]) : list of clients

    """
    def __init__(self, sender, api_key, api_secret,
                       fromaddr, smtp_pwd, smtp_server, smtp_port):
        super(Notify, self).__init__()
        self.nexmo = nexmo.Client(key=api_key, secret=api_secret)
        self.api_key = api_key
        self.api_secret = api_secret
        self.sender = sender


        self.fromaddr = fromaddr
        self.smtp_pwd = smtp_pwd
        self.smtp_server =smtp_server
        self.smtp_port = smtp_port

        self.clients = list()

    def push_sms(self, content):
        """
        Pushes sms to contact list

        Args:
            content (str) : SMS content

        """

        if not self.clients:
            return

        for client in self.clients:
            response = self.nexmo.send_message({'from': self.sender,
                                            'to': '{0}'.format(client.phone),
                                            'text': content})
            client.sms = response


    def build_release_content(self, title, body):
        """
        Builds an sms based on the contents of the .ini file

        Your password for TITLE is BODY

        Args:
            title (str) :  sms title
            body (str) :  sms body

        """
        return 'Your password for {0} is {1}'.format(title, body)



    def build_simple_sms(self, content):
        """
        Builds an sms based on the contents of the .ini file

        Args:
            content (str) :  sms content

        """
        return '{0}'.format(content)


    def send_email_confirmation(self,
            subject,
            in_success,
            in_error="We couldn't reach you by SMS, please get in touch with us!"):
        """
        Send confirmation email

        Loops through the SMS answers and sends out an email

        Args:
            subject (str) : email's subject
            in_success (str) : email's body if SMS status is OK
            in_error (str) : email's body if SMS status is NOK

        """

        import smtplib
        from email.message import EmailMessage

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.fromaddr

        # Send the message via a remote SMTP server
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.ehlo()
        server.starttls()
        server.login(self.fromaddr, self.smtp_pwd)

        if self.clients:
            for client in self.clients:
                if client.sms is None:
                    print('Skipping {0} @ {1}'.format(client.name,
                                                      client.email))
                    continue

                if client.sms['messages'][0]['status'] == 0:
                    body = in_success
                else:
                    body = in_error

                msg['To'] = client.email
                msg.set_content(body)

                server.send_message(msg)

        server.quit()


    def parser(self, filepath):
        """
        Parse xlsx

        Reads an excel list with the following format

        First Name | Surname | Phone

        Creates and stores an object representation for each client

        Args:
            filepath (str) : filepath for xls file


        """
        wb = pandas.read_excel(filepath)

        for idx, row in wb.iterrows():
            try:
                self.clients.append(Client(row['Name'],
                                       row['Surname'],
                                       row['Phone'],
                                       row['Email']))
            except:
                raise KeyError('Please check xlsx content')


    def print_response(self):
        """
        Print Responses

        Informs the user about what happened with the
        latest messages that where sent

        """
        for client in self.clients:
            response = client.sms['messages']
            print('{{{{"client", "{0}"}},"status":{1}}}'.format(client, response))


class Client(object):
    """Creates a client object for each contact

        Attributes:
        firstname (str) : Contact's firstname
        surname (str) : Contact's surname
        phone (str): Contact's phonenumber

    """
    def __init__(self, firstname, surname, phone, email=None):
        super(Client, self).__init__()
        self.firstname =  firstname
        self.surname = surname
        self.phone = phone
        self.email = email

    def __str__(self):
        return ('{0} {1} {2}'.format(self.firstname,
                                      self.surname,
                                      self.phone,
                                      self.email))

    def __repr__(self):
        return self.__str__()


def user_inputs():

    parser = argparse.ArgumentParser()
    parser.add_argument('--configuration', default='details.ini', type=str)
    parser.add_argument('--destination', default=None, type=str)
    args = parser.parse_args()

    return args


if __name__ == "__main__":

    # parse user input
    args = user_inputs()

    # reads necessary details
    config = configparser.ConfigParser()
    config.read(args.configuration)


    # validate fields
    try:
        sender = config.get('SMS','SENDER')
        api_key = config.get('NEXMO','API_KEY')
        api_secret = config.get('NEXMO','API_SECRET')
    except:
        raise KeyError('Missing NEXMO details')

    try:
        destination = config.get('SMS','DESTINATION')
    except:
        if args.destination is None:
            raise KeyError('Please enter a valid destination')

    try:
        sms_content = config.get('SMS','CONTENT')
    except:
        raise KeyError('Missing SMS content')

    try:
        fromaddr = config.get('EMAIL','SENDER')
        smtp_pwd = config.get('EMAIL','PASSWORD')
    except:
        raise KeyError('Missing EMAIL details (FROM and PASSWORD)')

    try:
        smtp_server = config.get('EMAIL','SMTP')
    except:
        smtp_server = 'smtp.office365.com'

    try:
        smtp_port = int(config.get('EMAIL','PORT'))
    except:
        smtp_port = 587

    # email confirmation details
    try:
        subject = config.get('SUBJECT')
    except:
        subject = 'Email notification'

    try:
        in_success=config.get('SUCCESS')
    except:
        in_success = 'We have sent you an SMS, please check your phone!'

    try:
        in_error=config.get('ERROR')
    except:
        in_error = 'We could not reach you by SMS, please get in touch with us!'

    # creates notifier object with NEXMO and MAIL details
    notify = Notify(sender=sender,
                    api_key=api_key,
                    api_secret=api_secret,
                    fromaddr=fromaddr,
                    smtp_pwd=smtp_pwd,
                    smtp_server=smtp_server,
                    smtp_port=smtp_port)

    # command line override sets only one client
    if args.destination is None:
        notify.parser(destination)
    else:
        notify.clients.append(Client('CMD', 'Line', args.destination))

    # send out notifications to clients
    notify.push_sms(notify.build_simple_sms(sms_content))
    notify.send_email_confirmation(subject, in_success, in_error)

    # for reference
    notify.print_response()