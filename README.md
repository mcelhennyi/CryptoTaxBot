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
January 2018: This is currently a WIP but I hope to have this done sometime in the coming months (Feb/Mar 2018)  
Update (2/12/18): The bot can pull down all past trades (up to 500 per coin) and calculate the `Fair Market Value` of that trade on the day it was made. The `Fair Market Value` used in this program is the `average` cost of `BTC` on the `DAY` of the trade. It will save all the information from binance along with calculated `Fair market values` into a CSV for visualizing in MS Excel.  

# Calculated Values and Calculations
## Definitions
FMV = Fair Market Value, here it is synonomous with the average cost in USD of the coin on the date of trade.  
CCT = Commission coin type  
Base currency = The currency used to buy the alt coin (BTC, ETH, BNB, USDT on Binance)  
Money Flow = The value of the trade, positive for for Sells and Negative for Buys  
PC = Purchased coin, the coin that is being purchased with the `base currency`

## Calculations
### Fair Market Values
The `Fair market value` of each coin is retrieved from the [cryptocompare](https://www.cryptocompare.com/) API as daily averages. Each time a new `fmv` is requested from the API it is buffered locally so that later `fmv` calls are greatly sped up.

### Money Flow Calculation
Notice that if the trade was A `buy` the resulting `money flow` is negative and the fee is added to the transaction, showing that we spent/lost money. Conversely notice that if the trade is a `sell` then the resulting `money flow` is positive and the fee is subtracted as a loss.  
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

# Installation
[Visit here for installation instructions](https://github.com/mcelhennyi/CryptoTaxBot/blob/master/INSTALLATION.md)

# Notice
I am not a CPA, accountant, or financial advisor. I take no responsibility for use of this app. If you have questions feel free to email me. imcelhenny1@gmail.com

# Donations
If this tool made your life easier, make mine easier for making it!  
BTC: 16HuArdg9DzXFyBopvkkBYfsSRtcodeq7v  
ETH/ERC-20 Tokens: 0xb70A779095F455419d9B6120288eb8C2963d1708  
LTC: LbLYzZLJCW4jA8xR5SSW8BLTK8hR8PpGnU  
