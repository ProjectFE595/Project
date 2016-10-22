This is mongoDB backup (10/21/2016) for our project data. You can restore it in your mongo database so you needn't to download the data from quandl (which takes a lot of time)

Install MongoDB on your computer and run it on the standard port.

Download the folder "dump" and put it into your directory so that you are in the parent directory of the dump directory.

Now type:

mongorestore dump

You will restore the project data to your local mongo database.


Yun Chen

