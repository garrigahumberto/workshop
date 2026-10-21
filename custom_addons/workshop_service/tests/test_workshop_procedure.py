from datetime import datetime, time, timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import TransactionCase


class TestWorkshopPreliminary(TransactionCase):

    def _enable_procedure_management(self):
        manager_group = self.env.ref(
            'workshop_service.group_workshop_procedure_manager'
        )
        self.env.user.write({'group_ids': [(4, manager_group.id)]})

    def _create_order(self, name='Taller', location=None, **values):
        if not location:
            location = self.env['workshop.location'].create({
                'name': name,
                'location_type': 'workshop',
            })
        values.setdefault('location_id', location.id)
        return self.env['workshop.order'].create(values)

    def _create_procedure(self, code='TEST-SERVICE'):
        return self.env['workshop.procedure'].create({
            'name': 'Servicio de prueba',
            'code': code,
            'line_ids': [(0, 0, {
                'line_type': 'labor',
                'name': 'Mano de obra',
                'quantity': 1,
            })],
        })

    def test_procedure_and_order_lines_validate_uom_compatibility(self):
        unit = self.env.ref('uom.product_uom_unit')
        dozen = self.env.ref('uom.product_uom_dozen')
        kilogram = self.env.ref('uom.product_uom_kgm')
        product = self.env['product.product'].create({
            'name': 'Producto para prueba de unidades',
            'uom_id': unit.id,
        })
        procedure = self._create_procedure('TEST-UOM')
        procedure_line_model = self.env['workshop.procedure.line']

        compatible_line = procedure_line_model.create({
            'procedure_id': procedure.id,
            'line_type': 'component',
            'name': 'Producto compatible',
            'product_id': product.id,
            'uom_id': dozen.id,
        })
        self.assertEqual(compatible_line.uom_id, dozen)

        with self.assertRaises(ValidationError):
            with self.cr.savepoint():
                procedure_line_model.create({
                    'procedure_id': procedure.id,
                    'line_type': 'component',
                    'name': 'Producto incompatible',
                    'product_id': product.id,
                    'uom_id': kilogram.id,
                })

        order = self._create_order('Taller para prueba de unidades')
        with self.assertRaises(ValidationError):
            with self.cr.savepoint():
                self.env['workshop.order.line'].create({
                    'order_id': order.id,
                    'name': 'Producto incompatible',
                    'product_id': product.id,
                    'uom_id': kilogram.id,
                })

    def test_revisions_are_sequential_per_code(self):
        Procedure = self.env['workshop.procedure']
        first = Procedure.create({
            'name': 'Cambio de aceite',
            'code': 'TEST-OIL',
        })
        second = Procedure.create({
            'name': 'Cambio de aceite actualizado',
            'code': 'TEST-OIL',
        })
        other = Procedure.create({
            'name': 'Otro servicio',
            'code': 'TEST-OTHER',
        })

        self.assertEqual(first.revision, 1)
        self.assertEqual(second.revision, 2)
        self.assertEqual(other.revision, 1)
        self.assertEqual(second.reference, 'TEST-OIL-002')

    def test_published_procedure_and_lines_are_immutable(self):
        self._enable_procedure_management()
        procedure = self._create_procedure()
        procedure.action_publish()

        with self.assertRaises(UserError):
            procedure.write({'name': 'Cambio no permitido'})
        with self.assertRaises(UserError):
            procedure.line_ids.write({'name': 'Cambio no permitido'})

    def test_new_published_revision_replaces_previous_choice(self):
        self._enable_procedure_management()
        first = self._create_procedure('TEST-REVISION')
        first.action_publish()
        second = first.copy()
        second.action_publish()

        self.assertEqual(second.revision, 2)
        self.assertEqual(first.state, 'archived')
        self.assertFalse(first.active)
        self.assertEqual(second.state, 'published')

    def test_applying_procedure_copies_fixed_snapshot_and_labor_owner(self):
        self._enable_procedure_management()
        procedure = self._create_procedure('TEST-APPLY')
        procedure.action_publish()
        order = self._create_order('Taller de aplicación')
        order.write({'procedure_to_apply_id': procedure.id})

        order.action_apply_procedure()

        application = order.application_ids
        line = order.line_ids
        self.assertEqual(application.procedure_id, procedure)
        self.assertEqual(application.procedure_revision, 1)
        self.assertEqual(line.name, 'Mano de obra')
        self.assertEqual(line.performed_by_id, self.env.user)
        self.assertEqual(line.planned_quantity, 1)

        line.write({'actual_quantity': 3, 'state': 'done'})
        self.assertEqual(line.actual_quantity, 3)
        self.assertEqual(procedure.line_ids.quantity, 1)

    def test_older_revision_cannot_be_applied_after_new_revision_published(self):
        self._enable_procedure_management()
        first = self._create_procedure('TEST-CURRENT')
        first.action_publish()
        second = first.copy()
        second.action_publish()
        order = self._create_order('Taller revisión vigente')
        order.write({'procedure_to_apply_id': first.id})

        with self.assertRaises(UserError):
            order.action_apply_procedure()

        order.write({'procedure_to_apply_id': second.id})
        order.action_apply_procedure()
        self.assertEqual(order.application_ids.procedure_id, second)

    def test_order_state_changes_preserve_auditable_events(self):
        order = self._create_order('Taller estados')

        with self.assertRaises(UserError):
            order.write({'state': 'closed'})

        order.action_close()
        with self.assertRaises(UserError):
            order.write({'diagnosis': 'Edición de orden cerrada'})

        order.write({
            'reopen_reason': 'Revisión por garantía',
            'follow_up_type': 'warranty',
        })
        order.action_reopen()
        self.assertEqual(order.state, 'open')
        self.assertEqual(
            order.event_ids.mapped('event_type'),
            ['opened', 'closed', 'reopened'],
        )
        self.assertEqual(order.event_ids[-1].reason, 'Revisión por garantía')
        self.assertEqual(order.event_ids[-1].follow_up_type, 'warranty')

    def test_cancellation_requires_reason_and_preserves_history(self):
        order = self._create_order('Taller cancelación')

        with self.assertRaises(UserError):
            order.action_cancel()

        order.write({'cancellation_reason': 'El cliente desistió'})
        order.action_cancel()
        self.assertEqual(order.state, 'cancelled')
        self.assertEqual(order.event_ids[-1].event_type, 'cancelled')
        self.assertEqual(order.event_ids[-1].reason, 'El cliente desistió')

    def test_order_line_cannot_reference_procedure_applied_to_other_order(self):
        self._enable_procedure_management()
        procedure = self._create_procedure('TEST-ORDER-LINK')
        procedure.action_publish()
        first_order = self._create_order('Taller orden A')
        first_order.write({'procedure_to_apply_id': procedure.id})
        first_order.action_apply_procedure()
        other_order = self._create_order('Taller orden B')

        with self.assertRaises(ValidationError):
            self.env['workshop.order.line'].create({
                'order_id': other_order.id,
                'application_id': first_order.application_ids.id,
                'name': 'Línea cruzada',
            })

    def test_dashboard_metrics_follow_date_range_and_workshop_filters(self):
        Order = self.env['workshop.order']
        workshop = self.env['workshop.location'].create({
            'name': 'Dashboard taller principal',
            'location_type': 'workshop',
        })
        other_workshop = self.env['workshop.location'].create({
            'name': 'Dashboard segundo taller',
            'location_type': 'workshop',
        })
        store = self.env['workshop.location'].create({
            'name': 'Dashboard tienda',
            'location_type': 'store',
        })

        self._create_order('Dashboard abierta', workshop)
        self._create_order(
            'Dashboard vencida',
            workshop,
            promised_date=fields.Datetime.now() - timedelta(days=1),
        )
        completed_order = self._create_order('Dashboard cerrada', workshop)
        completed_order.action_close()
        today = fields.Date.context_today(Order.with_context(tz='UTC'))
        old_date = today - timedelta(days=40)
        self._create_order(
            'Dashboard antigua',
            workshop,
            request_date=datetime.combine(old_date, time(12)),
        )
        self._create_order('Dashboard otro taller', other_workshop)
        self._create_order('Dashboard tienda', store, origin='store')

        today_string = fields.Date.to_string(today)
        data = Order.with_context(tz='UTC').get_dashboard_data(
            today_string,
            today_string,
            workshop.id,
        )
        self.assertEqual(data['metrics'], {
            'total': 3,
            'open': 2,
            'completed': 1,
            'pending': 1,
        })
        self.assertEqual(len(data['recent_orders']), 3)

        old_date_string = fields.Date.to_string(old_date)
        old_date_data = Order.with_context(tz='UTC').get_dashboard_data(
            old_date_string,
            old_date_string,
            workshop.id,
        )
        self.assertEqual(old_date_data['metrics']['total'], 1)
        self.assertEqual(len(old_date_data['recent_orders']), 1)
        old_date_workshop = next(
            item for item in old_date_data['locations']
            if item['id'] == workshop.id
        )
        self.assertEqual(old_date_workshop['orders'], 1)

        inclusive_range_data = Order.with_context(tz='UTC').get_dashboard_data(
            old_date_string,
            today_string,
            workshop.id,
        )
        self.assertEqual(inclusive_range_data['metrics']['total'], 4)

        all_workshops = Order.with_context(tz='UTC').get_dashboard_data(
            today_string,
            today_string,
        )
        self.assertEqual(
            all_workshops['metrics']['total'],
            sum(location['orders'] for location in all_workshops['locations']),
        )
        workshop_data = next(
            item for item in all_workshops['locations']
            if item['id'] == workshop.id
        )
        self.assertEqual(workshop_data['orders'], 3)
        self.assertEqual(workshop_data['open'], 3)
        self.assertEqual(workshop_data['overdue'], 1)
        self.assertNotIn(
            store.id,
            [location['id'] for location in all_workshops['locations']],
        )

    def test_dashboard_rejects_invalid_date_ranges_and_non_workshop_location(self):
        Order = self.env['workshop.order']
        workshop = self.env['workshop.location'].create({
            'name': 'Dashboard taller válido',
            'location_type': 'workshop',
        })
        store = self.env['workshop.location'].create({
            'name': 'Dashboard tienda no válida',
            'location_type': 'store',
        })

        today = fields.Date.context_today(Order)
        today_string = fields.Date.to_string(today)
        yesterday_string = fields.Date.to_string(today - timedelta(days=1))

        with self.assertRaises(UserError):
            Order.get_dashboard_data('not-a-date', today_string)
        with self.assertRaises(UserError):
            Order.get_dashboard_data(today_string, False)
        with self.assertRaises(UserError):
            Order.get_dashboard_data('', '')
        with self.assertRaises(UserError):
            Order.get_dashboard_data(today_string, yesterday_string)
        with self.assertRaises(UserError):
            Order.get_dashboard_data(today_string, today_string, store.id)
        with self.assertRaises(UserError):
            Order.get_dashboard_data(
                today_string,
                today_string,
                workshop.id + 999999,
            )

    def test_dashboard_does_not_bypass_order_read_permissions(self):
        public_user = self.env.ref('base.public_user')
        data = self.env['workshop.order'].with_user(
            public_user
        ).get_dashboard_data()

        self.assertIn('error', data)
