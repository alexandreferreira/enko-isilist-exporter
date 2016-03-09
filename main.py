import sys

from isilist_api import IsilistAPI
from repository import UserLists, UserListItems
from sync import Sync

if __name__ == "__main__":
    isilist_api = IsilistAPI()
    email, password = sys.argv[1], sys.argv[2]
    isilist_api.init(email, password)

    sync = Sync(isilist_api.get_sync())
    sync.sync()

    user_lists = list(UserLists.extract_as_enko())
    print user_lists
    for user_list in user_lists:
        items = list(UserListItems.get_all_items_from_list(user_list.id))
        print items
        print "--------------------"
        print "\n"

