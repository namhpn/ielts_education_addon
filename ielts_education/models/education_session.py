from odoo import api, fields, models

class EducationSession(models.Model):
    _name = "education.session"
    _description = "Class Session"

    name = fields.Char(string="Session Name", required=True)
    class_id = fields.Many2one('education.class', string="Class", required=True)
    session_date = fields.Date(string="Session Date", required=True)
    start_time = fields.Float(string="Start Time")
    end_time = fields.Float(string="End Time")
    session_no = fields.Integer(string="Session Number")
    attendance_ids = fields.One2many('education.attendance', 'session_id', string="Attendances")
    notes = fields.Text(string="Notes")

    @api.model_create_multi
    def create(self, vals_list):
        sessions = super().create(vals_list)
        for session in sessions:
            if session.class_id:
                # Find active enrollments for the class
                enrollments = self.env['education.enrollment'].search([
                    ('class_id', '=', session.class_id.id),
                    ('status', '=', 'ongoing')
                ])
                
                attendance_vals = []
                for enrollment in enrollments:
                    attendance_vals.append({
                        'session_id': session.id,
                        'enrollment_id': enrollment.id,
                        'state': 'present', # Default state
                    })
                
                if attendance_vals:
                    self.env['education.attendance'].create(attendance_vals)
        return sessions
