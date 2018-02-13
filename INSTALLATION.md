# Setup Python
## Install Python
I suggest you download and install Anaconda 4.2 (Python 3.5) for future library use compatibility, but standard Python3.5 is plenty.

## Pull Code Down
Open a command prompt
```
cd <location for install>
git clone https://github.com/mcelhennyi/CryptoTaxBot.git CryptoTaxBot
```

## Install Project Dependencies
Linux:
```
cd CryptoTaxBot
sudo pip install -e requirements.txt
```

Windows:

Open Administrator command prompt and type,
```
cd CryptoTaxBot
pip install -e requirements
```

# Create API keys
Currently only binance is supported by this bot. Please visit binance and create a read-only api key. Then once they key is aquired save to a file.

Create a `.keys` file and place it inside the `CryptoTaxBot` directory. The file should look as follows:
```
binance-key = <public key>
binance-secret = <private key, or 'secret'>
```

# Installation Complete
Now installation is compelte and the `CryptoTaxBot` is ready for use. Due to binace Rest-API restrictions this bot will take a while to run when it runs, since Binance limits Rest-API calls to 120 per minute. This bot will only call to binance at a max of 60 calls per minute, or 1 per second. Secondly, the API used for the `FairMarketValue` seems to be slow to respond, so it can add some delay as well. You will notice at first the FMV API calls will slow the process down quite a bit, but as time goes on the FMV value per each day is buffered and the buffered value is used instead of asking for the same value from the FMV API, this drastically increases the speed at which the bot will run.
