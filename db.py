import pymongo
import pdb
import datetime
from copy import deepcopy
import json
import locale; locale.setlocale(locale.LC_ALL, 'es_ES.utf8')
import calendar; month_name = [month for month in calendar.month_name]


def get_db(settings, drop):
    connection = pymongo.MongoClient(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
    db_name = settings['MONGODB_DB']
    if drop:
        connection.drop_database(db_name)
    return connection[db_name]


def get_collection(db, collection_name):
    if collection_name in db.list_collection_names():
        return db[collection_name]

    collection = db[collection_name]
    collection.create_index([("reviewer", pymongo.DESCENDING),
                             ("game_name", pymongo.DESCENDING),
                             ("release_date", pymongo.DESCENDING)], unique=True)

    collection.create_index([("release_date", pymongo.DESCENDING)])

    collection.create_index([("score", pymongo.DESCENDING)])

    collection.create_index([("genre", pymongo.DESCENDING),
                             ("release_date", pymongo.DESCENDING),
                             ("score", pymongo.DESCENDING)])

    collection.create_index([("genre", pymongo.DESCENDING),
                             ("score", pymongo.DESCENDING),
                             ("release_date", pymongo.DESCENDING)])


    return collection


def string2time(string_date):
    return datetime.datetime.strptime(string_date, '%d-%m-%Y')


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
    query = {"game_name":{"$regex": name, "$options": 'i'}}
    cursor = collection.find(query).limit(max_number_results)
    return [_process_result(result) for result in cursor]


def build_query(eq_filters, range_filters):
    filter_dict = {}

    and_cond = []
    for field, eq_conds in eq_filters.items():
        if len(eq_conds) == 1:
            filter_dict[field] = eq_conds[0]
        else:
            and_cond += [{field:value} for value in eq_conds]
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



def insert_json(json_path, drop=False):

    target_platforms = ['Xbox Series X','Xbox One', 'PS5', 'PS4', 'PC', 'Nintendo Switch']
    # reviewers_map = {'ign': 'IGN ES', 'hobby': 'Hobby Consolas'}

    with open(json_path, "r") as handle:
        data = json.load(handle)

    indices_to_remove = []
    for idx, el in enumerate(data):
        try:
            data[idx]["release_date"] = string2time(el["release_date"])

            title = el['title']
            description = el["description"]
            platforms = [platform_name for platform_name in target_platforms if (platform_name in title) or 
                                                                                (platform_name in description)]
            if platforms:
                el["platforms"] = platforms

            el["genre"] = el.pop("genres")

        except Exception:
            indices_to_remove.append(idx)
            
    data = [el for idx, el in enumerate(data) if idx not in indices_to_remove]

    MONGODB_SERVER = "localhost"
    MONGODB_PORT = 27017
    MONGODB_DB = "game_reviews"

    settings = {
        'MONGODB_SERVER': MONGODB_SERVER,
        'MONGODB_PORT': MONGODB_PORT,
        'MONGODB_DB': MONGODB_DB
    }
    db = get_db(settings, drop)
    index_coll = get_collection(db, 'reviews')
    insert_many(index_coll, data)
    
if __name__ == "__main__":
    insert_json("ign/2021-02-10.json", drop=False)
