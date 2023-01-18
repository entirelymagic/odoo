from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Here are stored Real Estate property tags"

    name = fields.Char(string="Name", required=True)

    _sql_constraints = [
        (
            'unique_property_tag_name',
            'UNIQUE(name)',
            'The property tag name must be unique!',
        ),
    ]
