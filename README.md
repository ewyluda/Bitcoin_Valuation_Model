# Bitcoin_Valuation_Model
#### A model to estimate whether current Bitcoin price is supported by activity on the network.

## Introduction
Since 2017 Bitcoin and the cryptocurreny universe has attracted massive attention and has been a personal interest of mine. While researching ways to value Bitcoin and other cryptocurencies, I came accross the work of Chris Burniske and his book, Cryptoassets: The Innovative Investor's Guide to Bitcoin and Beyond, and became fascinated with his method to determine the fundamental value of cryptocurrenies using Metcalfe's Law.

### Metcalfe's Law
Metcalfe's Law, states that the value of a telecommunications network is proportional to the square of the number of connected users of the system (NV ~ n2).

![Metcalfe's Law Graphic](resources/metcalfe2.png)

Two telephones can make only one connection, five can make 10 connections, and twelve can make 66 connections.

Critics of Metcalfe's Law point to the fact that not all network connections or users contribute equally to the network, to account for this I used Metcalfe's Law (NV ~ n2) along with two variations to the law being Odlyzko's Law and the Generalized Metcalfe's Law (Clearblocks determination) shown below:

![Metcalfe Variations](resources/metcalfe_variations.png)

## Objective
In this study, the goal was to estimate whether Bitcoin's price is supported by activity on the network. To do this, upper and lower bounds for Bitcoin Network Value were derived based on the number of Daily Active Addresses (DAA). 

## Developing Fundamental Upper & Lower Boundaries

Metcalfe's Original Law (NV ~ n2) was used to create the upper fundamental value boundary for Bitcoin. The original law was chosen for the upper boundary because it is the most liberal and considers each and every user equally contributes to the value of the network.

Odlyzko's Law (NV ~ n*ln(n)) was used to create the lower fundamental value boundary. Odlyzko's Law, being the most conservative of the 3 variations studied made the most sense to use for the lower boundary.

![Upper & Lower Boundaries](resources/upper_lower_boundaries.png)

