# FoodborneNYC

The new implementation of a system to mine social media documents for evidence of foodborne illness outbreaks in NYC restaurants.

This software is used by the NYC Department of Health and Mental Hygiene (DOHMH) to inform their practices.

[src](src/) contains the code which downloads and classifies Yelp and Twitter docs for evidence of foodborne illness events, and serves the analyzed data via an api. (Note that this package uses python 3.6)

[jamia_2017](jamia_2017/official) contains experimental code used to produce the results for our manuscript [Discovering Foodborne Illness in Online Restaurant Reviews](https://academic.oup.com/jamia/advance-article/doi/10.1093/jamia/ocx093/4725036), published in [JAMIA](https://academic.oup.com/jamia
), October 10, 2018. (Note that this code uses python 2.7)
