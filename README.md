# CryptoTaxBot
A way to automate logging all of your trades for taxes. This is perfect for people using a day trading bot, or for people who day trade. 

# Goal
Create a logger that runs once a month (configurable) and pulls down all trades since last pull, calculate fair market value at time of trade and then logs these trades into a .csv file for easy viewing in Excel. Then it will have an optional backup feature that will upload the .csv's to google drive to keep them in case the computer this program runs on crashes or fails.  

Since I am making this for myself, I am doing this open source and am not selling it.

# Proposed Life cycle
Note: ``highlighted text`` means this part is complete  
1) ``Pull down all trades`` that are currently not logged for the year.
2) ``Calculate the fair market value``, as well as profit/loss ``for each trade``.
3) ``Save these values as well as the data from the exchange to a .csv (spreadsheet).``
4) Upload the spreadsheet to a google drive folder for safe backup. (Optional, recommended)
5) Repeat each month (configurable)

# Status
## Current
January 2018: This is currently a WIP but I hope to have this done sometime in the coming months (Feb/Mar 2018)  
Update (2/12/18): The bot can pull down all past trades (up to 500 per coin) and calculate the `Fair Market Value` of that trade on the day it was made. The `Fair Market Value` used in this program is the `average` cost of `BTC` on the `DAY` of the trade. It will save all the information from binance along with calculated `Fair market values` into a CSV for visualizing in MS Excel.  

## TODO
- create a way to only retrieve what has not been retrieved yet.
- automate uploading results to google drive for garunteed backup
- retrieve more than 500 per coin, if needed (imagine running this program once at the end of the year, instead of periodically throughout the year)

# Algorithm Descriptions
## Definitions
FMV = Fair Market Value, here it is synonomous with the average cost in USD of the coin on the date of trade.  
CCT = Commission coin type  
Base currency = The currency used to buy the alt coin (BTC, ETH, BNB, USDT on Binance)  
Money Flow = The value of the trade, positive for for Sells and Negative for Buys  
PC = Purchased coin, the coin that is being purchased with the `base currency`

## Calculations
### Fair Market Value
The `Fair market value` of each coin is retrieved from the [cryptocompare](https://www.cryptocompare.com/) API as daily averages. Each time a new `fmv` is requested from the API it is buffered locally so that later `fmv` calls are greatly sped up.

### Money Flow
Notice that if the trade was A `buy` the resulting `money flow` is negative and the fee is added to the transaction, showing that we spent/lost money. Conversely notice that if the trade is a `sell` then the resulting `money flow` is positive and the fee is subtracted as a loss.  
Note: You may decide to check my work, I encourage it...however if you do you may see that the `money flow` seems to not make sense. You think to yourself "I know I sold this for a gain, but my money flow says its a loss".  
There are two scenarios:  
1) You sold on the same day, and maybe the quantities were different (you sold with some dust left over)  
or  
2) you sold on different days and the value of BTC averaged over the day doesnt reflect the actual value of the BTC at the time of sale (maybe you bought on a valley and sold at a peak on two different days, but the average was no where near the valley/peak). This is ok [says an article from investopedia](https://www.investopedia.com/university/definitive-bitcoin-tax-guide-dont-let-irs-snow-you/definitive-bitcoin-tax-guide-chapter-2-trading-gains-and-losses-fair-market-value.asp), since using the daily average for each day is a "reasonable manner which is consistently applied"(investopedia). 

#### The Money Flow Calculation
```
if is_buy:
    # If we are buying this we count it as a negative flow.
    # However if we are buying we want the fee to look like an outflow, so we add it
    #             n1  *          amt of <sym>          * USD / <sym>  + $USD
    flow = -((quantity * value_of_sym_in_base_currency * base_fmv) + fee_usd)
else:
    # We sold, so we need to show our profit as a positive flow, but the fee is still a negative flow
    flow = quantity * value_of_sym_in_base_currency * base_fmv - fee_usd
```
`quantity` is straight out of the binance api response for this trade  
`value_of_sym_in_base_currency` is the value of a single `PC` in `Base Currency`  
`base_fmv` is the USD value of one `base currency` coin  
`fee_usd` is the value of the fee binance collected in USD  

# How to Use
## Installation
[Visit here for installation instructions](https://github.com/mcelhennyi/CryptoTaxBot/blob/master/INSTALLATION.md)

## Running the program
The program can be launched in a terminal/command-prompt by running the following commad:
```
cd CryptoTaxBot/
python main.py
```
Notice: This will only run the program once. I plan to create a script to add this program to a cron-job for linux, but have not gotten to that part yet. Feel free to try cron-jobs out for your self. 

# Notice
I am not a CPA, accountant, or financial advisor. I take no responsibility for use of this app. If you have questions feel free to email me, or open up an issue above. 

# Contact
Email: imcelhenny1@gmail.com  
Telegram: https://t.me/cryptotaxbot

# Donations
If this tool made your life easier then help make mine easier for making it!  
BTC: 16HuArdg9DzXFyBopvkkBYfsSRtcodeq7v  
ETH/ERC-20 Tokens: 0xb70A779095F455419d9B6120288eb8C2963d1708  
LTC: LbLYzZLJCW4jA8xR5SSW8BLTK8hR8PpGnU  
