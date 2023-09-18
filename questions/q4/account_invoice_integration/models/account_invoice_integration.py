from odoo import models, fields, api
import requests
from os import getenv

class AccountInvoiceIntegration(models.Model):
    _name = 'account.invoice.integration'
    _description = 'Invoice Integration with External System'

    invoice_id = fields.Many2one('account.move', string='Invoice', required=True)
    external_system_id = fields.Char(string='External Invoice ID')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('error', 'Error'),
    ], string='Integration Status', default='pending')
    response_message = fields.Text(string='Response Message')
    periodic_call_delay = fields.Integer(string='Periodic Call Delay (minutes)')

    @api.model
    def send_to_external_system(self, invoice_id, external_system_id):
        try:            
            integration_data = {
                'invoice_id': invoice_id,
                'external_system_id': external_system_id,
            }            
            response = requests.post(getenv('INVOICE_EXTERNAL_API_ENDPOINT'), json=integration_data)
            integration = self.create({
                'invoice_id': invoice_id,
                'external_system_id': external_system_id,
                'status': 'success' if response.status_code == 200 else 'error',
                'response_message': response.text,
            })
        except Exception as e:            
            integration = self.create({
                'invoice_id': invoice_id,
                'external_system_id': external_system_id,
                'status': 'error',
                'response_message': str(e),
            })
    
    def create_invoice_in_odoo(self):        
        try:
            for record in self:                
                invoice_data = record.invoice_data  
                invoice_values = self.parse_invoice_data(invoice_data)  
                invoice = self.env['account.move'].create(invoice_values)                
                record.write({'name': invoice.name})
        except Exception as e:            
            raise
    
    @api.model
    def get_last_invoice_update(self):
        try:            
            api_endpoint = getenv('INVOICE_EXTERNAL_API_ENDPOINT')
            response = requests.get(api_endpoint)

            if response.status_code == 200:
                update_data = response.json()
                last_update_datetime = update_data.get('last_update_datetime')
                return last_update_datetime

        except Exception as e:
            raise
        
    @api.model
    def fetch_updates_from_external_system(self, last_update):
        try:            
            if self.get_last_invoice_update() != last_update:                
                response = requests.get(getenv('INVOICE_EXTERNAL_API_ENDPOINT'))
    
                if response.status_code == 200:
                    update_data = response.json()
                    self.process_external_system_updates(update_data)
                    self.set_last_invoice_update()  
    
        except Exception as e:
            
            raise       
    
