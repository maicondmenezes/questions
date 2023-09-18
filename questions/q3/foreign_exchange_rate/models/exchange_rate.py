from odoo import models, fields

class ForeignExchangeRate(models.Model):
    _name = 'account.foreign.exchange.rate'
    _description = 'Foreign Exchange Rates'

    date = fields.Date(string='Date', required=True)
    currency_from_id = fields.Many2one('res.currency', string='Source Currency', required=True)
    currency_to_id = fields.Many2one('res.currency', string='Destination Currency', required=True)
    exchange_rate = fields.Float(string='Exchange Rate', required=True)
