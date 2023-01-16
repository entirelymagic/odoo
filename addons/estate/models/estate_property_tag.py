from odoo import api, fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Here are stored Real Estate property tags"
    
    name = fields.Char(string="Name", required=True)
    