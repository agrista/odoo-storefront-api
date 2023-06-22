# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint

from odoo import _, http
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.payment import utils as payment_utils

_logger = logging.getLogger(__name__)


class AgristaController(http.Controller):

    _webhook_url = '/payment/agrista/notification'

    @http.route('/payment/agrista/get_provider_info', type='json', auth='public')
    def agrista_get_provider_info(self, provider_id):
        """ Return public information on the provider.

        :param int provider_id: The provider handling the transaction, as a `payment.provider` id
        :return: Information on the provider, namely: the state, payment method type, login ID, and
                 public client key
        :rtype: dict
        """
        provider_sudo = request.env['payment.provider'].sudo().browse(provider_id).exists()
        return {
            'state': provider_sudo.state,
            'payment_method_type': provider_sudo.agrista_payment_method_type,
            # The public API key solely used to identify the seller account with Agrista
            'login_id': provider_sudo.agrista_login,
            # The public client key solely used to identify requests from the Accept.js suite
            'client_key': provider_sudo.agrista_client_key,
        }

    @http.route('/payment/agrista/payment', type='json', auth='public')
    def agrista_payment(self, reference, partner_id, access_token, opaque_data):
        """ Make a payment request and handle the response.

        :param str reference: The reference of the transaction
        :param int partner_id: The partner making the transaction, as a `res.partner` id
        :param str access_token: The access token used to verify the provided values
        :param dict opaque_data: The payment details obfuscated by Agrista
        :return: None
        """
        # Check that the transaction details have not been altered
        if not payment_utils.check_access_token(access_token, reference, partner_id):
            raise ValidationError("Agrista: " + _("Received tampered payment request data."))

        # Make the payment request to Agrista
        tx_sudo = request.env['payment.transaction'].sudo().search([('reference', '=', reference)])
        response_content = tx_sudo._agrista_create_transaction_request(opaque_data)

        # Handle the payment request response
        _logger.info(
            "payment request response for transaction with reference %s:\n%s",
            reference, pprint.pformat(response_content)
        )
        tx_sudo._handle_notification_data('agrista', {'response': response_content})
