import calendar
import pymongo
import pdb
import datetime
from copy import deepcopy
import json
import locale
locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
month_name = [month for month in calendar.month_name]


def get_db(settings, drop):
    connection = pymongo.MongoClient(
        settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
    db_name = settings['MONGODB_DB']
    return connection[db_name]


def get_collection(db, collection_name):
    return db[collection_name]


def insert_many(collection, items_list):
    try:
        collection.insert_many(items_list)
    except pymongo.errors.DuplicateKeyError:
        return False
    return True


def _process_result(result):
    result["genre"] = ", ".join(result["genre"])
    result["platforms"] = ", ".join(result["platforms"])
    result["release_date"] = str(result["release_date"]).split(' ')[0]
    result["score"] = int(result["score"])
    return result


def list_reviews(collection, filter_dict, sort_by="release_date", offset=0, page_size=1):
    cursor = collection.find(filter_dict).sort(sort_by, pymongo.DESCENDING)
    if offset > 0:
        cursor = cursor.skip(offset)
    cursor = cursor.limit(page_size+1)
    results = [_process_result(result) for result in cursor]
    has_next = len(results) > page_size
    if has_next:
        return results[:-1], has_next
    return results, has_next


def search_by_name(collection, name, max_number_results=5):
    query = {"game_name": {"$regex": name, "$options": 'i'}}
    cursor = collection.find(query).limit(max_number_results)
    return [_process_result(result) for result in cursor]


def build_query(eq_filters, range_filters):
    filter_dict = {}

    and_cond = []
    for field, eq_conds in eq_filters.items():
        if len(eq_conds) == 1:
            filter_dict[field] = eq_conds[0]
        else:
            and_cond += [{field: value} for value in eq_conds]
    if and_cond:
        filter_dict["$and"] = and_cond

    for range_field, (inf_limit, sup_limit) in range_filters.items():
        _range_filter = {range_field: {}}
        if inf_limit:
            _range_filter[range_field]["$gt"] = inf_limit
        if sup_limit:
            _range_filter[range_field]["$lt"] = sup_limit
        if _range_filter[range_field]:
            filter_dict.update(_range_filter)
    return filter_dict
