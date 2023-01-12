odoo.define('rfq_vendor_portal', function (require) {
    'use strict';    
    var publicWidget = require('web.public.widget');
    
    publicWidget.registry.RFQUpdateLineButton = publicWidget.Widget.extend({
        selector: '.o_portal_purchase_sidebar a.js_line_update_json',
        events: {
            'click ': '_onClick',
        },
        /**
         * @override
         */
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.elems = self._getUpdatableElements();
                self.elems.$lineUnitPrice.change(function (ev) {
                    var price = parseFloat(this.value);
                    self._onChangeUnitPrice(price);
                });
            });
        },
        /**
         * Locate in the DOM the elements to update
         * Mostly for compatibility, when the module has not been upgraded
         * In that case, we need to fall back to some other elements
         *
         * @private
         * @return {Object}: Jquery elements to update
         */
        _getUpdatableElements: function () {
            var $parentTr = this.$el.parents('tr:first');
            var $lineUnitPrice = this.$el.closest('.input-group').find('.js_unit_price')
            
            var $rfqLinePriceToal = $parentTr.find('.oe_order_line_price_total .oe_currency_value');
            var $rfqLinePriceSubTotal = $parentTr.find('.oe_order_line_price_subtotal .oe_currency_value');
    
            if (!$rfqLinePriceToal.length && !$rfqLinePriceSubTotal.length) {
                $rfqLinePriceToal = $rfqLinePriceSubTotal = $parentTr.find('.oe_currency_value').last();
            }

            var $rfqAmountUntaxed = $('[data-id="total_untaxed"]').find('span, b');
            var $rfqAmountTotaltax = $('[data-id="total_tax"]').find('span, b');
            var $rfqAmountTotal = $('[data-id="total_amount"]').find('span, b');            
    
            if (!$rfqAmountUntaxed.length) {
                $rfqAmountUntaxed = $rfqAmountTotal.eq(1);
                $rfqAmountTotal = $rfqAmountTotal.eq(0).add($rfqAmountTotal.eq(2));
            }
            
            return {
                $lineUnitPrice: $lineUnitPrice,                
                $rfqLinePriceSubTotal: $rfqLinePriceSubTotal,
                $rfqLinePriceToal: $rfqLinePriceToal,
                $rfqAmountUntaxed: $rfqAmountUntaxed,
                $rfqAmountTotal: $rfqAmountTotal,
                $rfqAmountTotaltax: $rfqAmountTotaltax,
                $rfqTotalsTable: $('#total'),               
            };
        }, 
        /**
         * Reacts to the click on the -/+ buttons
         *
         * @param {Event} ev
         */   
        _onClick: function (ev) {
            ev.preventDefault();
            return this._onChangeUnitPrice();            
        },
        /**
         * Process the change in line Unit Price
         *
         * @private
         * @param {Event} ev
         */
        _onChangeUnitPrice: function (price) {
            var access_token = false
            var href = this.$el.attr("href");
            var rfqID = href.match(/my\/purchase\/([0-9]+)/);
            var lineID = href.match(/update_rfq_line\/([0-9]+)/);
            var token = href.match(/token=([\w\d-]*)/)[1];
            if (token) {
                access_token = token;
            }
            rfqID = parseInt(rfqID[1]);
            this._callUpdateLineRoute(rfqID,{
                'line_id': parseInt(lineID[1]),
                'remove': this.$el.is('[href*="remove"]'),
                'unlink': this.$el.is('[href*="unlink"]'),
                'input_price': price >= 0 ? price : false,
                'token': access_token,
            }).then(this._updateRfqLineValues.bind(this));
        },
        /**
         * Calls the route to get updated values of the line and order
         * when the unit price of a product has changed
         *
         * @private
         * @param {integer} order_id
         * @param {Object} params
         * @return {Deferred}
         */
        _callUpdateLineRoute: function (rfq_id, params) {
            var self = this;
            var url = "/my/purchase/" + rfq_id + "/update_rfq_line_dict";            
            return this._rpc({
                route: url,
                params: params,
            });
        },
        /**
         * Processes data from the server to update the orderline UI
         *
         * @private
         * @param {Element} $orderLine: orderline element to update
         * @param {Object} data: contains order and line updated values
         */
        _updateRfqLineValues: function (data) {
            if (!data) {
                window.location.reload();
            }
            var rfqAmountTotal = data.rfq_amount_total;
            var rfqAmountUntaxed = data.rfq_amount_untaxed;
            var rfqAmountTotaltax = data.rfq_amount_tax;                    
            var rfqTotalsTable = $(data.rfq_totals_table);

            var linePriceUnit = data.rfq_line_price_unit;
            var rfqLinePriceToal = data.rfq_line_price_total;
            var rfqLinePriceSubTotal = data.rfq_line_price_subtotal;
    
            if (this.elems.$rfqLinePriceToal.length && rfqLinePriceToal !== undefined) {
                this.elems.$rfqLinePriceToal.text(rfqLinePriceToal);
            }
            if (this.elems.$rfqLinePriceSubTotal.length && rfqLinePriceSubTotal !== undefined) {
                this.elems.$rfqLinePriceSubTotal.text(rfqLinePriceSubTotal);
            }    
            if (rfqAmountUntaxed !== undefined) {
                this.elems.$rfqAmountUntaxed.text(rfqAmountUntaxed);
            }    
            if (rfqAmountTotaltax !== undefined) {
                this.elems.$rfqAmountTotaltax.text(rfqAmountTotaltax);
            }    
            if (rfqAmountTotal !== undefined) {
                this.elems.$rfqAmountTotal.text(rfqAmountTotal);
            }          
            if (rfqTotalsTable) {
                this.elems.$rfqTotalsTable.find('table').replaceWith(rfqTotalsTable);
            }

            this.elems.$lineUnitPrice.val(linePriceUnit);
        },                 
    });
});;