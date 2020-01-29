---
layout: post
title: Use the tools linux gave You!
description: A post about 2 tools all linux distributions give you. This is handy for recording and extracting data.
tags:
 - Tools

---
So recently I have been undertaking some courses in order to increase the knowledge I have on Pen testing and hacking in general. One of the common themes is about adequate note taking in which they (the instructors) would go into demonstrations of different applications they use to accomplish this and it dawned on me... you are using linux why not just use the tools already installed?<br />
Now these applications...don't get me wrong, they are very good at cleaning up notes but none of them are automated. This to me can be inefficient and what happens if you forget a key command you ran, because you forgot to type it again in these note taking applications.<br />
Enter Script, makes a typescript of everything on your terminal session. The terminal data is stored in raw form to a log file and information about timing to another (optional) structured log file. To stop recording your terminal session you just type exit. <br />
Script if not given a filename will create a file in your current working directory called "transcript" but you can alternative give it a filename that is a bit better. for example  `script output.txt` and it can be just that simple. I would suggest checking out the man page for script located at [script manpage](http://man7.org/linux/man-pages/man1/script.1.html) or you can simply type man script in your terminal.<br />
So thats the first tool and it'll record your terminal session. Now we move onto the second and well it is better known...Grep! 

Enter Grep, it searches for patterns in each file.  Patterns are one or more patterns separated by newline characters, and grep prints each line that matches a pattern. I would suggest checking out the man page for grep located at [grep manpage](http://www.man7.org/linux/man-pages/man1/grep.1.html) or you can simply type man grep in your terminal. 

So our Script command gives an output file, we can then search that file using grep and now start separating out all our output into nicely filtered files. So say we use theHarvester application to gather information on a target...let's use Microsoft as our ~~victim~~...oh I mean target lol
<br />
We've enabled script by typing `script output.txt` 

We now run theHarvester `theHarvester -d microsoft.com -l 1000 -b all`

Now we let that run and all the command and the output that come from theHarvester and that are displayed on the screen are written to our output.txt file. Once our command has completed successfully we simply exit out of script by typing `exit` (please note you could keep script going and do other tasks like nmap scans, netcat banner grabbing, just remember to exit at the end).
<br />
Now this is where we get down to filtering out data, theHarvester collects a lot of OSINT data for us to use but it's all in one file...what if we wanted to strip out say just twitter handles or email addresses that it found, so that we can use it in other applications. If we just used the output.txt by itself most of our applications would error with other erroneous input that is in the txt file. 

So let's start with the Twitters by using grep we can strip out the twitter handles into another file. `grep -E -o "@[0-9a-zA-Z]+" < output.txt > twitterHandles.txt` 

This uses a regular expression to strip out a twitter handle like mine @SteveBartimote and then puts it into a text file called twitterHandles.txt... but all that file will contain is twitter usernames!
<br />
Now lets look at email addresses, using the same output.txt file and grep we will use a different regular expression to strip out emails. `grep -E -o “\b[a-zA-Z0-9.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9.-]+\b” < output.txt > emailAddresses.txt`

There you have it a text file called emailAddressess.txt containing all the email addresses theHarvester's output has... now you'll notice with starting theHarvester that it's developer's email address is also listed in our output.txt (usually the top entry) be sure to remove it from your file...wouldn't want to spam him.
<br /> you still keep the output.txt as the evidence of 1. the commands you ran and 2. the output you received in your engagement. However that recording of that is done for you with script.
<br />
With Grep really the only limitation is your knowledge of regular expressions. Definitely take the time to "try" and understand them...it's worth it!

Somethings to know/remember:
* Script only records the current session so you can feel free to open a second terminal session and it wont record it... now if you are like me 1 terminal window is not enough, look at the man page for script there is an --append option or in your second terminal create a different output file. For example I run nmap in a seperate window and create a second file called nmapOutput.txt which I then use grep to strip out all the IPs and services. But really learn these commands and use and abuse them

* Script only does terminal applications, anything in a GUI you'll need to configure that application to generate an output file.
