---
layout: post
title: Use the tools Linux gave You!
description: A post about 2 tools all linux distributions give you. This is handy for recording and extracting data.
tags:
 - Tools

---
So recently I have been undertaking some courses in order to increase the knowledge I have on Pent testing and hacking in general. One of the common themes is about adequate note taking in which they (the instructors) would go into demonstrations of different applications they use to accomplish this and it dawned on me... you are using linux why not just use the tools already installed?<br />
Now these applications...don't get me wrong, they are very good at cleaning up notes but none of them are automated. This to me can be inefficient and what happens if you forget a key command you ran, because you forgot to type it again in these note taking applications.<br />
Enter the linux tool "script" makes a typescript of everything on your terminal session. The terminal data is stored in raw form to a log file and information about timing to another (optional) structured log file. To stop recording your terminal session you just type exit. <br />
Script if not given a filename will create a file in your current working directory called "transcript" but you can alternative give it a filename that is a bit better. for example  `script output.txt` and it can be just that simple. I would suggest checking out the man page for script located at http://man7.org/linux/man-pages/man1/script.1.html or you can simply type man script in your terminal.<br />
So thats the first tool and it'll record your terminal session. Now we move onto the second and well it is better known...Grep! Because our Script command gives an output file we can then search that file using grep and start separating out all out output into nicely filtered files. So say we use theHarvester to gather information on a target...let's use Microsoft lol
<br />
We've enabled script by typing `script output.txt` 
<br />
We now run theHarvester `theHarvester -d microsoft.com -l 1000 -b all`
<br />
Now we let that run and all the commands and the output that come from theHarvester and are disabled on the screen are written to our output.txt file. Once our command has completed successfully we simply exit out of script by typing `exit`
<br />
Now this is where we get down to filtering out data, theHarvester collects a lot of OSINT data for us to use but it's all in one file...what it we wanted to strip out say just twitter handles or email addresses it found, so that we can use it in other applications. If we just used the output.txt by itself most of our applications would error with other erroneous input that is in the txt file. Enter Grep
<br />
So let's start with the Twitters by using grep we can strip out the twitter handles into another file. 
<br />
`grep -E -o "@[0-9a-zA-Z]+" < output.txt > twitterHandles.txt` 
<br />
This uses a regular expression to strip out a twitter handle like mine @SteveBartimote and then puts it into a text file called twitterHandles.txt... but all that file will contain is twitter usernames!
<br />
Now lets look at email addresses, using the same output.txt file and grep we will use a different regular expression to strip out emails
<br />
`grep -E -o “\b[a-zA-Z0-9.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9.-]+\b” < output.txt > emailAddresses.txt`
<br />
There you have it a text file called emailAddressess.txt containing all the email addresses theHarvester's output has... not you'll notice with starting theHarvester that it's developer's email address is also listed (usually the top entry) be sure to remove it from your file...wouldn't want to spam him.
<br /> you still keep the output.txt as the evidence of 1. the commands you ran and 2. the output you received in your engagement. However that recording of that is done for you with script.
