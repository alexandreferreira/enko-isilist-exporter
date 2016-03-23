# coding=utf-8
from peewee import Model, BigIntegerField, CharField, BooleanField, IntegerField, DecimalField, \
    PrimaryKeyField, SqliteDatabase, SQL, DoesNotExist, fn

db = SqliteDatabase('isilist.db')


class BaseModel(Model):
    id = PrimaryKeyField()
    modified_at = CharField(null=True)
    created_at = CharField(null=True)
    deleted = BooleanField(null=True)

    class Meta:
        database = db

    @classmethod
    def create_or_update(cls, _id, **kwargs):
        if cls.select().where(cls.id == _id).count() == 1:
            cls.update(**kwargs)
        else:
            cls.create(id=_id, **kwargs)


class UserLists(BaseModel):

    STATUS = {
        '1': 'Aberta',
        '2': 'Aguardando Resposta',
        '3': 'Em Atendimento',
        '4': 'Esperando Aceitação',
        '5': 'Cancelada',
        '6': 'Fechada',
        '7': 'Expirada'
    }

    foreign_id = CharField(null=True)
    owner_id = BigIntegerField()
    store_id = BigIntegerField(null=True)
    name = CharField(null=True)
    client_id = BigIntegerField(null=True)
    description = CharField(null=True)
    responded_list_id = BigIntegerField(null=True)
    thread_id = BigIntegerField()
    thread_status = IntegerField()
    waiting_response = BooleanField(null=True)
    waiting_acceptance = BooleanField(null=True)
    acceptance_response = BooleanField(null=True)
    status = IntegerField(null=True)
    last_status_since = CharField(null=True)
    collaborator_id = BigIntegerField(null=True)
    discount = DecimalField(null=True)
    expires_at = CharField(null=True)

    @classmethod
    def get_all_received_lists(cls):
        where = """
                (
                  (
                      (responded_list_id <> 0 OR status IN (1, 2, 4, 3, 5, 7))
                      or
                      EXISTS (SELECT 1 FROM listactions la_a
                                WHERE la_a.list_id = id
                                  AND la_a.kind = 1 AND la_a.deleted = 0)
                  )
                )
                 """
        return cls.select().where(SQL(where))

    @classmethod
    def extract_as_enko(cls):
        return cls.get_all_received_lists()

    @property
    def client(self):
        try:
            return Contatcs.get(Contatcs.id == self.client_id)
        except DoesNotExist:
            return None

    @property
    def seller(self):
        if self.collaborator_id:
            return Contatcs.get(Contatcs.id == self.collaborator_id)
        else:
            return None

    @property
    def subtotal(self):
        return UserListItems\
            .select(fn.Sum(UserListItems.total))\
            .filter(UserListItems.list_id == self.id)\
            .scalar()

    @property
    def total(self):
        return (self.subtotal or 0) - (self.discount or 0)

    @property
    def date_approved(self):
        return ListActions.get(ListActions.list_id == self.id and
                               ListActions.kind == 1 and
                               ListActions.user_id == self.client_id).created_at

    @property
    def date_cancelled(self):
        return ListActions.get(ListActions.list_id == self.id and
                               ListActions.kind == 6).created_at

    @property
    def date_rejected(self):
        return ListActions.get(ListActions.list_id == self.id and
                               ListActions.kind == 2).created_at

    @property
    def seller(self):
        try:
            return Contatcs.get(Contatcs.id == self.collaborator_id)
        except DoesNotExist:
            return None

    @property
    def enko_status(self):
        if self.thread_status in (1, 2, 3, 4, 5):
            return 1
        elif self.thread_status == 6:
            return 3
        elif self.thread_status in (5, 7):
            return 4


    @property
    def get_status_unicode(self):
        return UserLists.STATUS.get(str(self.thread_status))

    def get_sale_items(self):
        return UserListItems.get_all_items_from_list(self.id)

    def get_sale_payments(self):
        return ListPayments.get_all_payments_from_list(self.id)

    def __unicode__(self):
        return "%s - %s" % (self.id, self.name)


class UserListItems(BaseModel):
    foreign_id = CharField(null=True)
    list_id = BigIntegerField()
    base_item_id = BigIntegerField(null=True)
    display_order = IntegerField(null=True)
    product_id = BigIntegerField(null=True)
    product_name = CharField(null=True)
    price = DecimalField(null=True)
    total = DecimalField(null=True)
    quantity = DecimalField(null=True)

    def __unicode__(self):
        return "%s - %s " % (self.id, self.product_name)

    @classmethod
    def get_all_items_from_list(cls, list_id):
        return cls.select().where(cls.list_id == list_id)


class Profile(BaseModel):
    kind = IntegerField()
    email = CharField()
    name = CharField()
    email_verified = BooleanField()
    identity_number = CharField(null=True)
    country = CharField(null=True)
    state = CharField(null=True)
    city = CharField(null=True)
    postal_code = CharField(null=True)
    address_line_1 = CharField(null=True)
    address_line_2 = CharField(null=True)

    def __unicode__(self):
        return "%s - %s " % (self.id, self.name)

    class Meta:
        database = db


class Contatcs(BaseModel):
    kind = IntegerField()
    email = CharField()
    name = CharField()
    email_verified = BooleanField()
    identity_number = CharField(null=True)
    country = CharField(null=True)
    state = CharField(null=True)
    city = CharField(null=True)
    postal_code = CharField(null=True)
    address_line_1 = CharField(null=True)
    address_line_2 = CharField(null=True)

    def __unicode__(self):
        return "%s - %s " % (self.id, self.name)

    class Meta:
        database = db


class ListPayments(BaseModel):
    list_id = BigIntegerField()
    store_id = BigIntegerField()
    client_id = BigIntegerField()
    thread_id = BigIntegerField()
    price = DecimalField()
    operator_name = CharField(null=True)
    operator_status = CharField()
    status = CharField()

    def __unicode__(self):
        return "%s - %s " % (self.id, self.list_id)

    class Meta:
        database = db

    @classmethod
    def get_all_payments_from_list(cls, list_id):
        return cls.select().where(cls.list_id == list_id and (cls.status == 'AUTHORIZED' or
                                                              cls.status == 'PAID'))


class ListActions(BaseModel):
    kind = IntegerField()
    user_id = BigIntegerField()
    motive = CharField(null=True)
    list_id = BigIntegerField()

    class Meta:
        database = db

    def __unicode__(self):
        return "%s - %s - %s" % (self.id, self.kind, self.user_id)


try:
    db.create_tables([ListActions, ListPayments, UserListItems, UserLists, Contatcs])
except:
    pass
