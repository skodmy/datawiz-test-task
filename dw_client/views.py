from django.shortcuts import render, redirect
from django.forms import ValidationError
from django.core.paginator import Paginator

from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from dwapi.datawiz import DW

from .decorators import dw_auth_required
from .forms import AuthorizationForm, SalesForm
from .statscomps import compute_products_sales_statistics, group_per_product_sales_stats


def clear_session_data(request):
    session = getattr(request, 'session', None)
    if session:
        session.clear()


def sign_in(request):
    # check if already signed in
    if getattr(request, 'dw', None):
        return redirect('dw-client:profile:info')
    # validating data
    form = AuthorizationForm(data=request.POST)
    try:
        if form.is_valid():
            form.clean()
        else:
            raise ValidationError(form.errors)
    except ValidationError as e:
        return render(request, 'dw_client/auth/sign/in.html', {'form': AuthorizationForm(), 'errors': e.messages})
    else:
        request.session['dw_api_key'] = form.cleaned_data['key']
        request.session['dw_api_secret'] = form.cleaned_data['secret']
        try:
            # checking if such combination exists
            DW(request.session['dw_api_key'], request.session['dw_api_secret'])
        except InvalidGrantError:
            # if not exists clearing session data associated with it and returning to sign in
            clear_session_data(request)
            return render(request, 'dw_client/auth/sign/in.html', )
        # else go to profile/info page
        return redirect('dw-client:profile:info')


@dw_auth_required()
def index(request):
    return render(request, 'dw_client/index.html')


@dw_auth_required()
def profile_info(request):
    return render(request, 'dw_client/profile/info.html')


@dw_auth_required()
def sign_out(request):
    if hasattr(request, 'dw'):
        delattr(request, 'dw')
    clear_session_data(request)
    return redirect('dw-client:auth:sign:in')


@dw_auth_required()
def stats_page(request):
    return render(request, 'dw_client/sales/stats_page.html', {'form': SalesForm(), })


@dw_auth_required()
def sales_statistics(request, date_from, date_to, page_number=1):
    if request.is_ajax():
        # getting products sales statistics
        gen_sales_stats, per_prod_sales_stats = compute_products_sales_statistics(
            request.dw,
            date_from,
            date_to,
            incl_per_prod=True
        )
        # paginating them
        gen_sales_stats_paginator = Paginator(gen_sales_stats, 1)
        per_prod_sales_stats_paginator = Paginator(per_prod_sales_stats, 1)
        # grouping per product sales statistics by income character
        prods_grown_in_sales_stats_group, prods_fell_in_sales_stats_group = group_per_product_sales_stats(
            per_prod_sales_stats_paginator.get_page(page_number).object_list[0]
            if page_number in per_prod_sales_stats_paginator.page_range and per_prod_sales_stats_paginator.count != 0
            else []
        )
        # rendering tables with gathered statistics data
        return render(
            request,
            'dw_client/sales/statistics.html',
            {
                'active_page_number': page_number,
                'page_numbers': list(gen_sales_stats_paginator.page_range),
                'gen_page': gen_sales_stats_paginator.get_page(page_number).object_list
                if page_number in gen_sales_stats_paginator.page_range
                else [],
                'per_prod_sales_stats_page': {
                    'grown_group': prods_grown_in_sales_stats_group,
                    'fell_group': prods_fell_in_sales_stats_group,
                }
            }
        )
    return redirect('dw-client:sales:stats-page')
