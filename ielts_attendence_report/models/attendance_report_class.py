from odoo import api, fields, models, tools

class AttendanceReportClass(models.Model):
    _name = "ielts.attendance_report_class"
    _description = "Attendance Report by Class"
    _auto = False
    _order = 'class_id desc'

    class_id = fields.Many2one('education.class', string="Class", readonly=True)
    teacher_id = fields.Many2one('hr.employee', string="Teacher", readonly=True)
    total_attendances = fields.Integer(string="Total Attendances", readonly=True)
    total_present = fields.Integer(string="Total Present", readonly=True)
    total_absent_excused = fields.Integer(string="Total Absent Excused", readonly=True)
    total_absent_unexcused = fields.Integer(string="Total Absent Unexcused", readonly=True)
    total_late = fields.Integer(string="Total Late", readonly=True)
    total_leave_early = fields.Integer(string="Total Leave Early", readonly=True)
    attendance_rate = fields.Float(string="Attendance Rate (%)", readonly=True, group_operator="avg")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    row_number() OVER() AS id,
                    c.id AS class_id,
                    c.teacher_id AS teacher_id,
                    COUNT(a.id) AS total_attendances,
                    COUNT(CASE WHEN a.state = 'present' THEN 1 END) AS total_present,
                    COUNT(CASE WHEN a.state = 'absent_excused' THEN 1 END) AS total_absent_excused,
                    COUNT(CASE WHEN a.state = 'absent_unexcused' THEN 1 END) AS total_absent_unexcused,
                    COUNT(CASE WHEN a.state = 'late' THEN 1 END) AS total_late,
                    COUNT(CASE WHEN a.state = 'leave_early' THEN 1 END) AS total_leave_early,
                    CASE 
                        WHEN COUNT(a.id) > 0 THEN 
                            (COUNT(CASE WHEN a.state = 'present' THEN 1 END) + 
                             COUNT(CASE WHEN a.state = 'late' THEN 1 END) + 
                             COUNT(CASE WHEN a.state = 'leave_early' THEN 1 END)) * 100.0 / COUNT(a.id)
                        ELSE 0
                    END AS attendance_rate
                FROM
                    education_class c
                    JOIN education_session s ON s.class_id = c.id
                    JOIN education_attendance a ON a.session_id = s.id
                GROUP BY
                    c.id, c.teacher_id
            )
        """ % self._table)
