# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re
import smtplib
import sys
import base64
import ssl
import idna
import copy

from OpenSSL import crypto as SSLCrypto
from OpenSSL.crypto import Error as SSLCryptoError, FILETYPE_PEM
from OpenSSL.SSL import Context as SSLContext, Error as SSLError

from odoo import api, models, _, tools
from odoo.addons.base.models.ir_mail_server import is_ascii, ustr, MailDeliveryException, SMTP_TIMEOUT
from odoo.exceptions import UserError
from odoo.addons.bhs_aws_ses_mail_tracking.libs import smtplib_inherit

_logger = logging.getLogger(__name__)
_test_logger = logging.getLogger('odoo.tests')


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    def connect(self, host=None, port=None, user=None, password=None, encryption=None,
                smtp_from=None, ssl_certificate=None, ssl_private_key=None, smtp_debug=False, mail_server_id=None,
                allow_archived=False):
        """Override the connect method to integrate new SMTP class"""

        # Do not actually connect while running in test mode
        if self._is_test_mode():
            return

        mail_server = smtp_encryption = None
        if mail_server_id:
            mail_server = self.sudo().browse(mail_server_id)
            if not allow_archived and not mail_server.active:
                raise UserError(_('The server "%s" cannot be used because it is archived.', mail_server.display_name))
        elif not host:
            mail_server, smtp_from = self.sudo()._find_mail_server(smtp_from)

        if not mail_server:
            mail_server = self.env['ir.mail_server']
        ssl_context = None

        if mail_server and mail_server.smtp_authentication != "cli":
            smtp_server = mail_server.smtp_host
            smtp_port = mail_server.smtp_port
            if mail_server.smtp_authentication == "certificate":
                smtp_user = None
                smtp_password = None
            else:
                smtp_user = mail_server.smtp_user
                smtp_password = mail_server.smtp_pass
            smtp_encryption = mail_server.smtp_encryption
            smtp_debug = smtp_debug or mail_server.smtp_debug
            from_filter = mail_server.from_filter
            if (mail_server.smtp_authentication == "certificate"
               and mail_server.smtp_ssl_certificate
               and mail_server.smtp_ssl_private_key):
                try:
                    ssl_context = SSLContext(ssl.PROTOCOL_TLS)
                    smtp_ssl_certificate = base64.b64decode(mail_server.smtp_ssl_certificate)
                    certificate = SSLCrypto.load_certificate(FILETYPE_PEM, smtp_ssl_certificate)
                    smtp_ssl_private_key = base64.b64decode(mail_server.smtp_ssl_private_key)
                    private_key = SSLCrypto.load_privatekey(FILETYPE_PEM, smtp_ssl_private_key)
                    ssl_context.use_certificate(certificate)
                    ssl_context.use_privatekey(private_key)
                    # Check that the private key match the certificate
                    ssl_context.check_privatekey()
                except SSLCryptoError as e:
                    raise UserError(_('The private key or the certificate is not a valid file. \n%s', str(e)))
                except SSLError as e:
                    raise UserError(_('Could not load your certificate / private key. \n%s', str(e)))

        else:
            # we were passed individual smtp parameters or nothing and there is no default server
            smtp_server = host or tools.config.get('smtp_server')
            smtp_port = tools.config.get('smtp_port', 25) if port is None else port
            smtp_user = user or tools.config.get('smtp_user')
            smtp_password = password or tools.config.get('smtp_password')
            if mail_server:
                from_filter = mail_server.from_filter
            else:
                from_filter = self.env['ir.mail_server']._get_default_from_filter()

            smtp_encryption = encryption
            if smtp_encryption is None and tools.config.get('smtp_ssl'):
                smtp_encryption = 'starttls' # smtp_ssl => STARTTLS as of v7
            smtp_ssl_certificate_filename = ssl_certificate or tools.config.get('smtp_ssl_certificate_filename')
            smtp_ssl_private_key_filename = ssl_private_key or tools.config.get('smtp_ssl_private_key_filename')

            if smtp_ssl_certificate_filename and smtp_ssl_private_key_filename:
                try:
                    ssl_context = SSLContext(ssl.PROTOCOL_TLS)
                    ssl_context.use_certificate_chain_file(smtp_ssl_certificate_filename)
                    ssl_context.use_privatekey_file(smtp_ssl_private_key_filename)
                    # Check that the private key match the certificate
                    ssl_context.check_privatekey()
                except SSLCryptoError as e:
                    raise UserError(_('The private key or the certificate is not a valid file. \n%s', str(e)))
                except SSLError as e:
                    raise UserError(_('Could not load your certificate / private key. \n%s', str(e)))

        if not smtp_server:
            raise UserError(
                (_("Missing SMTP Server") + "\n" +
                 _("Please define at least one SMTP server, "
                   "or provide the SMTP parameters explicitly.")))

        if smtp_encryption == 'ssl':
            if 'SMTP_SSL' not in smtplib.__all__:
                raise UserError(
                    _("Your Odoo Server does not support SMTP-over-SSL. "
                      "You could use STARTTLS instead. "
                       "If SSL is needed, an upgrade to Python 2.6 on the server-side "
                       "should do the trick."))
            connection = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=SMTP_TIMEOUT)
        else:
            # Change here: use smtplib_inherit for BHSoft
            connection = smtplib_inherit.SMTPInherit(smtp_server, smtp_port, timeout=SMTP_TIMEOUT)
            #####

        connection.set_debuglevel(smtp_debug)
        if smtp_encryption == 'starttls':
            # starttls() will perform ehlo() if needed first
            # and will discard the previous list of services
            # after successfully performing STARTTLS command,
            # (as per RFC 3207) so for example any AUTH
            # capability that appears only on encrypted channels
            # will be correctly detected for next step
            connection.starttls(context=ssl_context)

        if smtp_user:
            # Attempt authentication - will raise if AUTH service not supported
            local, at, domain = smtp_user.rpartition('@')
            if at:
                smtp_user = local + at + idna.encode(domain).decode('ascii')
            mail_server._smtp_login(connection, smtp_user, smtp_password or '')

        # Some methods of SMTP don't check whether EHLO/HELO was sent.
        # Anyway, as it may have been sent by login(), all subsequent usages should consider this command as sent.
        connection.ehlo_or_helo_if_needed()

        # Store the "from_filter" of the mail server / odoo-bin argument to  know if we
        # need to change the FROM headers or not when we will prepare the mail message
        connection.from_filter = from_filter
        connection.smtp_from = smtp_from

        return connection

    @api.model
    def send_email(self, message, mail_server_id=None, smtp_server=None, smtp_port=None,
                   smtp_user=None, smtp_password=None, smtp_encryption=None,
                   smtp_ssl_certificate=None, smtp_ssl_private_key=None,
                   smtp_debug=False, smtp_session=None):
        """Rewrite send_mail method to change message_id"""

        smtp = smtp_session
        if not smtp:
            smtp = self.connect(
                smtp_server, smtp_port, smtp_user, smtp_password, smtp_encryption,
                smtp_from=message['From'], ssl_certificate=smtp_ssl_certificate, ssl_private_key=smtp_ssl_private_key,
                smtp_debug=smtp_debug, mail_server_id=mail_server_id,)

        smtp_from, smtp_to_list, message = self._prepare_email_message(message, smtp)

        # Do not actually send emails in testing mode!
        if self._is_test_mode():
            _test_logger.info("skip sending email in test mode")
            return message['Message-Id']

        try:
            message_id = message['Message-Id']

            if sys.version_info < (3, 7, 4):
                # header folding code is buggy and adds redundant carriage
                # returns, it got fixed in 3.7.4 thanks to bpo-34424
                message_str = message.as_string()
                message_str = re.sub('\r+(?!\n)', '', message_str)

                mail_options = []
                if any((not is_ascii(addr) for addr in smtp_to_list + [smtp_from])):
                    # non ascii email found, require SMTPUTF8 extension,
                    # the relay may reject it
                    mail_options.append("SMTPUTF8")
                smtp.sendmail(smtp_from, smtp_to_list, message_str, mail_options=mail_options)
            else:
                resp = smtp.send_message(message, smtp_from, smtp_to_list)
                # Change here: Update SES Message-ID
                host_split = smtp._host.split(".")
                (region, domain) = host_split[1], f"{host_split[2]}.{host_split[3]}"
                if domain == "amazonaws.com":
                    ses_message_id = f"<{resp.decode().split(' ')[1]}@{region}.amazonses.com>"
                    trace = self.env['mailing.trace'].search([('message_id', '=', message_id)])
                    if trace:
                        trace[0].ses_message_id = ses_message_id
                #####

            # do not quit() a pre-established smtp_session
            if not smtp_session:
                smtp.quit()
        except smtplib.SMTPServerDisconnected:
            raise
        except Exception as e:
            params = (ustr(smtp_server), e.__class__.__name__, ustr(e))
            msg = _("Mail delivery failed via SMTP server '%s'.\n%s: %s", *params)
            _logger.info(msg)
            raise MailDeliveryException(_("Mail Delivery Failed"), msg)
        return message_id
