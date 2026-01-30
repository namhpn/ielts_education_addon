from odoo import api, fields, models

class EducationProgress(models.Model):
    _name = "education.progress"
    _description = "Student Progress"

    enrollment_id = fields.Many2one('education.enrollment', string="Enrollment", required=True)
    student_id = fields.Many2one('res.partner', related='enrollment_id.student_id', string="Student", store=True)
    class_id = fields.Many2one('education.class', related='enrollment_id.class_id', string="Class", store=True)
    checkpoint_type = fields.Selection([
        ('after_first_week', 'After First Week'),
        ('mid_course', 'Mid Course'),
        ('pre_mock_test', 'Pre Mock Test'),
        ('other', 'Other')
    ], string="Checkpoint Type", required=True)
    evaluation_date = fields.Date(string="Evaluation Date", default=fields.Date.context_today)
    listening = fields.Float(string="Listening")
    reading = fields.Float(string="Reading")
    writing = fields.Float(string="Writing")
    speaking = fields.Float(string="Speaking")
    overall_band = fields.Float(string="Overall Band", compute='_compute_overall_band', store=True)
    teacher_id = fields.Many2one('hr.employee', string="Teacher")
    teacher_comment = fields.Text(string="Teacher Comment")

    @api.depends('listening', 'reading', 'writing', 'speaking')
    def _compute_overall_band(self):
        for record in self:
            avg = (record.listening + record.reading + record.writing + record.speaking) / 4
            decimal_part = avg % 1
            if decimal_part == 0:
                record.overall_band = avg
            elif decimal_part < 0.5:
                record.overall_band = int(avg) + 0.5
            elif decimal_part == 0.5:
                record.overall_band = avg
            else:
                record.overall_band = int(avg) + 1.0
