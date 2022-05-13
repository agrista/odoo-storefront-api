# -*- coding: utf-8 -*-
# Copyright 2022 ODOOGAP/PROMPTEQUATION LDA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import graphene
from graphql import GraphQLError
from odoo.http import request
from odoo import _
from odoo.osv import expression

from odoo.addons.graphql_vuestorefront.schemas.objects import (
    SortEnum, Product, Attribute, AttributeValue
)


def get_search_order(sort):
    sorting = ''
    for field, val in sort.items():
        if sorting:
            sorting += ', '
        if field == 'price':
            sorting += 'list_price %s' % val.value
        else:
            sorting += '%s %s' % (field, val.value)

    # Add id as last factor so we can consistently get the same results
    if sorting:
        sorting += ', id ASC'
    else:
        sorting = 'id ASC'

    return sorting


def get_search_domain(env, search, **kwargs):
    # Only get published products
    domains = [env['website'].get_current_website().sale_product_domain()]

    # Filter with ids
    if kwargs.get('ids', False):
        domains.append([('id', 'in', kwargs['ids'])])

    # Filter with Category ID
    if kwargs.get('category_id', False):
        domains.append([('public_categ_ids', 'child_of', kwargs['category_id'])])

    # Deprecated: Filter with Attribute Value
    if kwargs.get('attribute_value_id', False):
        domains.append([('attribute_line_ids.value_ids', 'in', kwargs['attribute_value_id'])])

    # Filter with Attribute Value
    if kwargs.get('attrib_values', False):
        attrib = None
        ids = []
        for value in kwargs['attrib_values']:
            try:
                value = value.split('-')
                if len(value) != 2:
                    continue

                attribute_id = int(value[0])
                attribute_value_id = int(value[1])
            except ValueError:
                continue

            if not attrib:
                attrib = attribute_id
                ids.append(attribute_value_id)
            elif attribute_id == attrib:
                ids.append(attribute_value_id)
            else:
                domains.append([('attribute_line_ids.value_ids', 'in', ids)])
                attrib = attribute_id
                ids = [attribute_value_id]
        if attrib:
            domains.append([('attribute_line_ids.value_ids', 'in', ids)])

    # Filter With Name
    if kwargs.get('name', False):
        name = kwargs['name']
        for n in name.split(" "):
            domains.append([('name', 'ilike', n)])

    if search:
        for srch in search.split(" "):
            domains.append([
                '|', '|', ('name', 'ilike', srch), ('description_sale', 'like', srch), ('default_code', 'like', srch)])

    # Product Price Filter
    if kwargs.get('min_price', False):
        domains.append([('list_price', '>=', float(kwargs['min_price']))])
    if kwargs.get('max_price', False):
        domains.append([('list_price', '<=', float(kwargs['max_price']))])

    return expression.AND(domains)


def get_product_list(env, current_page, page_size, search, sort, **kwargs):
    Product = env['product.template'].sudo()
    domain = get_search_domain(env, search, **kwargs)
    # First offset is 0 but first page is 1
    if current_page > 1:
        offset = (current_page - 1) * page_size
    else:
        offset = 0
    order = get_search_order(sort)
    products = Product.search(domain, order=order)
    attribute_values = products.mapped('public_categ_ids').mapped('attribute_value_ids')
    total_count = len(products)
    products = products[offset:offset + page_size]
    return products, total_count, attribute_values


class Products(graphene.Interface):
    products = graphene.List(Product)
    total_count = graphene.Int(required=True)
    attribute_values = graphene.List(AttributeValue)


class ProductList(graphene.ObjectType):
    class Meta:
        interfaces = (Products,)


class ProductFilterInput(graphene.InputObjectType):
    ids = graphene.List(graphene.Int)
    category_id = graphene.List(graphene.Int)
    # Deprecated
    attribute_value_id = graphene.List(graphene.Int)
    attrib_values = graphene.List(graphene.String)
    name = graphene.String()
    min_price = graphene.Float()
    max_price = graphene.Float()


class ProductSortInput(graphene.InputObjectType):
    id = SortEnum()
    name = SortEnum()
    price = SortEnum()


class ProductQuery(graphene.ObjectType):
    product = graphene.Field(
        Product,
        id=graphene.Int(default_value=None),
        barcode=graphene.String(default_value=None),
    )
    products = graphene.Field(
        Products,
        filter=graphene.Argument(ProductFilterInput, default_value={}),
        current_page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=20),
        search=graphene.String(default_value=False),
        sort=graphene.Argument(ProductSortInput, default_value={})
    )
    attribute = graphene.Field(
        Attribute,
        required=True,
        id=graphene.Int(),
    )

    @staticmethod
    def resolve_product(self, info, id=None, barcode=None):
        env = info.context["env"]

        if id:
            product = env["product.template"].sudo().search([('id', '=', id)], limit=1)
        elif barcode:
            product = env["product.template"].sudo().search([('barcode', '=', barcode)], limit=1)
        else:
            product = None

        website = env['website'].get_current_website()
        request.website = website

        if not product:
            raise GraphQLError(_('Product does not exist.'))
        return product

    @staticmethod
    def resolve_products(self, info, filter, current_page, page_size, search, sort):
        env = info.context["env"]
        products, total_count, attribute_values = get_product_list(env, current_page, page_size, search, sort, **filter)
        return ProductList(products=products, total_count=total_count, attribute_values=attribute_values)

    @staticmethod
    def resolve_attribute(self, info, id):
        attribute = info.context["env"]["product.attribute"].search([('id', '=', id)], limit=1)
        if not attribute:
            raise GraphQLError(_('Attribute does not exist.'))
        return attribute
