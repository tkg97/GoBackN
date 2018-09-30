# GoBackN

To run the code, just extract the code to some folder. Folder will contain host1.py, host2.py which are code files for the two host emulators. There are also frame.py and myqueue.py which provide supporting classes for data frames, ack frames, and queue data structure.
There are some txt and log files which is the observed data by changing certain parameters of the code. Names of these files are self explanatory to some extent for the parameters used. By default, all files use window size of 7 and time window of 1000ms.

Open two terminals (python 3 should be installed) and run "python host1.py" and "python host2.py" on the terminals respectively.

It doesn't require any additional dependencies.

Your firewall might ask for permission for this network interaction between two hosts, please allow any permission popup.

All the variables are declared on top for both of the code files, you may change those as per your convenience.