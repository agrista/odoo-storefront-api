# -*- coding: utf-8 -*-
# Copyright 2023 ODOOGAP/PROMPTEQUATION LDA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import uuid
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    storefront_debug_mode = fields.Boolean('Debug Mode')
    storefront_payment_success_return_url = fields.Char(
        'Payment Success Return Url', related='website_id.storefront_payment_success_return_url', readonly=False,
        required=True
    )
    storefront_payment_error_return_url = fields.Char(
        'Payment Error Return Url', related='website_id.storefront_payment_error_return_url', readonly=False,
        required=True
    )
    storefront_cache_invalidation_key = fields.Char('Cache Invalidation Key', required=True)
    storefront_cache_invalidation_url = fields.Char('Cache Invalidation Url', required=True)
    storefront_mailing_list_id = fields.Many2one('mailing.list', 'Newsletter', domain=[('is_public', '=', True)],
                                          related='website_id.storefront_mailing_list_id', readonly=False, required=True)

    # Storefront Images
    storefront_image_quality = fields.Integer('Quality', required=True)
    storefront_image_background_rgba = fields.Char('Background RGBA', required=True)
    storefront_image_resize_limit = fields.Integer('Resize Limit', required=True,
                                            help='Limit in pixels to resize image for width and height')

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        res.update(
            storefront_debug_mode=ICP.get_param('storefront_debug_mode'),
            storefront_cache_invalidation_key=ICP.get_param('storefront_cache_invalidation_key'),
            storefront_cache_invalidation_url=ICP.get_param('storefront_cache_invalidation_url'),
            storefront_image_quality=int(ICP.get_param('storefront_image_quality', 100)),
            storefront_image_background_rgba=ICP.get_param('storefront_image_background_rgba', '(255, 255, 255, 255)'),
            storefront_image_resize_limit=int(ICP.get_param('storefront_image_resize_limit', 1920)),
        )
        return res

    def set_values(self):
        if self.storefront_image_quality < 0 or self.storefront_image_quality > 100:
            raise ValidationError(_('Invalid image quality percentage.'))

        if self.storefront_image_resize_limit < 0:
            raise ValidationError(_('Invalid image resize limit.'))

        super(ResConfigSettings, self).set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('storefront_debug_mode', self.storefront_debug_mode)
        ICP.set_param('storefront_cache_invalidation_key', self.storefront_cache_invalidation_key)
        ICP.set_param('storefront_cache_invalidation_url', self.storefront_cache_invalidation_url)
        ICP.set_param('storefront_image_quality', self.storefront_image_quality)
        ICP.set_param('storefront_image_background_rgba', self.storefront_image_background_rgba)
        ICP.set_param('storefront_image_resize_limit', self.storefront_image_resize_limit)

    @api.model
    def create_storefront_cache_invalidation_key(self):
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('storefront_cache_invalidation_key', str(uuid.uuid4()))
