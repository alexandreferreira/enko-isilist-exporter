import repository
from repository import Contatcs, UserLists, UserListItems, ListActions


def dictfetchall(entity):
    if entity:
        return [
            dict(zip(entity['columns'], row))
            for row in entity['values']
            ]
    else:
        return []


def cleanup_data(data, fields):
    new_data = {}
    for field in fields:
        new_data[field] = data.pop(field)
    return new_data


class Sync(object):
    sync_data = None

    def __init__(self, sync_data):
        self.sync_data = sync_data

    def sync(self):
        print "Contacts: " + str(self.sync_contacts())
        print "Lists: " + str(self.sync_lists())
        print "List Items: " + str(self.sync_list_items())
        self.sync_list_actions()
        self.sync_list_payments()

    def sync_contacts(self):
        with repository.db.atomic():
            for contact in dictfetchall(self.sync_data["contacts"]):
                contact_id = contact.pop("id", None)
                contact = cleanup_data(contact, ["modified_at", "created_at", "deleted", "email", "name",
                                                 "kind", "email_verified", "identity_number", "country", "state",
                                                 "city", "postal_code", "address_line_1", "address_line_2"])
                Contatcs.create_or_update(contact_id, **contact)
        return Contatcs.select().count()

    def sync_lists(self):
        with repository.db.atomic():
            for user_list in dictfetchall(self.sync_data['lists']):
                list_id = user_list.pop('id')
                user_list = cleanup_data(user_list, ["modified_at", "created_at", "deleted", "expires_at", "foreign_id",
                                                     "name", "client_id", "description", "responded_list_id",
                                                     "thread_id", "owner_id",
                                                     "waiting_response", "waiting_acceptance", "acceptance_response",
                                                     "status", "last_status_since", "collaborator_id", "store_id"])
                UserLists.create_or_update(list_id, **user_list)
        return UserLists.select().count()

    def sync_list_items(self):
        with repository.db.atomic():
            for list_item in dictfetchall(self.sync_data['list_items']):
                list_item_id = list_item.pop('id')
                list_item = cleanup_data(list_item, ["modified_at", "created_at", "deleted", "list_id",
                                                     "base_item_id", "display_order", "product_id",
                                                     "product_name", "price", "total", "quantity"])
                UserListItems.create_or_update(list_item_id, **list_item)
        return UserListItems.select().count()

    def sync_list_payments(self):
        with repository.db.atomic():
            for list_action in dictfetchall(self.sync_data['list_payments']):
                list_action_id = list_action.pop('id')
                list_action = cleanup_data(list_action, ["list_id", "store_id", "client_id", "thread_id",
                                                         "price", "operator_status", "status"])
                UserListItems.create_or_update(list_action_id, **list_action)
        return ListActions.select().count()

    def sync_list_actions(self):
        with repository.db.atomic():
            for list_action in dictfetchall(self.sync_data['list_actions']):
                list_action_id = list_action.pop('id')
                list_action = cleanup_data(list_action, ["modified_at", "created_at", "deleted", "list_id",
                                                         "kind", "user_id", "motive"])
                ListActions.create_or_update(list_action_id, **list_action)
        return ListActions.select().count()

