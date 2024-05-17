# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, Command


class Followers(models.Model):
    _inherit = 'mail.followers'

    @api.model_create_multi
    def create(self, vals_list):
        record_tracking_reply_id = self.env.ref('bhs_aws_ses_mail_tracking.tracking_mailing').id
        domain = f"not (val['res_id'] == {record_tracking_reply_id} and val['res_model'] == 'mailing.mailing')"
        vals_list = list(filter(lambda val: eval(domain), vals_list))
        return super(Followers, self).create(vals_list)
