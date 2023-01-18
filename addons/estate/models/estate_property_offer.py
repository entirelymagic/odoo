from odoo import api, fields, models
from datetime import timedelta
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Here are stored Real Estate property offers"
    
    price = fields.Float(string="Price", digits=(2,2))
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
    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline")
    
    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = fields.datetime.now() + timedelta(days=record.validity)
            
    def _inverse_date_deadline(self):
        for record in self:
            record.validity = (record.date_deadline - fields.datetime.now().date()).days

    def action_set_property_offer_as_accepted(self):
        """ Search to see if there are any accepted offers in all properties, 
        If no record is accepted set this one as accepted otherwise raise UserError"""
        for record in self:

            accepted_offer = self.env["estate.property.offer"].search([("property_id", "=", record.property_id.id), ("status", "=", "accepted")])
            print(accepted_offer)
            if accepted_offer:
                raise UserError("You cannot sell a property twice!")
            if record.property_id.state == "canceled":
                raise UserError("You cannot sell a canceled property!")
            record.property_id.state = "sold"
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id
            record.status = "accepted"
            # set the record of all other offers as "refused"
            other_offers = self.env["estate.property.offer"].search([("property_id", "=", record.property_id.id), ("id", "!=", record.id)])
            print(other_offers)
            other_offers.status = "refused"
        return True
    
    def action_set_property_offer_as_refused(self):
        for record in self:
            if record.property_id.state == "canceled":
                raise UserError("You cannot refuse an offer on a canceled property!")
            record.status = "refused"
        return True