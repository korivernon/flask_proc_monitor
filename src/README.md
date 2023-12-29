# Front End

## API
Currently, there are only two functions - not deployed officially. To be completed
at a later date. 

- /volRunnerPositions
  - this will get the current positions that the vol runner selected for the current day.
- /kickOffVolRunner
  - This will kick off the volatility runner that analyzed performance for the current day
- /longStraddle/<ticker>/<dte>/<method>
  - This will generate long straddles for a ticker given a ticker, days until expiration, and method 
  of generating the strike of the straddle. 
    - You can either choose the **mean** over the previous DTE days, or current **spot**