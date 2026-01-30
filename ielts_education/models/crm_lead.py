from odoo import api, fields, models, _
from odoo.exceptions import UserError

class CrmLead(models.Model):
    _inherit = "crm.lead"

    def action_create_enrollment(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_("Please set a Student before creating an Enrollment."))

        existing_enrollment = self.env['education.enrollment'].search([('crm_lead_id', '=', self.id)], limit=1)
        if existing_enrollment:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Enrollment'),
                'res_model': 'education.enrollment',
                'res_id': existing_enrollment.id,
                'view_mode': 'form',
                'target': 'current',
            }

        default_values = {
            'crm_lead_id': self.id,
            'student_id': self.partner_id.id,
            'name': f"{self.name} - {self.partner_id.name}",
            'enroll_date': fields.Date.context_today(self),
        }

        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Enrollment'),
            'res_model': 'education.enrollment',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_' + k: v for k, v in default_values.items()},
        }
