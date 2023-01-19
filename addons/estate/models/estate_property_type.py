from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Here are stored Real Estate property types"
    _order = "name"

    name = fields.Char(string='Property Type', required=True, translate=True)
    sequence = fields.Integer(string="Sequence", default=1, help="Used to order Properties types, lower is better.")

    _sql_constraints = [
        (
            'unique_property_type_name',
            'UNIQUE(name)',
            'The property type name must be unique!',
        ),
    ]
