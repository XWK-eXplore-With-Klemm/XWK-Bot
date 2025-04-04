This esp micropython robot project is now publicly hosted on github. Let's work on a KISS OTA.

How about a bash script that creates a list of all files in micropython/

Then save this list in the repo.

Next we add a button in the @index.html sidebar-footer "UPDATE". This uses the built in @microWebSrv.py .

It then calls a function which 
- gets the file list from github
- checks for newer files with different size (is there a file date in micropython?, if not possible update all) and update them
- reboot

what do you think about it? any better ideas? don't write code yet