from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero


class RealEstateProperty(models.Model):
    _name = "estate.property"
    _description = "Here is stored Real Estate information"

    name = fields.Char('Plan Name', required=True, translate=True)
    description = fields.Text(string='Description')
    postcode = fields.Char(string='Post Code', required=True)
    date_availability = fields.Date(string='Available from', default=fields.datetime.now(), copy=False)
    expected_price = fields.Float(string='Expected Price', required=True, default=0)
    selling_price = fields.Float(string='Selling Price', readonly=True )
    bedrooms = fields.Integer(string='Bedrooms', default=2)
    living_area = fields.Integer(string='Living Area')
    total_area = fields.Integer(string='Total Area', compute="_compute_total_area", default=0)
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
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    salesman_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    property_type_id = fields.Many2one(
        "estate.property.type", string="Property Type", required=True, ondelete="restrict"
    )

    tags_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    best_price = fields.Integer(string="Best Price", compute="_compute_best_offer")

    @api.onchange("garden_area", "living_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids")
    def _compute_best_offer(self):
        for record in self:
            try:
                record.best_price = max(record.mapped('offer_ids.price'))
            except ValueError:
                record.best_price = 0

    def action_set_estate_property_as_canceled(self):
        for record in self:
            if record.state == "sold":
                raise UserError("You cannot cancel a sold property!")
            record.state = "canceled"
        return True

    def action_set_estate_property_as_sold(self):
        for record in self:
            if record.state == "canceled":
                raise UserError("You cannot sell a canceled property!")
            record.state = "sold"
        return True

    _sql_constraints = [
        (
            'check_expected_price_positive',
            'CHECK(expected_price >= 0)',
            'The expected price must be positive!',
        ),
        (
            'check_selling_price_positive',
            'CHECK(selling_price >= 0)',
            'The selling price must be positive!',
        ),
        (
            'unique_property_name',
            'UNIQUE(name)',
            'The property name must be unique!',
        ),
    ]
    
    @api.constrains('selling_price')
    def check_property_selling_price(self):
        """Selling price cannot be lower than 90% of the expected price"""
        for record in self:
            if record.selling_price < 0.9 * record.expected_price:
                raise UserError("The selling price cannot be lower than 90% of the expected price!")
