from odoo import api, fields, models, _
from odoo.exceptions import UserError

class EducationEnrollment(models.Model):
    _name = "education.enrollment"
    _description = "Student Enrollment"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Reference", required=True, default="New")
    student_id = fields.Many2one('res.partner', string="Student", required=True)
    class_id = fields.Many2one('education.class', string="Class", required=True)
    crm_lead_id = fields.Many2one('crm.lead', string="CRM Lead")
    enroll_date = fields.Date(string="Enrollment Date", default=fields.Date.context_today)
    status = fields.Selection([
        ('ongoing', 'Ongoing'),
        ('paused', 'Paused'),
        ('done', 'Done'),
        ('dropped', 'Dropped')
    ], string="Status", default='ongoing')
    
    attendance_rate = fields.Float(string="Attendance Rate", compute="_compute_attendance_rate", store=True)
    satisfaction_score = fields.Float(string="Satisfaction Score")
    current_band = fields.Float(string="Current Band", compute="_compute_current_band", store=True)
    target_band = fields.Float(string="Target Band")
    risk_level = fields.Selection([
        ('none', 'New Student'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string="Risk Level", compute="_compute_risk_level", store=True)
    
    attendance_ids = fields.One2many('education.attendance', 'enrollment_id', string="Attendances")
    progress_ids = fields.One2many('education.progress', 'enrollment_id', string="Progress")
    notes = fields.Text(string="Notes")

    @api.depends('attendance_ids', 'attendance_ids.state')
    def _compute_attendance_rate(self):
        for record in self:
            total_sessions = len(record.attendance_ids)
            if total_sessions > 0:
                present_count = len(record.attendance_ids.filtered(lambda a: a.state in ['present', 'late', 'leave_early']))
                record.attendance_rate = (present_count / total_sessions) * 100
            else:
                record.attendance_rate = 0.0

    @api.depends('progress_ids', 'progress_ids.overall_band', 'progress_ids.evaluation_date')
    def _compute_current_band(self):
        for record in self:
            latest_progress = record.progress_ids.sorted(key=lambda p: (p.evaluation_date, p.id), reverse=True)[:1]
            if latest_progress:
                record.current_band = latest_progress.overall_band
            else:
                record.current_band = 0.0

    @api.depends('attendance_rate', 'current_band', 'target_band')
    def _compute_risk_level(self):
        for record in self:
            if record.attendance_rate == 0 or (record.current_band and record.current_band == 0.0):
                record.risk_level = 'none'
            elif record.attendance_rate < 50 or (record.target_band and record.current_band < record.target_band - 1.0):
                record.risk_level = 'high'
            elif record.attendance_rate < 80 or (record.target_band and record.current_band < record.target_band - 0.5):
                record.risk_level = 'medium'
            else:
                record.risk_level = 'low'

    def action_send_email(self):
        self.ensure_one()
        if not self.student_id.email:
            raise UserError(_("The student does not have an email address. Please set an email before sending."))
        
        template = self.env.ref('ielts_education.email_template_enrollment_welcome', raise_if_not_found=False)
        if not template:
            raise UserError(_("Email template not found."))

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': {
                'default_model': 'education.enrollment',
                'default_res_ids': [self.id],
                'default_template_id': template.id,
                'default_composition_mode': 'comment',
                'default_partner_ids': [self.student_id.id],
                'force_email': True,
            },
        }
