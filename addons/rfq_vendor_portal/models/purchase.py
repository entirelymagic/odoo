from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    is_rfq_submitted = fields.Boolean('RFQ Submitted', default=False, readonly=True, copy=False)
    require_signature = fields.Boolean('Online Signature',states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
         default=True, readonly=True, help='To confirm orders automatically, get an online signature from the consumer.')
    signature = fields.Image('Signature', copy=False, attachment=True, 
        max_width=1024, max_height=1024, help='Signature received through the portal.')
    signed_by = fields.Char('Signed By', copy=False, help='Name of the person that signed the SO.')
    signed_on = fields.Datetime('Signed On', copy=False, help='Date of the signature.')

    @api.model
    def action_rfq_sent(self):
        if self.filtered(lambda rec: rec.state != 'draft'):
            raise UserError(_('Only draft orders can be marked as sent directly.'))
        for rec in self:
            rec.message_subscribe(partner_ids=rec.partner_id.ids)
        self.write({'state': 'sent'})

    def _get_portal_return_action(self):       
        self.ensure_one()
        if self.state == 'purchase':
            return self.env.ref('purchase.purchase_form_action')
        else:
            return self.env.ref('purchase.purchase_rfq')

    def has_to_be_signed(self, include_draft=False):
        return (self.state == 'sent' or (self.state == 'draft' and include_draft)) and self.require_signature and not self.signature
    
    def preview_purchase_rfq(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }