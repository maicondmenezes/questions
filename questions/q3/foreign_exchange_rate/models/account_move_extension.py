from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        company_currency = self.env.company.currency_id
        if self.currency_id and self.currency_id != company_currency:
            exchange_rate = self.env['account.foreign.exchange.rate'].search([
                ('date', '=', self.date),
                ('currency_from_id', '=', self.currency_id.id),
                ('currency_to_id', '=', company_currency.id)
            ], limit=1).exchange_rate

            for line in self.line_ids:
                line.debit_currency = line.debit * exchange_rate
                line.credit_currency = line.credit * exchange_rate
