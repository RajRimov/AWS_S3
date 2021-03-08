import os
import logging
import datetime as dt
import time
# import keyboard
# Getting the current work directory (cwd)
thisdir = os.getcwd()

LOG_FILE = os.getcwd() + "/logs"
IMAGE_FOLDER = os.getcwd()+ "/Image"
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)
if not os.path.exists(LOG_FILE):
    os.makedirs(LOG_FILE)
LOG_FILE = LOG_FILE + "/" + dt.datetime.fromtimestamp(time.time()).strftime('%Y_%m_%d %H_%M_%S') + ".log"
# Format: Info 2020:2020-11-04 21:55:45,351 
#         File Counts: 10
logFormatter = logging.Formatter("%(levelname)s %(asctime)s %(message)s")
fileHandler = logging.FileHandler("{0}".format(LOG_FILE))
fileHandler.setFormatter(logFormatter)
rootLogger = logging.getLogger()
rootLogger.addHandler(fileHandler)
rootLogger.setLevel(logging.INFO)

# File Exist Flag
# Exist_Flag = True 
# r=root, d=directories, f = files
while True:
    # if keyboard.is_pressed('q'):  # if key 'q' is pressed 
    #     print('You Pressed A Key!')
    #     break  # finishing the loop
    for r, d, f in os.walk(thisdir):
        count = 0 
        for file in f:
            file_name, file_extension = os.path.splitext(file)
            #filter files 
            if file_extension.lower() == ".jpg":
                count += 1
                print(os.path.join(r, file))
                # remove the file
                os.remove(os.path.join(r, file))
        if count != 0:
            logging.info("\nFile Counts: {0}".format(count))
            # Exist_Flag = False
            # break

            
