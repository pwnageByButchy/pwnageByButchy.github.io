---
layout: post
title: Security Feeds with Pi Zero
description: A hardware project...I know right the software guy is doign a hardware project. Using a Pi Zero (or a few of them) and no special software creating an RTSP feed from a Pi Zero with a Pi Camera attached.
tags:
 - Project

---
The aim is to build a security camera system with out of the box electronic components...by this I mean no soldering!

Using a Raspberry Pi Zero (wireless) with a camera kit, create a security camera and a RTSP video feed. To have that recorded and viewable on a main control machine (for the POC I am usinga Ubuntu VM). A condition of the proof of concept is the need to not program too much code.

Items used:
Raspberry Pi Zero Wireless
Raspberry Pi Camera v2
Raspberry Pi Zero Case (Optional but does include Pi Zero Camera Adapter)
MicroSD Card with Raspbian Lite
A Ubuntu Virtual Machine (1GB RAM, 1 CPU)

Setup MicroSD with SSH and Wifi Details and boot Pi Zero

SSH into Pi, run `raspi-config` enable camera, change default password and then update OS with `sudo apt update && sudo apt upgrade`

Now we install VLC to do our streaming `sudo apt install vlc`

Now to initiate the stream we run `raspivid -o - -t 0 -n -w 640 -h 480 -fps 30 -rot 270 -br 50 | cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8554/}' :demux=h264`

Here we are using the inbuilt application raspivid to activate the camera and passing it through the commandline version VLC to create the RTSP stream.

Now we can just use VLC on our desktop to "open a network stream" to rtsp://[Pi Zero's IP Address]:8554/ and you should now see the camera's feed.

I created a script to run this command on boot or the Pi Zero so that as soon as the Pi Zero boots it is streaming video over RTSP.

Next step was to setup the Ubuntu VM to record the stream. For phase 1 it is recording hourly increments in phase 2 I will add motion detection so it will only record when it detects motion.

I used the latest version of Ubuntu, nothing special but again I updated the OS with `sudo apt update && sudo apt upgrade`

The installed ffmpeg for the recording `sudo apt install ffmpeg vlc` also VLC to ensure the VM was seeing the feed but it is not a required component.

I created a bash file to record the video and added it to the crontab so that every hour it would record an hour of video. Stores it in a folder called "Recordings" the a subfolder of the date of the day it was recorded

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

This is just phase 1 of my proof of concept, there are systems out there that do this or a similar thing but I found a lot of the heavy lifting was on the Pi Zero which isnt that powerful. So I decided to start from scratch and initially with a single camera.

Phase 2 will be focusing on the motion detection which will be processed by the Ubuntu VM... I have thoughts of using a Raspberry Pi 4 for this and setting it up to display the video through the HDMI so you can connect it to your TV and watch the feeds. Past that adding more cameras and then testing all the security.

Once that is done seeing how to make it as user friendly to setup as possible. Maybe some hidden of covert cameras as well.
