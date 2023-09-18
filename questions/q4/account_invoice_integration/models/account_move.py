import requests
from odoo import models, api
from os import getenv
class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def action_post(self):
        res = super(AccountMove, self).action_post()
        for invoice in self:
            if invoice.type == 'out_invoice':
                try:                    
                    integration_data = {
                        'invoice_id': invoice.id,
                        'external_system_id': '',  
                    }                    
                    response = requests.post(getenv('INVOICE_ENDPOINT'), json=integration_data)
                    integration = self.env['account.invoice.integration'].create({
                        'invoice_id': invoice.id,
                        'external_system_id': integration_data['external_system_id'],
                        'status': 'success' if response.status_code == 200 else 'error',
                        'response_message': response.text,
                    })
                except Exception as e:                    
                    integration = self.env['account.invoice.integration'].create({
                        'invoice_id': invoice.id,
                        'external_system_id': integration_data['external_system_id'],
                        'status': 'error',
                        'response_message': str(e),
                    })
        return res