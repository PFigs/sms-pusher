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
        api_key (str) : Nexmo's Wirepas API KEY
        api_secret (str) : Nexmo's Wirepas API secret
        clients ([]) : list of clients
        sender (str) : Sender's name

    """
    def __init__(self, sender, api_key, api_secret):
        super(Notify, self).__init__()
        self.nexmo = nexmo.Client(key=api_key, secret=api_secret)
        self.api_key = api_key
        self.api_secret = api_secret
        self.sender = sender

        self.clients = list()
        self.responses = list()


    def push_sms(self, content):
        """ 
        Pushes sms to contact list

        Args:
            content (str) : SMS content

        """
        
        if not self.clients:
            return

        self.responses = list()

        for client in self.clients:
            response = self.nexmo.send_message({'from': self.sender,
                                            'to': '+{0}'.format(client.phone), 
                                            'text': content})
            self.responses.append(response)


    def build_release_content(self, cfg):
        """
        Builds an sms based on the contents of the .ini file

        Args:
            cfg (obj) :  configparser object
        
        """
        return 'Your password for {0} is {1}'.format(cfg.get('SMS','TITLE'),
                                                   cfg.get('SMS','BODY'))



    def build_simple_sms(self, cfg):
        """
        Builds an sms based on the contents of the .ini file

        Args:
            cfg (obj) :  configparser object
        
        """
        return '{0} : {1}'.format(cfg.get('SMS','TITLE'),
                                cfg.get('SMS','BODY'))

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
            self.clients.append(Client(row['Name'], 
                                       row['Surname'], 
                                       row['Phone']))
        

    def print_response(self):
        """ 
        Print Responses

        Informs the user about what happened with the 
        latest messages that where sent

        """
        for response in self.responses:
            response = response['messages'][0]
            print(response)
            

class Client(object):
    """Creates a client object for each contact
    
        Attributes:
        firstname (str) : Contact's firstname
        surname (str) : Contact's surname
        phone (str): Contact's phonenumber

    """
    def __init__(self, firstname, surname, phone):
        super(Client, self).__init__()
        self.firstname =  firstname
        self.surname = surname
        self.phone = phone

    def __str__(self):
        return ('{0} {1} +{2}'.format(self.firstname, 
                                      self.surname, 
                                      self.phone))

    def __repr__(self):
        return self.__str__()


def user_inputs():

    parser = argparse.ArgumentParser()
    parser.add_argument('--configFile', default='details.ini', type=str)
    args = parser.parse_args()
    
    return args


if __name__ == "__main__":

    # parse user input
    args = user_inputs()

    # reads necessary details
    config = configparser.ConfigParser()
    config.read(args.configFile)

    notify = Notify(sender=config.get('SMS','SENDER'), 
                    api_key=config.get('NEXMO','API_KEY'), 
                    api_secret=config.get('NEXMO','API_SECRET'))
    notify.parser(config.get('SMS','DESTINATION'))

    notify.push_sms(notify.build_release_content(config))
    notify.print_response()