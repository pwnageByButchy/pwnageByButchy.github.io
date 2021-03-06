---
layout: post
title: Security Feeds with Pi Zero (Phase 1)
description: A hardware project...I know right the software guy is doing a hardware project. Using a Pi Zero (or a few of them) and no special software creating an RTSP feed from a Pi Zero with a Pi Camera attached.
tags:
- Project

---
The aim is to build a security camera system with out of the box electronic components...by this I mean no soldering!

Using a Raspberry Pi Zero (wireless) with a camera kit, create a security camera and a RTSP video feed. To have that recorded and viewable on a main control machine (for the POC I am usinga Ubuntu VM). A condition of the proof of concept is the need to not program too much code.

![Raspberry Pi Zero](/assets/images/ZeroAssembled.JPG "Raspberry Pi Zero Fully Assembled")
![Raspberry Pi Zero](/assets/images/ZeroMeasured.JPG "Raspberry Pi Zero - 8cm long") <br /><br />

Items used:
* Raspberry Pi Zero Wireless
* MicroSD Card with Raspbian Lite
* Raspberry Pi Camera v2
* Raspberry Pi Zero Case (Optional but does include Pi Zero Camera Adapter)
* A Ubuntu Virtual Machine (1GB RAM, 1 CPU)


#### Setup the Pi Zero ####
![Raspberry Pi Zero](/assets/images/ZeroInside.JPG "Raspberry Pi Zero")
![Raspberry Pi Zero](/assets/images/ZeroOutside.JPG "Raspberry Pi Zero")<br /><br />
Setup MicroSD with SSH and Wifi Details and boot Pi Zero

SSH into Pi, run `sudo raspi-config` enable camera, change default password

![Raspberry Pi Zero Raspi-Config](/assets/images/runRaspi-Config.PNG "Raspberry Pi Zero Updating the OS")

![Raspberry Pi Zero Raspi-Config](/assets/images/runRaspi-ConfigMenu.PNG "Raspberry Pi Zero raspi-config main menu")

Let's do the password first. go into Change User Password

![Raspberry Pi Zero Raspi-Config Changing Password](/assets/images/passwordChange.PNG "Raspberry Pi Zero Updating the OS")

Now go into "5 Interfacing Options" and then select "P1 Camera"

![Raspberry Pi Zero Raspi-Config](/assets/images/runRaspi-ConfigMenu.PNG "Raspberry Pi Zero raspi-config main menu")

![Raspberry Pi Zero Enabling Camera](/assets/images/enableCamera.PNG "Raspberry Pi Zero Updating the OS")

Then update OS with `sudo apt update -y && sudo apt upgrade -y`

![Raspberry Pi Zero Updating OS](/assets/images/aptUpdate.PNG "Raspberry Pi Zero Updating the OS")

Now we install VLC to do our streaming `sudo apt install vlc`

![Raspberry Pi Zero Updating OS](/assets/images/installVLC.PNG "Raspberry Pi Zero installing VLC")

Now to initiate the stream we run `raspivid -o - -t 0 -n -w 640 -h 480 -fps 30 -rot 270 -br 50 | cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8554/}' :demux=h264`

![Raspberry Pi Zero Initate the Stream](/assets/images/raspividCommand.PNG "Raspberry Pi Zero Initate the Stream")

Here we are using the inbuilt application raspivid to activate the camera and passing it through the commandline version VLC to create the RTSP stream. Now we can just use VLC on our desktop to "open a network stream" to rtsp://[Pi Zero's IP Address]:8554/ and you should now see the camera's feed.

![Raspberry Pi Zero captured on VLC](/assets/images/vlcOpenNetworkStream.PNG "Raspberry Pi Zero captured on VLC")<br /><br />

![Openning a Network Stream on VLC](/assets/images/vlcRunningStream.PNG "Openning a Network Stream on VLC")<br /><br />
I created a script to run this command on boot so that as soon as the Pi Zero boots it starts streaming video over RTSP.

#### Setting Up the Ubuntu VM ####
Next step was to setup the Ubuntu VM to record the stream. For phase 1 it is recording hourly increments in phase 2 I will add motion detection so it will only record when it detects motion. I used the latest version of Ubuntu, nothing special but again I updated the OS with `sudo apt update && sudo apt upgrade`. The installed ffmpeg for the recording `sudo apt install ffmpeg vlc` also VLC to ensure the VM was seeing the feed but it is not a required component.

I created a bash file to record the video and added it to the crontab so that every hour it would record an hour of video. Stores it in a folder called "Recordings" the a subfolder of the date of the day it was recorded

So we create the folder by running `mkdir /Recordings`

```
#!/bin/bash

date=$(date +%d-%b-%Y)
datetime=$(date +%d-%b-%Y-%H)
fulldatetime=$(date +"%T on the %d-%m-%Y (ACST)")
filename=Camera1-$datetime"00hrs.mp4"
directory="/Recordings/"$date
if [[ -d $directory ]]
then
ffmpeg -i rtsp://[Pi Zero's IP Address]:8554/ -t 01:00:00 -metadata comment="Recording started at $fulldatetime" -metadata title="$filename" -vcodec copy $directory/$filename
else
mkdir $directory
ffmpeg -i rtsp://[Pi Zero's IP Address]:8554/ -t 01:00:00 -metadata comment="Recording started at $fulldatetime" -metadata title="$filename" -vcodec copy $directory/$filename
fi
```

then to ensure the script runs on the hour every hour we add a line to the crontab...

This is just phase 1 of my proof of concept, there are systems out there that do this or a similar thing but I found a lot of the heavy lifting was on the Pi Zero which isnt that powerful. So I decided to start from scratch and initially with a single camera.

Phase 2 will be focusing on the motion detection which will be processed by the Ubuntu VM... I have thoughts of using a Raspberry Pi 4 for this and setting it up to display the video through the HDMI so you can connect it to your TV and watch the feeds. Past that adding more cameras and then testing all the security.

Once that is done seeing how to make it as user friendly to setup as possible. Maybe some hidden of covert cameras as well.
