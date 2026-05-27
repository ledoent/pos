# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPosBarcodeRulePricedWithChangeRate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.BarcodeRule = cls.env["barcode.rule"]
        cls.config = cls.env["pos.config"].create(
            {
                "name": "Test POS - Change Rate",
                "change_rate_barcode": 10.0,
            }
        )

    def test_barcode_rule_type_selection_includes_price_change_rate(self):
        selection_values = [v for v, _ in self.BarcodeRule._fields["type"].selection]
        self.assertIn(
            "price_change_rate",
            selection_values,
            "barcode.rule.type must include 'price_change_rate'",
        )

    def test_barcode_rule_type_ondelete_set_default(self):
        rule = self.BarcodeRule.create(
            {
                "name": "Test change rate rule",
                "type": "price_change_rate",
                "pattern": r"23{NNNNN}",
            }
        )
        self.assertEqual(rule.type, "price_change_rate")
        # Simulate module uninstall behaviour: the ondelete="set default"
        # means the field reverts to default when the selection value is
        # removed. We verify the field is writable back to a standard value.
        rule.type = "price"
        self.assertEqual(rule.type, "price")

    def test_pos_config_change_rate_field_exists_and_stores(self):
        self.assertEqual(self.config.change_rate_barcode, 10.0)

    def test_pos_config_change_rate_zero_by_default(self):
        config = self.env["pos.config"].create({"name": "Test POS - Default Rate"})
        self.assertEqual(config.change_rate_barcode, 0.0)

    def test_res_config_settings_related_field(self):
        settings = (
            self.env["res.config.settings"]
            .with_context(default_pos_config_id=self.config.id)
            .create({})
        )
        self.assertEqual(settings.change_rate_barcode, 10.0)
        settings.change_rate_barcode = 5.5
        settings.execute()
        self.assertEqual(self.config.change_rate_barcode, 5.5)
