# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint

from odoo import _, api, fields, models
from odoo.fields import Command
from odoo.exceptions import UserError, ValidationError

from .agrista_request import AgristaAPI

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('agrista', 'Agrista')], ondelete={'agrista': 'set default'})
    agrista_login = fields.Char(
        string="API Login ID", help="The ID solely used to identify the account with Agrista",
        required_if_provider='agrista')
    agrista_transaction_key = fields.Char(
        string="API Transaction Key", required_if_provider='agrista', groups='base.group_system')
    agrista_signature_key = fields.Char(
        string="API Signature Key", required_if_provider='agrista', groups='base.group_system')
    agrista_client_key = fields.Char(
        string="API Client Key",
        help="The public client key. To generate directly from Odoo or from Agrista backend.")
    # Authorize.Net supports only one currency: "One gateway account is required for each currency"
    # See https://community.developer.authorize.net/t5/The-Authorize-Net-Developer-Blog/Authorize-Net-UK-Europe-Update/ba-p/35957
    agrista_currency_id = fields.Many2one(
        string="Agrista Currency", comodel_name='res.currency')
    agrista_payment_method_type = fields.Selection(
        string="Allow Payments From",
        help="Determines with what payment method the customer can pay.",
        selection=[('credit_card', "Credit Card"), ('bank_account', "Bank Account (USA Only)")],
        default='credit_card',
        required_if_provider='agrista',
    )

    # === CONSTRAINT METHODS ===#

    @api.constrains('agrista_payment_method_type')
    def _check_payment_method_type(self):
        for provider in self.filtered(lambda p: p.code == "agrista"):
            if self.env['payment.token'].search([('provider_id', '=', provider.id)], limit=1):
                raise ValidationError(_(
                    "There are active tokens linked to this provider. To change the payment method "
                    "type, please disable the provider and duplicate it. Then, change the payment "
                    "method type on the duplicated provider."
                ))

    #=== COMPUTE METHODS ===#

    def _compute_feature_support_fields(self):
        """ Override of `payment` to enable additional features. """
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == 'agrista').update({
            'support_manual_capture': 'full_only',
            'support_refund': 'full_only',
            'support_tokenization': True,
        })

    # === ONCHANGE METHODS ===#

    @api.onchange('agrista_payment_method_type')
    def _onchange_agrista_payment_method_type(self):
        if self.agrista_payment_method_type == 'bank_account':
            self.display_as = _("Bank (powered by Authorize)")
            self.payment_method_ids = [Command.clear()]
        else:
            self.display_as = _("Credit Card (powered by Authorize)")
            self.payment_method_ids = [Command.set([self.env.ref(pm_xml_id).id for pm_xml_id in (
                'payment.payment_method_maestro',
                'payment.payment_method_mastercard',
                'payment.payment_method_discover',
                'payment.payment_method_diners_club_intl',
                'payment.payment_method_jcb',
                'payment.payment_method_visa',
            )])]

    # === ACTION METHODS ===#

    def action_update_merchant_details(self):
        """ Fetch the merchant details to update the client key and the account currency. """
        self.ensure_one()

        if self.state == 'disabled':
            raise UserError(_("This action cannot be performed while the provider is disabled."))

        agrista_api = AgristaAPI(self)

        # Validate the API Login ID and Transaction Key
        res_content = agrista_api.test_authenticate()
        _logger.info("test_authenticate request response:\n%s", pprint.pformat(res_content))
        if res_content.get('err_msg'):
            raise UserError(_("Failed to authenticate.\n%s", res_content['err_msg']))

        # Update the merchant details
        res_content = agrista_api.merchant_details()
        _logger.info("merchant_details request response:\n%s", pprint.pformat(res_content))
        if res_content.get('err_msg'):
            raise UserError(_("Could not fetch merchant details:\n%s", res_content['err_msg']))

        currency = self.env['res.currency'].search([('name', 'in', res_content.get('currencies'))])
        self.available_currency_ids = [Command.set(currency.ids)]
        self.agrista_client_key = res_content.get('publicClientKey')

    # === BUSINESS METHODS ===#

    def _get_validation_amount(self):
        """ Override of payment to return the amount for Agrista validation operations.

        :return: The validation amount
        :rtype: float
        """
        res = super()._get_validation_amount()
        if self.code != 'agrista':
            return res

        return 0.01

    def _get_validation_currency(self):
        """ Override of payment to return the currency for Agrista validation operations.

        :return: The validation currency
        :rtype: recordset of `res.currency`
        """
        res = super()._get_validation_currency()
        if self.code != 'agrista':
            return res

        return self.available_currency_ids[0]
