# Jane_Street_ETC

These are a set of codes used in Electronic Trading Challenges hosted by Jane Street in June, 2019.

## What does each file do?

Relevant files are Dyna_Q.py and trading-bot.py. Other files were not used or just used for a testing purpose.

### Dyna_Q.py
This implements Dyna-Q reinforcement learning agent. It observes the current trading prices of bond, decides whether we should buy or sell it or do nothing, and receives reward according to price changes. It balances out exploration and exploitation using Upper-Confidence-Bound (UCB1). It has some issues with convergence. The updated version is available at https://github.com/akonoroshi/Dyna_Q.

### trading-bot.py
This is a main driver to communicate with market using TCP. There were eight kinds of bonds (specified in symbols), and we had an instance of Dyna-Q for each bond. We dealt with this complexity with multiprocessing. It also calculates reward for Dyna-Q.
