import json
import sys

from enko import EnkoAPI
from isilist_api import IsilistAPI
from repository import UserLists
from sync import Sync
from transformer import ISIEnkoTransformer

if __name__ == "__main__":
    isilist_api = IsilistAPI()
    email, password = sys.argv[1], sys.argv[2]
    isilist_api.init(email, password)

    sync = Sync(isilist_api.get_sync())
    sync.sync()

    user_lists = UserLists.extract_as_enko()
    user_lists = [ISIEnkoTransformer.transform(user_list) for user_list in user_lists]
    enko_api = EnkoAPI()
    enko_api.process_sales(user_lists, '2016-01-01')
