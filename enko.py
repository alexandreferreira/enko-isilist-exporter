import StringIO
import gzip
import json
import os

import requests


class EnkoAPI(object):

    remote_sales = []
    remote_sales_keys = []

    sales_to_send = []

    enko_requests = None

    def __init__(self):
        self.enko_requests = EnkoRequests()

    def process_sales(self, sales_info, date):

        sales_ids = map(lambda x: str(x['sale']['external_id']), sales_info)

        self.remote_sales = self.enko_requests.get_all_sales_by_date(sales_ids, date)
        self.remote_sales_keys = {sale["external_id"]: sale for sale in self.remote_sales['saved']}

        for sale in sales_info:
            remote_sale = self.get_remote_sale(sale['sale']['external_id'])
            if remote_sale and not self.check_sale_changed(sale['sale'], remote_sale):
                dirty_items = self.sale_items_equals(sale['sale'], sales_info['items'])
                dirty_payments = self.payments_not_equals(sale['sale'], sales_info['payments'])
                if not dirty_items and not dirty_payments:
                    continue
            self.sales_to_send.append(sale)
        self.sales_to_send = map(lambda x: {'sale': x['sale'],
                                            'sale_items': x['items'],
                                            'sale_payments': x['payments']}, self.sales_to_send)
        self.enko_requests.send_sales_by_date(sales_info, date)

    def sale_items_equals(self, sale, local_sale_items):
        remote_sale_items = self.enko_requests.get_all_sales_items_by_sale(sale['external_id'])
        remote_sale_items_keys = {item["external_id"]: item for item in remote_sale_items}
        for item in local_sale_items:
            remote_item = remote_sale_items_keys.get(item['external_id'])
            if not remote_item or self.check_sale_item_changed(item, remote_item):
                return False
        return True

    def payments_not_equals(self, sale, local_sale_payments):
        remote_payments = self.enko_requests.get_all_sale_payments_by_sale(sale['external_id'])
        remote_payments_keys = {payment["external_id"]: payment for payment in remote_payments}
        for payment in local_sale_payments:
            remote_payment = remote_payments_keys.get(payment['external_id'])
            if not remote_payment or self.check_sale_sale_payment_changed(payment, remote_payment):
                return False
        return True

    def get_remote_sale(self, external_id):
        return self.remote_sales.get(external_id)

    def check_sale_changed(self, local_sale, remote_sale):
        return local_sale == remote_sale

    def check_sale_item_changed(self, local_sale_item, remote_sale_item):
        return local_sale_item == remote_sale_item

    def check_sale_sale_payment_changed(self, local_payment, remote_payment):
        return local_payment == remote_payment


class EnkoRequests(object):

    BASE_URL = "https://reporter.enko.com.br"
    CHECK_SALES = BASE_URL + "/etl/import/check/sales/"
    CHECK_SALE_ITEMS = BASE_URL + "/etl/sale/%s/items/"
    CHECK_SALE_PAYMENTS = BASE_URL + "/etl/sale/%s/payments/"
    SEND_SALES = BASE_URL + "/etl/import/"
    TOKEN = os.getenv("ENKO_TOKEN")

    def get_all_sales_by_date(self, ids,  date):
        ids = ','.join(ids)
        req = requests.post(self.CHECK_SALES, json={"ids": ids, "start_date": date, "end_date": date,
                                                    "token": self.TOKEN})
        req.raise_for_status()
        return req.json()

    def get_all_sales_items_by_sale(self, sale_id):
        url = self.CHECK_SALE_ITEMS % sale_id
        req = requests.get(url, params={"token": self.TOKEN})
        req.raise_for_status()
        return req.json()

    def get_all_sale_payments_by_sale(self, sale_id):
        url = self.CHECK_SALE_PAYMENTS % sale_id
        req = requests.post(url, params={"token": self.TOKEN})
        req.raise_for_status()
        return req.json()

    def send_sales_by_date(self, sales_info, date):
        print json.dumps(sales_info)
        out = StringIO.StringIO()
        with gzip.GzipFile(fileobj=out, mode="w") as f:
            f.write(json.dumps(sales_info))
        files = {'file': ('isilist', out.getvalue())}
        payload = {'token': self.TOKEN, 'date': date}
        req = requests.post(self.SEND_SALES, files=files, data=payload)
        req.raise_for_status()

        return req.content
