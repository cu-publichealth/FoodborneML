## Interactive Map of NYC Restaurants
This interactive map visualization was created to help track foodborne illness outbreaks in NYC restaurants. The Blue dots correspond to restaurants, and the opacity of the red-fill is the number of foodborne illness outbreaks in that region normalized over NYC

The code was developped at Columbia by Sam Raab. Source: https://github.com/raabsm/illnessmap

## Demo
![Demo](./demo.gif)

## Visualization of Yelp reviews
After clicking on a restaurant, a panel on the right shows Yelp reviews that discuss potential incidents of food poisoning. 
The panel shows only important sentences of Yelp reviews while you can find the whole review as well as extra information by clicking the "More Info" button.  

The classifier used to classify reviews and highlight important sentences is called HSAN and is described in detail at the following paper: https://www.aclweb.org/anthology/D19-5501.pdf

# Installation:

1) docker-compose build
2) docker-compose up

# Citation 

```
@inproceedings{karamanolakis-etal-2019-weakly,
    title = "Weakly Supervised Attention Networks for Fine-Grained Opinion Mining and Public Health",
    author = "Karamanolakis, Giannis and Hsu, Daniel and Gravano, Luis",
    booktitle = "Proceedings of the 5th Workshop on Noisy User-generated Text (W-NUT 2019)",
    year = "2019",
    address = "Hong Kong, China",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/D19-5501",
}
```
