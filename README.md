# sms-pusher
Reads contacts from a xlsx and pushes an sms to each of them using NEXMO's APIs.


# Defining SMS content
Content is defined inside a configuration file, by default details.ini 
which is expected to contain at least two sections NEXMO and SMS, such as

```
[NEXMO]
API_KEY = ...
API_SECRET = ...

[SMS]
TITLE = Main topic
BODY = Your voucher code is 12390
SENDER = SMS-PUSHER
```
