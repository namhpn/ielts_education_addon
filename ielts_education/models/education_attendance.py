from odoo import api, fields, models

class EducationAttendance(models.Model):
    _name = "education.attendance"
    _description = "Session Attendance"

    session_id = fields.Many2one('education.session', string="Session", required=True)
    enrollment_id = fields.Many2one('education.enrollment', string="Enrollment", required=True)
    student_id = fields.Many2one('res.partner', related='enrollment_id.student_id', string="Student", store=True)
    state = fields.Selection([
        ('present', 'Present'),
        ('absent_excused', 'Absent Excused'),
        ('absent_unexcused', 'Absent Unexcused'),
        ('late', 'Late'),
        ('leave_early', 'Leave Early')
    ], string="State", default='present')
    reason = fields.Char(string="Reason")
    comment = fields.Text(string="Comment")
