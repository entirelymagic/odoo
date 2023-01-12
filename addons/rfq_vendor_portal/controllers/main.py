import binascii

from collections import OrderedDict
from datetime import date
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.exceptions import AccessError, MissingError

from odoo import fields, http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

from functools import partial
from odoo.tools import formatLang

class CustomerPortal(CustomerPortal):
    
    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        PurchaseOrder = request.env['purchase.order']
        values['purchase_rfq_count'] = PurchaseOrder.search_count([
            ('state', '=', 'sent'),('partner_id','=',request.env.user.partner_id.id)
        ])if PurchaseOrder.check_access_rights('read', raise_exception=False) else 0

        return values

    @http.route(['/my/purchase_rfq', '/my/purchase_rfq/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_purchase_rfq(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        PurchaseOrder = request.env['purchase.order']

        domain = [('state', '=', 'sent')]
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc, id desc'},
            'name': {'label': _('Name'), 'order': 'name asc, id asc'},
            'submitted': {'label': _('RFQ Submitted'), 'order': 'is_rfq_submitted asc'},
            'amount_total': {'label': _('Total'), 'order': 'amount_total desc, id desc'},
        }
        # default sortby order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('state', '=', 'sent')]},
            'submitted': {'label': _('RFQ Submitted'), 'domain': [('is_rfq_submitted', '=', True)]},
            'sent': {'label': _('Sent'), 'domain': [('state', 'in', ['sent']),('partner_id','=',request.env.user.partner_id.id)]},
        }
        # count for pager
        purchase_rfq_count = PurchaseOrder.search_count(domain)

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # make pager
        pager = portal_pager(
            url="/my/purchase_rfq",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=purchase_rfq_count,
            page=page,
            step=self._items_per_page
        )
        # search the purchase orders to display, according to the pager data
        purchase_rfq = PurchaseOrder.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        request.session['my_rfq_purchase_history'] = purchase_rfq.ids[:100]
        values.update({
            'date': date_begin,
            'purchase_rfq': purchase_rfq.sudo(),
            'page_name': 'purchase_rfq',
            'pager': pager,
            'filterby': filterby,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_sortings': searchbar_sortings,            
            'default_url': '/my/purchase_rfq',
        })
        return request.render("rfq_vendor_portal.portal_my_purchase_rfq", values)
    
    @http.route(['/my/purchase/<int:order_id>'], type='http', auth="public", website=True)
    def portal_my_purchase_order(self, order_id=None, access_token=None, message=False, download=False, **kw):    
        try:
            purchase_order_sudo = self._document_check_access('purchase.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')                
                
        if purchase_order_sudo:
            now = fields.Date.today().isoformat()            
            session_obj_date = request.session.get('view_quote_%s' % purchase_order_sudo.id)
            if isinstance(session_obj_date, date):
                session_obj_date = session_obj_date.isoformat()            
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_quote_%s' % purchase_order_sudo.id] = now
                body = _('Viewed by customer %s') % purchase_order_sudo.partner_id.name
                _message_post_helper(
                    "purchase.order",
                    purchase_order_sudo.id,
                    body,
                    token=purchase_order_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=purchase_order_sudo.user_id.sudo().partner_id.ids,
                )

        report_type = kw.get('report_type')
        if report_type in ('html', 'pdf', 'text'):
            if purchase_order_sudo.state == 'purchase':                
                return self._show_report(model=purchase_order_sudo, report_type=report_type, report_ref='purchase.action_report_purchase_order', download=download)
            else:
                return self._show_report(model=purchase_order_sudo, report_type=report_type, report_ref='purchase.report_purchase_quotation', download=download)
        
        if purchase_order_sudo.state in ('draft', 'sent', 'cancel'):
            history = request.session.get('my_rfq_purchase_history', [])
        else:
            history = request.session.get('my_purchases_history', [])

        values = {
            'purchase_order': purchase_order_sudo,
            'message': message,
            'token': access_token,            
            'bootstrap_formatting': True,
            'partner_id': purchase_order_sudo.partner_id.id,
            'report_type': 'html',
            'action': purchase_order_sudo._get_portal_return_action(),
        }
        if purchase_order_sudo.company_id:
            values['res_company'] = purchase_order_sudo.company_id
        values.update(get_records_pager(history, purchase_order_sudo))
        return request.render('rfq_vendor_portal.purchase_order_portal_template', values)
    
    @http.route(['/my/purchase/<int:order_id>/update_rfq_line'], type='json', auth="public", website=True)
    def update_rfq_line(self, line_id, remove=False, unlink=False, order_id=None, access_token=None, **post):
        values = self.update_rfq_line_dict(line_id, remove, unlink, order_id, access_token, **post)
        if values:
            return [values['rfq_amount_total']]
        return values
    
    def _get_purchase_rfq_details(self, purchase_order_sudo, rfq_line=False, price=False):
        currency = purchase_order_sudo.currency_id
        format_price = partial(formatLang, request.env, digits=currency.decimal_places)
        results = {                        
            'rfq_amount_total': format_price(purchase_order_sudo.amount_total),
            'rfq_amount_untaxed': format_price(purchase_order_sudo.amount_untaxed),
            'rfq_amount_tax': format_price(purchase_order_sudo.amount_tax),
        }
        if rfq_line:
            results.update({
                'rfq_line_price_unit' : str(price),
                'rfq_line_price_total': format_price(rfq_line.price_total),
                'rfq_line_price_subtotal': format_price(rfq_line.price_subtotal),
            })
            try:
                results['rfq_totals_table'] = request.env['ir.ui.view']._render_template('rfq_vendor_portal.purchase_rfq_portal_content_totals_table', {
                    'purchase_order': purchase_order_sudo
                })
            except ValueError:
                pass
        return results

    @http.route(['/my/purchase/<int:order_id>/update_rfq_line_dict'], type='json', auth="public", website=True)
    def update_rfq_line_dict(self, line_id, remove=False, unlink=False, order_id=None, access_token=None, input_price=False, **kwargs):
        try:
            purchase_order_sudo = self._document_check_access('purchase.order', order_id, access_token=access_token)
        except (MissingError,AccessError):
            return request.redirect('/my')

        if purchase_order_sudo.state not in ('draft', 'sent'):
            return False

        rfq_line = request.env['purchase.order.line'].sudo().browse(int(line_id))
        if rfq_line.order_id != purchase_order_sudo:
            return False

        if unlink:
            rfq_line.unlink()
            return False

        if input_price is not False:
            price = input_price
        else:
            number = -1 if remove else 1
            price = rfq_line.price_unit + number

        if price < 0:
            price = 0.0

        rfq_line.write({'price_unit': price})
        results = self._get_purchase_rfq_details(purchase_order_sudo, rfq_line, price)
        return results
    
    @http.route(['/my/purchase/<int:order_id>/accept'], type='json', auth="public", website=True)
    def purchase_rfq_accept(self, order_id, access_token=None, name=None, signature=None):
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            purchase_order_sudo = self._document_check_access('purchase.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}

        if not purchase_order_sudo.has_to_be_signed():
            return {'error': _('The order is not in a state that requires a signature from the consumer.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            purchase_order_sudo.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'signature': signature,
                'is_rfq_submitted': True,
            })
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}        

        if purchase_order_sudo.state == 'purchase':
            pdf = request.env.ref('purchase.action_report_purchase_order').sudo()._render_qweb_pdf([purchase_order_sudo.id])[0]
        else:
            pdf = request.env.ref('purchase.report_purchase_quotation').sudo()._render_qweb_pdf([purchase_order_sudo.id])[0]

        _message_post_helper(
            'purchase.order', purchase_order_sudo.id, _('Order signed by %s') % (name,),
            attachments=[('%s.pdf' % purchase_order_sudo.name, pdf)],
            **({'token': access_token} if access_token else {}))

        query_string = '&message=sign_ok'        
        return {
            'force_refresh': True,
            'redirect_url': purchase_order_sudo.get_portal_url(query_string=query_string),
        }
    
    @http.route(['/my/purchase/<int:order_id>/decline'], type='http', auth="public", methods=['POST'], website=True)
    def purchase_decline(self, order_id, access_token=None, **post):
        try:
            purchase_order_sudo = self._document_check_access('purchase.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        message = post.get('decline_message')

        query_string = False
        if purchase_order_sudo.has_to_be_signed() and message:
            purchase_order_sudo.button_cancel()
            _message_post_helper('purchase.order', order_id, message, **{'token': access_token} if access_token else {})
        else:
            query_string = "&message=cant_reject"

        return request.redirect(purchase_order_sudo.get_portal_url(query_string=query_string))