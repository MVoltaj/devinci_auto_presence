# devinci_auto_presence
A little program to automatically check presence for you

*How it works*

- Program logs in into your account on devinci portail website
- If there is a presence it will check it, and wait until your next class
- If presence is closed, it will wait until your next class
- if presence is not opened, it will check every x seconds (delay you define) if it got opened, and when it opens, it checks it

Requirements:

¨- Python 3

Library :
- requests
- datetime
- time
- bs4
- pause
- colorama
- json

To install them, run in your cmd : pip install requests, pip install datetime, etc...

You need to input in the data.json file your credentials.
- Login
- Password
- Delay ( in seconds)

To run it, go to the directory where you downloaded it, open cmd and type "python main.py".
If it doesn"t work, you might try python3 main.py

You can also download the .exe here : https://drive.google.com/file/d/1anKjZO21YgjW1pUlBuSRC2Bi1FeHs3ej/view?usp=sharing

This will auto check your presence

An optimized V2 version will come soon, including a better flow, better handling and cleaner code.


If you find any bugs or have any questions, you can contact me at MVoltaj#6005

I'm not responsible of any abusal uses of this software
