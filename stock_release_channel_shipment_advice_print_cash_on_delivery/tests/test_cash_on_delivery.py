# Copyright 2024 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestCashOnDelivery(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product COD",
                "type": "product",
                "weight": 0.1,
                "uom_id": cls.uom_kg.id,
                "uom_po_id": cls.uom_kg.id,
            }
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")

        cls.pay_terms_immediate = cls.env.ref("account.account_payment_term_immediate")
        cls.pay_terms_cash_on_delivery = cls.env["account.payment.term"].create(
            {
                "name": "Cash on delivery",
                "cash_on_delivery": True,
                "line_ids": [Command.create({"value": "balance", "value_amount": 0})],
            }
        )
        cls.partner_a = cls.env["res.partner"].create({"name": "partner_a"})
        cls.partner_b = cls.env["res.partner"].create({"name": "partner_b"})
        cls.company = cls.env.user.company_id
        cls.default_pricelist = (
            cls.env["product.pricelist"]
            .with_company(cls.company)
            .create(
                {
                    "name": "default_pricelist",
                    "currency_id": cls.company.currency_id.id,
                }
            )
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.warehouse.lot_stock_id, 3
        )

    def test01(self):
        """
        Create 1 so for partner_a with payment terms having cash on delivery.

        create 1 so for partner_b with payment terms not having cash on delivery
        Validate the pickings of each so

        the picking of so partner_a has a cash on delivery invoice for partner_a
        the picking of so partner_b doesn't have a cash on delivery invoice for
        partner_b
        """
        # set cash on delivery for partner a payment term

        so1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner_a.id,
                "partner_invoice_id": self.partner_a.id,
                "partner_shipping_id": self.partner_a.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                ],
                "pricelist_id": self.default_pricelist.id,
                "picking_policy": "direct",
                "payment_term_id": self.pay_terms_cash_on_delivery.id,
            }
        )
        so1.action_confirm()
        pick1 = so1.picking_ids
        pick1.move_ids.write({"quantity_done": 1})
        pick1.button_validate()

        so2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner_b.id,
                "partner_invoice_id": self.partner_b.id,
                "partner_shipping_id": self.partner_b.id,
                "order_line": [
                    Command.create(
                        {
                            "name": self.product.name,
                            "product_id": self.product.id,
                            "product_uom_qty": 2,
                            "product_uom": self.product.uom_id.id,
                            "price_unit": self.product.list_price,
                        },
                    ),
                ],
                "pricelist_id": self.default_pricelist.id,
                "picking_policy": "direct",
                "payment_term_id": self.pay_terms_cash_on_delivery.id,
            }
        )
        so2.action_confirm()
        pick2 = so2.picking_ids
        pick2.move_ids.write({"quantity_done": 1})
        pick2.button_validate()

        # check that pick1 has a cash_on_delivery invoice for partner_a
        self.assertEqual(len(pick1.cash_on_delivery_invoice_ids), 1)
        cod_invoice = pick1.cash_on_delivery_invoice_ids[0]
        self.assertEqual(cod_invoice.invoice_partner_display_name, self.partner_a.name)

        # check that pick2 doesn't have any cash_on_delivery invoice
        self.assertEqual(len(pick2.cash_on_delivery_invoice_ids), 0)
