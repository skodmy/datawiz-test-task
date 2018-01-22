"""
Contains statistics computations routines.
"""
from functools import lru_cache
from decimal import Decimal
from collections import defaultdict
from typing import Dict, DefaultDict, List, Callable, Union

from pandas import DataFrame

from dwapi.datawiz import DW

from .mathematics import difference


def compute_sales_general_stats(products_sales_data: DataFrame) -> Dict[str, float]:
    """
    Computes sales general statistics.

    :param products_sales_data: a DataFrame object which contains products sales data.
    :return: a dictionary which contains sales general statistics.
    """
    sales_gen_stats = {
        'products_turnover': products_sales_data['turnover'].sum(),
        'products_qty': products_sales_data['qty'].sum(),
        'receipts_qty': products_sales_data['receipts_qty'].sum(),
    }

    sales_gen_stats['mean_receipt'] = sales_gen_stats['products_turnover'] / sales_gen_stats['receipts_qty']
    # wrapping every numeric(actually float) value with Decimal to avoid precision surprises
    for attr_key in sales_gen_stats:
        sales_gen_stats[attr_key] = Decimal("%.2f" % sales_gen_stats[attr_key])

    sales_gen_stats['date'] = products_sales_data['date'].unique()[0]  # not good enough solution

    return sales_gen_stats


def compute_sales_general_stats_diff(x_sls_gen_stats: dict, y_sls_gen_stats: dict, include_stats: bool=True) -> Dict:
    """
    Computes sales general statistics differences.

    :param x_sls_gen_stats: a dictionary with sales general statistics which will be used as comparison's sample.
    :param y_sls_gen_stats: ... - comparison's object.
    :param include_stats: a boolean flag which indicates to include stats for which difference where computed or not.
    :return: a dictionary which contains sales general statistics differences.
    """
    sales_gen_stats_diff = {
        stat: difference(x_sls_gen_stats.get(stat, 0.0), y_sls_gen_stats.get(stat, 0.0))
        for stat in y_sls_gen_stats
        if stat != 'date'
    }
    if include_stats:
        sales_gen_stats_diff['x'] = x_sls_gen_stats
        sales_gen_stats_diff['y'] = y_sls_gen_stats
    return sales_gen_stats_diff


def compute_sales_per_product_stats(products_sales_data: DataFrame) -> DefaultDict[str, float]:
    """
    Computes sales per product statistics.

    :param products_sales_data: a DataFrame instance with products sales data.
    :return: a dictionary which contains sales per product statistics.
    """
    sales_per_product_stats = defaultdict(lambda: {'id': -1, 'quantity': 0, 'turnover': 0})
    for product_id in products_sales_data['product'].unique():
        product_loc = products_sales_data.loc[products_sales_data['product'] == product_id]
        sales_per_product_stats[product_id] = {
            'name': product_loc['name'],
            'quantity': product_loc['qty'].sum(),
            'turnover': product_loc['turnover'].sum(),
        }
    return sales_per_product_stats


def compute_sales_per_product_stats_diff(x_sls_pprod_stats: DefaultDict, y_sls_pprod_stats: DefaultDict) -> List[Dict]:
    """
    Computes sales per product statistics differences.

    :param x_sls_pprod_stats: a defaultdict instance with sales per product statistics which is comparison's sample.
    :param y_sls_pprod_stats: ... - comparison's object.
    :return: a list of dictionaries with sales per product statistics differences.
    """
    return [
        {
            'id': product_id,
            'name': sales_product_stats['name'].unique()[0].split('|')[0].strip(),  # also not good enough solution
            'qty': sales_product_stats['quantity'] - x_sls_pprod_stats[product_id]['quantity'],
            'turnover': sales_product_stats['turnover'] - x_sls_pprod_stats[product_id]['turnover'],
        }
        for product_id, sales_product_stats in y_sls_pprod_stats.items()
    ]


def compute_sales_all_stats(products_sales: DataFrame, stats_comp_func: Callable=compute_sales_general_stats) -> List:
    """
    Computes all products sales statistics by using statistics computation function.

    IT'S BETTER TO TURN THIS INTO GENERATOR-FUNCTION TO SAVE MEMORY, BUT LATER DIFFS COMPUTATION REQUIRES A LIST =)

    :param products_sales: a DataFrame instance with products sales data.
    :param stats_comp_func: a callable which will be used to compute statistics.
    :return: a list with all computed statistics.
    """
    return [
        stats_comp_func(
            products_sales.loc[products_sales['date'] == date_]
        )
        for date_ in products_sales['date'].unique()
    ]


def compute_sales_all_stats_diffs(all_stats: List, stats_diff_comp_func: Callable=compute_sales_general_stats_diff):
    """
    Computes all product sales statistics differences by using statistics difference computation function.

    IT'S BETTER TO TURN THIS INTO GENERATOR-FUNCTION TO SAVE MEMORY, BUT LATER PAGINATION REQUIRES LIST.

    :param all_stats: a list of all sales statistics dictionaries.
    :param stats_diff_comp_func: a callable which will be used to compute statistics difference.
    :return: a list of all statistics differences.
    """
    return [
        stats_diff_comp_func(all_stats[index], all_stats[index + 1]) for index in range(len(all_stats) - 1)
    ]


def group_per_product_sales_stats(data: List[Dict[str, Union[float, Decimal]]], by="all"):
    """
    Groups per product sales statistics by income character.

    if by value was not recognized then returns all "possible" groups.

    :param data: a list with per product sales statistics data.
    :param by: a string that represents income character, can be 'grown' or 'fell'.
    :return: group or groups with per products sales statistics data(actually filter objects).
    """
    by_mapping = {
        "grown": lambda: filter(lambda stat: stat['qty'] > 0, data),
        "fell": lambda: filter(lambda stat: stat['qty'] <= 0, data),
    }
    if by not in by_mapping:
        return [by_mapping[by_key]() for by_key in by_mapping]
    return by_mapping[by]()


@lru_cache(maxsize=50)  # calls cache, django caching can be used for templates parts caching
def compute_products_sales_statistics(dw: DW, from_date: str, to_date: str, incl_per_prod: bool=False):
    """
    Computes products sales statistics.

    if incl_per_prod is true then returns per product sales statistics too else returns only general sales statistics.

    :param dw: datawiz api instance that will be used for grabbing sales data.
    :param from_date: a string that represents date in format 'yyyy-mm-dd' from which to start grabbing data.
    :param to_date:  a string that represents date in format 'yyyy-mm-dd' which indicates when to stop grabbing data.
    :param incl_per_prod: a boolean flag indicating to include per product sales statistics or not.
    :return: general statistics or tuple(general statistics, per product statistics).
    """
    products_sales = dw.get_products_sale(
        date_from=from_date,
        date_to=to_date,
        by=['turnover', 'qty', 'receipts_qty'],
        view_type='raw',
    )
    general_sales_stats = compute_sales_all_stats_diffs(compute_sales_all_stats(products_sales))

    if incl_per_prod:
        per_prod_sales_stats = compute_sales_all_stats_diffs(
            compute_sales_all_stats(
                products_sales,
                compute_sales_per_product_stats
            ),
            compute_sales_per_product_stats_diff
        )
        return general_sales_stats, per_prod_sales_stats

    return general_sales_stats
