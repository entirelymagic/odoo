from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Here are stored Real Estate property types"
    
    name = fields.Char(string='Property Type', required=True, translate=True)
