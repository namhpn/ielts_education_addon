from odoo import api, fields, models, tools

class AttendanceReportTeacher(models.Model):
    _name = "ielts.attendance_report_teacher"
    _description = "Attendance Report by Teacher"
    _auto = False
    _order = 'teacher_id desc'

    teacher_id = fields.Many2one('hr.employee', string="Teacher", readonly=True)
    total_classes = fields.Integer(string="Total Classes", readonly=True)
    total_attendances = fields.Integer(string="Total Attendances", readonly=True)
    total_present = fields.Integer(string="Total Present", readonly=True)
    total_absent_excused = fields.Integer(string="Total Absent Excused", readonly=True)
    total_absent_unexcused = fields.Integer(string="Total Absent Unexcused", readonly=True)
    total_late = fields.Integer(string="Total Late", readonly=True)
    total_leave_early = fields.Integer(string="Total Leave Early", readonly=True)
    average_attendance_rate = fields.Float(string="Average Attendance Rate (%)", readonly=True, group_operator="avg")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    row_number() OVER() AS id,
                    c.teacher_id AS teacher_id,
                    COUNT(DISTINCT c.id) AS total_classes,
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
                    END AS average_attendance_rate
                FROM
                    education_class c
                    JOIN education_session s ON s.class_id = c.id
                    JOIN education_attendance a ON a.session_id = s.id
                WHERE c.teacher_id IS NOT NULL
                GROUP BY
                    c.teacher_id
            )
        """ % self._table)
