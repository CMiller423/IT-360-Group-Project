# IT-360-Group-Project
Project Overview:
IT Forensics Collection Tool by Ed Mitchell and Carson Miller.
The goal of our project was to create a tool that will help a forensic investigator understand what is running on a system, as well as network connections to look for suspicious traffic. This tool can be used by regular users as well however all of the information it collects may not be usefull outside of a foresics investigation. A regular user may want this tool to get a quick overview of eveyrthing running on their system. Our tool collects general system information. Running processes with process id's and the location of those processes. Running services with hashes to check to see if they are legitimate. Driver Information. Login History. Browsing History / Artifacts. Active Network Connections, Routing Table, ARP Table, DNS Information, and Listening Ports (Needs to be ran as Admin)

Setup:
1. Python needs to be installed on your computer, any version above python 3 should work. You can check your version by running python --version in the command prompt
1a. If that command didnt work but you have python installed go into settings and find "Manage app execution aliases" Disable the two App Installers for python.exe and python3.exe. This should fix the problem.
2. Download the project files and place into a folder, for example /forensics-tool
3. Open the command prompt in that folder you can do this by clicking the top bar and typing cmd. Optionally you can type cmd in to the windows search box then run cd \Desktop\YourFolderName You will need to do it this way to run it as Administrator for the full report.
3a. This is assumming that you put the files into a folder on your desktop
4. run the gui by typing python win_fornensic_gui.py
5. Click run collection. This will run win_forensic_collect.py (It may take a few minutes to collect all of the information)
6. Once it is complete click load report, This will open a new window inside of your documents foler, you will need to navigate to the folder where the python files are and you will notice a new folder in there called forensics_collection_timestamp. Open that folder and click report.txt.
7. You can now review the report it generated inside of this gui or view it in its raw form by opening the text file.
8. This tool will also generate files of your history as well that it uses to parse into the report.
