# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint

from odoo import _, fields, models
from odoo.exceptions import UserError

from .agrista_request import AgristaAPI

_logger = logging.getLogger(__name__)


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    agrista_profile = fields.Char(
        string="Agrista Profile ID",
        help="The unique reference for the partner/token combination in the Agrista backend.")
    agrista_payment_method_type = fields.Selection(
        string="Agrista Payment Type",
        help="The type of payment method this token is linked to.",
        selection=[("credit_card", "Credit Card"), ("bank_account", "Bank Account (USA Only)")],
    )
