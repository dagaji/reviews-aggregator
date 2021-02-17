from app import app
from app import db, coll
from flask import render_template, request, Markup, current_app
from app.config import get_config, get_assets
import pdb
import datetime
import os.path

PAGE_SIZE = 9

@app.route('/')
@app.route('/index')
def index():

    config = get_config()
    reviewers_styles = [value["styles_url"] for _, value in get_assets().items()]
    reviewers = config['reviewers']
    genres = coll.distinct('genre')
    platforms = coll.distinct('platforms')
    dates_intervals = ["Anytime", "Past week", "Past month"]

    return render_template('base.html', reviewers=reviewers, 
                                        genres=genres, 
                                        platforms=platforms,
                                        dates_intervals=dates_intervals,
                                        reviewers_styles=reviewers_styles)


def extract_eq_filters():
    eq_filters = {}
    for key, val in request.args.items():
        if key in ["reviewer", "platforms", "genre"]:
            if key == "reviewer" and val == "any":
                continue
        else:
            continue
        eq_filters[key] = val.split(',')
    return eq_filters


def extract_range_filters():
    range_filters = {}
    date_interval = request.args.get("posted_date", "Anytime")
    if date_interval in ["Past week", "Past month"]:
        today = datetime.datetime.strptime("30-12-2020", '%d-%m-%Y')
        range_filters["release_date"] = {"Past week": (today - datetime.timedelta(days=7), today),
                                         "Past month":(today - datetime.timedelta(days=30), today)
                                        }[date_interval]
    return range_filters


@app.route('/list')
def list_reviews():
    if "search" in request.args:
        reviews = db.search_by_name(coll, request.args.get("search"))
        has_next = False
    else:
        eq_filters = extract_eq_filters()
        range_filters = extract_range_filters()
        query = db.build_query(eq_filters, range_filters)
        order = request.args.get("order", "release_date")
        page_num = int(request.args.get("page_num", 0))
        reviews, has_next = db.list_reviews(coll, query, page_size=PAGE_SIZE, 
                                                        offset=page_num*PAGE_SIZE, 
                                                        sort_by=order)

    reviewers_logos = {}
    for key, value in get_assets().items():
        with open(value["logo_path"], mode='r') as f:
            reviewers_logos[key] = f.read()

    return render_template('list.html', reviews=reviews, 
                                        reviewers_logos=reviewers_logos, 
                                        has_next=has_next)