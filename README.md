# reviews-aggregator

Responsive web application to explore game reviews extracted using [reviews-scraper](https://github.com/dagaji/reviews-scraper).
You can find more information about this project on [this post](https://dagaji.netlify.app/p/building-a-website-to-display-the-scraped-data/).

Technologies used:
* [Twitter Bootstrap](https://getbootstrap.com)
* [Flask](https://flask.palletsprojects.com)
* [MongoDB](https://www.mongodb.com/)

The website looks like this:

![Website screenshot](https://raw.githubusercontent.com/dagaji/reviews-aggregator/master/docs/images/screenshot.png)

## Installation

To install python dependencies type: 

`pip install -r requeriments.txt`

## Usage

Before you launch the web applicatication, some data must be stored in the MongoDB database. You can either insert reviews
using [reviews-scraper](https://github.com/dagaji/reviews-scraper) or you can manually insert some example data. If you decide for the latter,
please type the following command:

`mongoimport --db game_reviews --collection reviews --file data.json --drop`

After the data is in place, you can launch the application by typing:

`flask run`
