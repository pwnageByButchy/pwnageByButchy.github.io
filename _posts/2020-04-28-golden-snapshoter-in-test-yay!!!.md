---
layout: post
title: The Golden Snapshoter is in Test...Yay!!!!!
description: A Python3 script to create and maintain a “Golden Image” of VMs in VMWare Workstation (for the moment) on either a Windows or Linux hosts!....is now in Test!
tags:
 - Tools
 - Project

---
So we are in Test, Golden Snapshoter was created for the purpose of maintaining a Golden Image/Master Image of your VMs in VMWare.

Features included:
1. Generating Git Repos script
2. Creating a Forensic Clone of your VMs
3. Reverting to your Golden Image, Updating the VM's OS and then saving that as the up to date Image

This saves deleting the VM, downloading the VM and then updating it, download all the Git repos, download your git repos everytime time you mess up a VM or in the case of Pentesters when you start work on a new job start fresh but updated!

All you need to do is:
1. Create your VM - Download and Create your Guest VM with the OS of your choice
2. Install python3 and VMWare tools
3. Install any additional items you want included in your Image - Favourite Browser, Additional Tools, Password Manager, Git Repos
4. Configure your VM
5. Shutdown your VM

Then to run it do the following:
6. Configure all the variables in the settings.py to match your environment
7. run python3 ./GoldenSnapshoter.py and follow the prompts

This application generates a "git_script.txt" in the UpdateScripts directory, if you want this included in your system update copy the contents of this txt file into the appropriate UpdateScript. This is optional based on what you want to do and therefore a manual task.

<center><a title="GoldenSnapshoter on Github" href="https://github.com/pwnageByButchy/GoldenSnapshoter" target="_blank"><i class="fab fa-github fa-2x"></i></a></center>
