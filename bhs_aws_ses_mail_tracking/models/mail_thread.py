import logging
import re
import html

from odoo import api, models, tools, fields

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def _message_route_process(self, message, message_dict, routes):
        """ Override to update the parent mailing traces. The parent is found
        by using the References header of the incoming message and looking for
        matching message_id in mailing.trace. """
        if routes:
            # even if 'reply_to' in ref (cfr mail/mail_thread) that indicates a new thread redirection
            # (aka bypass alias configuration in gateway) consider it as a reply for statistics purpose
            thread_references = message_dict['references'] or message_dict['in_reply_to']
            msg_references = tools.mail_header_msgid_re.findall(thread_references)
            if msg_references:
                self.env['mailing.trace'].set_opened(domain=[('message_id', 'in', msg_references)])
                self.env['mailing.trace'].set_replied(domain=[('message_id', 'in', msg_references)])

            # change start here
            traces = self.env['mailing.trace'].search([('message_id', 'in', msg_references)])
            if not traces:
                self.env['mailing.trace'].set_opened(domain=[('ses_message_id', 'in', msg_references)])
                self.env['mailing.trace'].set_replied(domain=[('ses_message_id', 'in', msg_references)])
            # change end here

        return super(MailThread, self)._message_route_process(message, message_dict, routes)

    @api.model
    def _routing_handle_bounce(self, email_message, message_dict):
        """Override _routing_handle_bounce method to process if send mail with SES, message_id had been changed"""

        super(MailThread, self)._routing_handle_bounce(email_message, message_dict)

        bounced_msg_ids = message_dict['bounced_msg_ids']
        traces_by_message_id = self.env['mailing.trace'].search([('message_id', 'in', bounced_msg_ids)])
        if bounced_msg_ids and not traces_by_message_id:
            self.env['mailing.trace'].set_bounced(
                domain=[('ses_message_id', 'in', bounced_msg_ids)],
                bounce_message=tools.html2plaintext(message_dict.get('body') or '')
            )
