
class ISIEnkoTransformer(object):

    @classmethod
    def transform_date(cls, date):
        return date.split('T')[0]

    @classmethod
    def transform(cls, sale):
        sale_info = cls.transform_to_sale(sale)
        sale_items_info = []
        for sale_item in sale.get_sale_items():
            sale_items_info.append(cls.transform_to_sale_item(sale_item, sale.client, sale.seller))
        sale_payments = []
        for sale_payment in sale.get_sale_payments():
            sale_payments.append(cls.transform_to_sale_payment(sale_payment))
        return {'sale': sale_info, 'items': sale_items_info, 'payments': sale_payments}

    @classmethod
    def transform_to_sale(cls, sale):
        if sale.thread_status in (1, 2, 3, 4):
            sale_date = sale.created_at
        elif sale.thread_status == 5:
            sale_date = sale.date_cancelled
        elif sale.thread_status == 6:
            sale_date = sale.date_approved
        elif sale.thread_status == 7:
            sale_date = sale.expires_at or sale.created_at
        else:
            raise Exception("thread id not know status %d" % sale.thread_status)
        sale_date = cls.transform_date(sale_date)
        return {
            "external_id": sale.id,
            "date": sale_date,
            "external_sale_status": {
                "external_id": sale.thread_status,
                "name": sale.get_status_unicode
            },
            "client": cls.transform_contact_to_client(sale.client),
            "sale_status": sale.enko_status,
            "open_time": None,
            "close_time": None,
            "subtotal": float(sale.subtotal or 0),
            "discount": float(sale.discount or 0),
            "total": float(sale.total)
        }

    @classmethod
    def transform_to_sale_item(cls, list_item, client, seller):
        return {
            'external_id': list_item.id,
            'client': cls.transform_contact_to_client(client),
            'salesman': cls.transform_contact_to_seller(seller),
            'product': list_item.product_name,
            'quantity': float(list_item.quantity),
            'unit_price': float(list_item.price or 0),
            'total': float(list_item.total or 0)
        }

    @classmethod
    def transform_contact_to_seller(cls, seller):
        if not seller:
            return None
        return {
            'external_id': seller.id,
            'name': seller.name
        }

    @classmethod
    def transform_contact_to_client(cls, contact):
        if not contact:
            return None
        if contact.address_line_1 and contact.address_line_2:
            address = unicode(contact.address_line_1) + unicode(contact.address_line_2)
        elif contact.address_line_1:
            address = unicode(contact.address_line_1)
        else:
            address = None
        return {
            "external_id": contact.id,
            "name": contact.name,
            "address": address,
            "district": None,
            "state": str(contact.state) if contact.state else None,
            "city": str(contact.city) if contact.city else None,
            "phone": ""
        }

    @classmethod
    def transform_to_sale_payment(cls, sale_payment):
        return {
            'external_id': sale_payment.id,
            'payment_type': {
                'external_id': sale_payment.operator_name,
                'name': sale_payment.operator_name
            },
            'payment_operator': {
                'external_id': sale_payment.operator_name,
                'name': sale_payment.operator_name
            },
            'total': sale_payment.price
        }
