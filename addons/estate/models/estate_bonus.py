from odoo import models, fields


class EstateBonus(models.Model):
    _name = "estate.bonus"
    _description = "Here are stored Real Estate bonuses"
    
    bonus = fields.Char(string="Test", default="TestBonus")