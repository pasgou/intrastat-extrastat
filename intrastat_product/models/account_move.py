# Copyright 2011-2017 Akretion France (http://www.akretion.com)
# Copyright 2009-2020 Noviat (http://www.noviat.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# @author Luc de Meyer <info@noviat.com>

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    intrastat_transaction_id = fields.Many2one(
        comodel_name="intrastat.transaction",
        string="Intrastat Transaction Type",
        ondelete="restrict",
        track_visibility="onchange",
        help="Intrastat nature of transaction",
    )
    intrastat_transport_id = fields.Many2one(
        comodel_name="intrastat.transport_mode",
        string="Intrastat Transport Mode",
        ondelete="restrict",
    )
    src_dest_country_id = fields.Many2one(
        comodel_name="res.country",
        string="Origin/Destination Country",
        compute="_compute_intrastat_country",
        store=True,
        compute_sudo=True,
        help="Destination country for dispatches. Origin country for " "arrivals.",
    )
    intrastat_country = fields.Boolean(
        compute="_compute_intrastat_country",
        string="Intrastat Country",
        store=True,
        compute_sudo=True,
    )
    src_dest_region_id = fields.Many2one(
        comodel_name="intrastat.region",
        string="Origin/Destination Region",
        default=lambda self: self._default_src_dest_region_id(),
        help="Origin region for dispatches, destination region for "
        "arrivals. This field is used for the Intrastat Declaration.",
        ondelete="restrict",
    )
    intrastat = fields.Char(
        string="Intrastat Declaration", related="company_id.intrastat"
    )

    @api.depends("partner_shipping_id.country_id", "partner_id.country_id")
    def _compute_intrastat_country(self):
        for inv in self:
            country = inv.partner_shipping_id.country_id or inv.partner_id.country_id
            if not country:
                country = inv.company_id.country_id
            inv.src_dest_country_id = country.id
            inv.intrastat_country = country.intrastat

    @api.model
    def _default_src_dest_region_id(self):
        return self.env.company.intrastat_region_id


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    hs_code_id = fields.Many2one(
        comodel_name="hs.code", string="Intrastat Code", ondelete="restrict"
    )

    @api.onchange("product_id")
    def intrastat_product_id_change(self):
        if self.product_id:
            hs_code = self.product_id.get_hs_code_recursively()
            self.hs_code_id = hs_code and hs_code.id or False
