# -*- coding: utf-8 -*-
#################################################################################
# Author      : CFIS (<https://www.cfis.store/>)
# Copyright(c): 2017-Present CFIS.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.cfis.store/>
#################################################################################

{
    "name": "Request For Quotation Portal - RFQ Portal",
    "summary": """
        This module allows vendors to search through all of Odoo's RFQs and Purchase Orders. 
        For example, after adding buy lines, a purchase RFQ can be generated for the vendor, 
        and once the state is changed to Sent, the vendor portal user can access the order/document. 
        On line products, vendors can change the unit pricing. They can also use the Accept and 
        Sign option to complete the RFQ.
    """,
    "version": "15.0.1",
    "description": """
        Manage RFQ Portal,
        Request For Quotation Portal
        Manage Multiple RFQs Module, 
        Vendor Change RFQ Price App, 
        Vendor Portal,
        Request For Quote Portal,
        Manage Request For Quotation Price, 
        Request For Quote Update Price, 
        Automatic Backend Price Change Odoo, 
        Client Change RFQ Price ,
        Supplier Change Quotation Price Odoo.
    """,    
    "author": "CFIS",
    "maintainer": "CFIS",
    "license" :  "Other proprietary",
    "website": "https://www.cfis.store",
    "images": ["images/rfq_vendor_portal.png"],
    "category": "Portal",
    "depends": [
        "portal",
        "purchase",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_views.xml",
        "views/purchase_portal_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [            
            "/rfq_vendor_portal/static/src/js/rfq_vendor_portal.js",
            "/rfq_vendor_portal/static/src/css/style.css",
        ],
        "web.assets_qweb": [
                      
        ],
    },
    "installable": True,
    "application": True,
    "price"                :  30,
    "currency"             :  "EUR",
}
