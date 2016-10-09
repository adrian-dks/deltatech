# -*- coding: utf-8 -*-



from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang

from odoo.exceptions import UserError, RedirectWarning, ValidationError

import odoo.addons.decimal_precision as dp




class AccountInvoice(models.Model):
    _inherit = "account.invoice"


    invoice_line = fields.One2many('account.invoice.line', related="invoice_line_ids")
    payment_term = fields.Many2one('account.payment.term', related='payment_term_id')
    fiscal_position = fields.Many2one('account.fiscal.position', related='fiscal_position_id')
    tax_line = fields.One2many('account.invoice.tax', related="tax_line_ids" )


    internal_number = fields.Char(string='Invoice Number', readonly=True,
                              default=False, copy=False,
                              help="Unique number of the invoice, computed automatically when the invoice is created.")


    @api.multi
    def action_number(self):
        # TODO: not correct fix but required a fresh values before reading it.
        self.write({})

        for inv in self:
            self.write({'internal_number': inv.number})

            if inv.type in ('in_invoice', 'in_refund'):
                if not inv.reference:
                    ref = inv.number
                else:
                    ref = inv.reference
            else:
                ref = inv.number

            self._cr.execute(""" UPDATE account_move SET ref=%s
                           WHERE id=%s AND (ref IS NULL OR ref = '')""",
                             (ref, inv.move_id.id))
            self._cr.execute(""" UPDATE account_move_line SET ref=%s
                           WHERE move_id=%s AND (ref IS NULL OR ref = '')""",
                             (ref, inv.move_id.id))
            self._cr.execute(""" UPDATE account_analytic_line SET ref=%s
                           FROM account_move_line
                           WHERE account_move_line.move_id = %s AND
                                 account_analytic_line.move_id = account_move_line.id""",
                             (ref, inv.move_id.id))
            self.invalidate_cache()

        return True


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    invoice_line_tax_id = fields.Many2many('account.tax', related='invoice_line_tax_ids')
