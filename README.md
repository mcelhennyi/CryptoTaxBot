# CryptoTaxBot
A way to automate logging all of your trades for taxes. This is perfect for people using a day trading bot, or for people who day trade. 

# Goal
Create a logger that runs once a month (configurable) and pulls down all trades since last pull, calculate fair market value at time of trade and then logs these trades into a .csv file for easy viewing in Excel. Then it will have an optional backup feature that will upload the .csv's to google drive to keep them in case the computer this program runs on crashes or fails.  

Since I am making this for myself, I am doing this open source and am not selling it.

# Life cycle
1) Pull down all trades that are currently not logged for the year.
2) Calculate the fair market value, as well as profit/loss for each trade.
3) Save these values as well as the data from the exchange to a .csv (spreadsheet).
4) Upload the spreadsheet to a google drive folder for safe backup. (Optional, recommended)
5) Repeat each month (configurable)

# Status
This is currently a WIP but I hope to have this done sometime in the coming months (Feb/Mar 2018)

# Installation
(When finished I will have install instructions)

# Notice
I am not a CPA, accountant, or financial advisor. I take no responsibility for use of this app. If you have questions feel free to email me. imcelhenny1@gmail.com

# Donations
BTC: 16HuArdg9DzXFyBopvkkBYfsSRtcodeq7v

ETH/ERC-20 Tokens: 0xb70A779095F455419d9B6120288eb8C2963d1708

LTC: LbLYzZLJCW4jA8xR5SSW8BLTK8hR8PpGnU
