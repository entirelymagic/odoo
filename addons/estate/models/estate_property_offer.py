from odoo import api, fields, models

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Here are stored Real Estate property offers"
    
    price = fields.Float(string="Price", digits=2)
    status = fields.Selection(
        string="Status", 
        copy=False,
        selection=[
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ]
    
    )
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)