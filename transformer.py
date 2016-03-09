
class ISIEnkoTransformer(object):

    @classmethod
    def transform_to_sale(cls, sale):
        if sale.thread_id in (1, 2, 3, 4):
            sale_date = sale.created
        elif sale.thread_id == 5:
            sale_date = sale.date_cancelled
        elif sale.thread_id == 6:
            sale_date = sale.date_done
        elif sale.thread_id == 7:
            # TODO quando uma lista esta expirada?
            sale_date = None
        else:
            raise Exception("thread id not know status %d" % sale.thread_id)

        return {
            "external_id": sale.id,
            "date": sale_date,
            "external_sale_status": {
                "external_id": sale.thread_id,
                "name": sale.thred_id_unicode
            },
            "client": {
                "external_id": sale.client_id,
                "name": "",
                "address": "",
                "district": "",
                "state": "",
                "city": "",
                "phone": ""
            },
            "sale_status": sale.enko_sale_status,
            "open_time": "",
            "close_time": "",
            "subtotal": sale.subtotal,
            "discount": sale.discount,
            "total": sale.total
        }

    @classmethod
    def transform_to_sale_item(cls, sale_item):
        pass

    @classmethod
    def transform_to_sale_payment(cls, sale_payment):
        pass
