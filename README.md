# FoodborneML

[Adaptive Information Extraction from Social Media for Actionable Inferences in Public Health](http://publichealth.cs.columbia.edu/)

Columbia University, Computer Science Department 

This repo holds the code for our system that analyzes social media documents and extracts evidence of foodborne illness outbreaks in restaruants. 

This system has been developed and maintained at Columbia University and has been serving API requests on a daily basis by the NYC Department of Health and Mental Hygiene and the Los Angeles County Department of Public Health.

## Structure of the repo: 

[src](src/) contains the system code, which downloads and classifies Yelp and Twitter documents for evidence of foodborne illness events, and serves the classified documents to health departments via an API. (Requires python 3.6)

[jamia_2017](jamia_2017/official) contains experimental code used to produce the results for our manuscript [Discovering Foodborne Illness in Online Restaurant Reviews](https://academic.oup.com/jamia/advance-article/doi/10.1093/jamia/ocx093/4725036), published in [JAMIA](https://academic.oup.com/jamia
), October 10, 2018. (Requires python 2.7)
