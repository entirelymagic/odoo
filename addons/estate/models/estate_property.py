from odoo import fields, models
from dateutil.relativedelta import relativedelta


class RealEstateProperty(models.Model):
    _name = "estate.property"
    _description = "Here is stored Real Estate information"

    name = fields.Char('Title', required=True, translate=True)
    description = fields.Text(string='Description')
    postcode = fields.Char(string='Post Code', required=True)
    date_availability = fields.Date(
        string='Available From',
        copy=False, 
        default=lambda self: fields.datetime.now() + relativedelta(months=+3)
    )
    expected_price = fields.Float(string='Expected Price', required=True)
    selling_price = fields.Float(string='Selling Price', readonly=True, copy=False)
    bedrooms = fields.Integer(string='Bedrooms', default=2)
    living_area = fields.Integer(string='Living Area')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage')
    garden = fields.Boolean(string='Garden')
    garden_area = fields.Integer(string='Garden Area')
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ],
    )
    state = fields.Selection(
        [
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        copy=False,
        default="new",
    )
    active = fields.Boolean(default=True)
    
    buyer_id = fields.Many2one("res.partner", string="Buyer")
    salesman_id = fields.Many2one("res.user", string="Salesman")
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
