# FoodborneML

[Adaptive Information Extraction from Social Media for Actionable Inferences in Public Health](http://publichealth.cs.columbia.edu/)

Columbia University, Computer Science Department 

This repo holds the code for our system that analyzes social media documents and extracts evidence of foodborne illness outbreaks in restaurants. 

This system has been developed and maintained at Columbia University and has been serving daily API requests by the NYC Department of Health and Mental Hygiene and the Los Angeles County Department of Public Health.

## Structure of the repo: 

[api](api/) contains our system code, which downloads and classifies Yelp and Twitter documents for evidence of foodborne illness events, and serves the classified documents to health departments through an API. (Requires python 3.6)

[jamia_2017](jamia_2017/official) contains experimental code used to produce the results for our manuscript [Discovering Foodborne Illness in Online Restaurant Reviews](https://academic.oup.com/jamia/advance-article/doi/10.1093/jamia/ocx093/4725036), published in [JAMIA](https://academic.oup.com/jamia), October 10, 2018. (Requires python 2.7)

[foodborne-viz](foodborne-viz/) contains code for our interactive visualization platform that displays a map of NYC restaurants and the corresponding Yelp reviews that disclose evidence of foodborne illness events. For the efficient exploration of multiple reviews in our platform, we display the most important sentences that were highlighted by our classifier, as described in our [W-NUT@ EMNLP'19 paper](https://www.aclweb.org/anthology/D19-5501.pdf).

[weakly-supervised-cotraining](https://github.com/gkaramanolakis/ISWD/tree/41452f447284491cf8ade8e09f3bc4e314ec64f7) contains code for our weakly-supervised co-training method that trains classifiers for aspect detection (e.g., restaurant price, food quality) using just a few keywords per aspect, as described in our [EMNLP '19 paper](https://www.aclweb.org/anthology/D19-1468.pdf).

[cross-lingual](https://github.com/gkaramanolakis/CLTS/tree/14356e96910caf2b1c2262cf390873f3dedaa783/) contains code for our cross-lingual text classification method that trains classifiers across languages without the requirement of training data for each target language, as described in our [Findings of EMNLP '20 paper](https://www.aclweb.org/anthology/2020.findings-emnlp.323.pdf). We will soon include the code for extending our public health system to languages beyond English, as described in our [LOUHI @ EMNLP '20 paper](https://www.aclweb.org/anthology/2020.louhi-1.15.pdf). 
