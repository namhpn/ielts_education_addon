from odoo import api, fields, models

class EducationClass(models.Model):
    _name = "education.class"
    _description = "IELTS Class"

    name = fields.Char(string="Class Name", required=True)
    program_type = fields.Selection([
        ('foundation', 'Foundation'),
        ('pre_ielts', 'Pre-IELTS'),
        ('general', 'General'),
        ('intensive', 'Intensive'),
        ('other', 'Other')
    ], string="Program Type", required=True)
    teacher_id = fields.Many2one('hr.employee', string="Teacher")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    target_band = fields.Float(string="Target Band")
    description = fields.Text(string="Description")
    
    enrollment_ids = fields.One2many('education.enrollment', 'class_id', string="Enrollments")
    session_ids = fields.One2many('education.session', 'class_id', string="Sessions")
