from odoo import Command
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase


class WorkshopCoreCase(TransactionCase):
    """Utilidades comunes para las pruebas del núcleo."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.unit = cls.env.ref('uom.product_uom_unit')
        cls.Procedure = cls.env['workshop.procedure']
        cls.Version = cls.env['workshop.procedure.version']
        cls.Line = cls.env['workshop.procedure.line']
        cls.Order = cls.env['workshop.order']

    def _make_version(self, code, lines=None, publish=True):
        procedure = self.Procedure.create({'name': code, 'code': code})
        version = self.Version.create({'procedure_id': procedure.id})
        if lines is None:
            lines = [{'line_type': 'operation', 'name': 'Revisar'}]
        for vals in lines:
            self.Line.create(dict(vals, version_id=version.id))
        if publish:
            version.action_publish()
        return version

    def _make_user(self, login, group_xmlids):
        users = self.env['res.users'].with_context(no_reset_password=True)
        field = 'group_ids' if 'group_ids' in users._fields else 'groups_id'
        return users.create({
            'name': login,
            'login': login,
            field: [Command.link(self.env.ref(x).id) for x in group_xmlids],
        })


class TestProcedureLifecycle(WorkshopCoreCase):

    def test_empty_version_cannot_be_published(self):
        version = self._make_version('TEST-EMPTY', lines=[], publish=False)
        with self.assertRaises(UserError):
            version.action_publish()

    def test_incomplete_component_cannot_be_published(self):
        version = self._make_version(
            'TEST-INCOMPLETE',
            lines=[{'line_type': 'component', 'name': 'Batería', 'quantity': 1}],
            publish=False,
        )
        with self.assertRaises(UserError):
            version.action_publish()  # falta la unidad de medida

    def test_published_version_is_immutable(self):
        version = self._make_version('TEST-IMMUTABLE')
        self.assertEqual(version.state, 'published')
        with self.assertRaises(UserError):
            version.write({'change_summary': 'cambio'})
        with self.assertRaises(UserError):
            version.write({'state': 'preparation'})
        with self.assertRaises(UserError):
            version.line_ids[0].write({'name': 'otro'})
        with self.assertRaises(UserError):
            version.line_ids[0].unlink()
        with self.assertRaises(UserError):
            self.Line.create({
                'version_id': version.id,
                'line_type': 'operation',
                'name': 'Nueva',
            })
        with self.assertRaises(UserError):
            version.unlink()

    def test_new_version_keeps_previous_and_copies_lines(self):
        version = self._make_version('TEST-NEWVER')
        version.action_create_new_version()
        versions = version.procedure_id.version_ids.sorted('version_number')
        self.assertEqual(versions.mapped('version_number'), [1, 2])
        self.assertEqual(versions[0].state, 'published')
        self.assertEqual(versions[1].state, 'preparation')
        self.assertEqual(versions[1].line_ids.mapped('name'), ['Revisar'])

    def test_retire_published_version(self):
        version = self._make_version('TEST-RETIRE')
        version.action_retire()
        self.assertEqual(version.state, 'retired')
        with self.assertRaises(UserError):
            version.action_retire()

    def test_cycle_between_procedures_is_rejected(self):
        # A v1 publicada; B v1 referencia a A v1; A v2 intenta referenciar B v1.
        version_a1 = self._make_version('TEST-CYC-A')
        version_b1 = self._make_version('TEST-CYC-B', lines=[{
            'line_type': 'subprocedure',
            'name': 'Usar A',
            'subprocedure_version_id': version_a1.id,
        }])
        version_a2 = self.Version.create({
            'procedure_id': version_a1.procedure_id.id,
        })
        with self.assertRaises(ValidationError):
            self.Line.create({
                'version_id': version_a2.id,
                'line_type': 'subprocedure',
                'name': 'Usar B',
                'subprocedure_version_id': version_b1.id,
            })

    def test_publish_requires_procedure_manager(self):
        version = self._make_version('TEST-PERM', publish=False)
        technician = self._make_user(
            'tech_publish', ['workshop_service.group_workshop_technician']
        )
        with self.assertRaises(AccessError):
            version.with_user(technician).action_publish()
        manager = self._make_user(
            'proc_publish', ['workshop_service.group_workshop_procedure_manager']
        )
        version.with_user(manager).action_publish()
        self.assertEqual(version.state, 'published')


class TestOrderWorkflow(WorkshopCoreCase):

    def _make_order(self, **vals):
        return self.Order.create(dict({'description': 'No enciende'}, **vals))

    def test_full_flow(self):
        order = self._make_order()
        self.assertEqual(order.state, 'solicitud')
        order.action_start_diagnosis()
        order.diagnosis = 'Batería agotada'
        order.action_send_quote()
        order.write({'accepted_by_name': 'Cliente', 'acceptance_channel': 'phone'})
        order.action_approve()
        self.assertTrue(order.accepted_at)
        order.action_start_repair()
        order.action_finish()
        self.assertTrue(order.completed_at)
        order.delivery_received_by = 'Cliente'
        order.action_deliver()
        order.action_close()
        self.assertEqual(order.state, 'cerrada')
        self.assertTrue(order.closed_at)

    def test_invalid_transition_is_rejected(self):
        order = self._make_order()
        with self.assertRaises(UserError):
            order.action_finish()
        with self.assertRaises(UserError):
            order.action_close()

    def test_state_cannot_be_written_directly(self):
        order = self._make_order()
        with self.assertRaises(UserError):
            order.write({'state': 'cerrada'})
        with self.assertRaises(UserError):
            order.with_context(workshop_state_change=True).write({
                'state': 'cerrada',
            })
        with self.assertRaises(UserError):
            self._make_order(state='cerrada')

    def test_quote_requires_diagnosis(self):
        order = self._make_order()
        order.action_start_diagnosis()
        with self.assertRaises(UserError):
            order.action_send_quote()

    def test_repair_requires_approval_by_default(self):
        order = self._make_order()
        order.action_start_diagnosis()
        order.diagnosis = 'x'
        order.action_send_quote()
        with self.assertRaises(UserError):
            order.action_start_repair()

    def test_repair_without_approval_when_type_allows(self):
        repair_type = self.env['workshop.repair.type'].create({
            'name': 'Rápida',
            'code': 'TEST-QUICK',
            'require_quote_acceptance': False,
        })
        order = self._make_order(repair_type_id=repair_type.id)
        order.action_start_diagnosis()
        order.diagnosis = 'x'
        order.action_send_quote()
        order.action_start_repair()
        self.assertEqual(order.state, 'en_reparacion')

    def test_cancel_requires_reason_and_keeps_order(self):
        order = self._make_order()
        with self.assertRaises(UserError):
            order.action_cancel()
        order.cancellation_reason = 'El cliente desistió'
        order.action_cancel()
        self.assertEqual(order.state, 'cancelada')
        with self.assertRaises(UserError):
            order.write({'description': 'cambio'})
        with self.assertRaises(UserError):
            order.unlink()

    def test_urgent_priority_does_not_skip_controls(self):
        order = self._make_order(priority='2')
        with self.assertRaises(UserError):
            order.action_finish()

    def test_follow_up_order_requires_original(self):
        original = self._make_order()
        with self.assertRaises(ValidationError):
            self._make_order(follow_up_type='warranty')
        follow_up = self._make_order(
            original_order_id=original.id, follow_up_type='warranty'
        )
        self.assertEqual(follow_up.original_order_id, original)

    def test_technician_cannot_approve_or_cancel(self):
        technician = self._make_user(
            'tech_flow', ['workshop_service.group_workshop_technician']
        )
        order = self._make_order()
        order.action_start_diagnosis()
        order.diagnosis = 'x'
        order.action_send_quote()
        order.write({'accepted_by_name': 'Cliente', 'acceptance_channel': 'phone'})
        with self.assertRaises(AccessError):
            order.with_user(technician).action_approve()
        with self.assertRaises(AccessError):
            order.with_user(technician).action_cancel()

    def test_salesperson_manages_order_prices_but_not_technical_flow(self):
        salesperson = self._make_user(
            'sales_flow', ['workshop_service.group_workshop_salesperson']
        )
        order = self._make_order()
        order.with_user(salesperson).write({'description': 'Venta'})
        line = self.env['workshop.order.line'].with_user(salesperson).create({
            'order_id': order.id,
            'name': 'Servicio',
            'applied_unit_price': 125,
        })
        line.with_user(salesperson).write({'applied_unit_price': 150})
        self.assertEqual(line.applied_unit_price, 150)
        self.assertFalse(salesperson.has_group(
            'workshop_service.group_workshop_technician'
        ))
        with self.assertRaises(AccessError):
            order.with_user(salesperson).action_start_diagnosis()

        order.action_start_diagnosis()
        order.diagnosis = 'Falla identificada'
        order.action_send_quote()
        order.with_user(salesperson).write({
            'accepted_by_name': 'Cliente',
            'acceptance_channel': 'phone',
        })
        order.with_user(salesperson).action_approve()
        self.assertEqual(order.state, 'aprobada')


class TestProcedureApplication(WorkshopCoreCase):

    def _apply(self, order, version):
        return self.env['workshop.order.procedure'].create({
            'order_id': order.id,
            'procedure_version_id': version.id,
        })

    def test_apply_copies_lines_with_origin(self):
        version = self._make_version('TEST-APPLY', lines=[
            {'line_type': 'operation', 'name': 'Desmontar', 'sequence': 10},
            {
                'line_type': 'component', 'name': 'Batería', 'sequence': 20,
                'quantity': 2, 'product_uom_id': self.unit.id,
            },
            {
                'line_type': 'service_labor', 'name': 'Mano de obra',
                'sequence': 30, 'valuation_method': 'fixed',
                'reference_price': 50.0,
            },
        ])
        order = self.Order.create({})
        application = self._apply(order, version)
        lines = order.line_ids.sorted('sequence')
        self.assertEqual(lines.mapped('name'), ['Desmontar', 'Batería', 'Mano de obra'])
        self.assertEqual(lines[1].planned_quantity, 2)
        self.assertEqual(lines[1].actual_quantity, 0)
        self.assertEqual(lines[2].applied_unit_price, 50.0)
        self.assertFalse(any(lines.mapped('is_manual')))
        self.assertEqual(lines.procedure_application_id, application)

    def test_template_change_does_not_alter_existing_orders(self):
        version = self._make_version('TEST-SNAPSHOT')
        order = self.Order.create({})
        self._apply(order, version)
        version.action_create_new_version()
        draft = version.procedure_id.version_ids.filtered(
            lambda v: v.state == 'preparation'
        )
        draft.line_ids.write({'name': 'Cambiada en v2'})
        self.assertEqual(order.line_ids.mapped('name'), ['Revisar'])

    def test_unpublished_or_retired_version_cannot_be_applied(self):
        draft = self._make_version('TEST-DRAFT-APPLY', publish=False)
        order = self.Order.create({})
        with self.assertRaises(UserError):
            self._apply(order, draft)
        retired = self._make_version('TEST-RETIRED-APPLY')
        retired.action_retire()
        with self.assertRaises(UserError):
            self._apply(order, retired)

    def test_subprocedure_is_expanded_with_concrete_version(self):
        child = self._make_version('TEST-CHILD', lines=[
            {'line_type': 'operation', 'name': 'Paso hijo'},
        ])
        parent = self._make_version('TEST-PARENT', lines=[
            {'line_type': 'operation', 'name': 'Paso padre', 'sequence': 10},
            {
                'line_type': 'subprocedure', 'name': 'Usar hijo',
                'sequence': 20, 'subprocedure_version_id': child.id,
            },
        ])
        order = self.Order.create({})
        self._apply(order, parent)
        self.assertEqual(
            order.line_ids.sorted('sequence').mapped('name'),
            ['Paso padre', 'Paso hijo'],
        )
        applications = order.procedure_application_ids
        self.assertEqual(
            applications.mapped('procedure_version_id'), parent | child
        )
        child_app = applications.filtered('parent_application_id')
        self.assertEqual(child_app.procedure_version_id, child)

    def test_manual_line_is_flagged(self):
        order = self.Order.create({})
        line = self.env['workshop.order.line'].create({
            'order_id': order.id, 'name': 'Limpieza',
        })
        self.assertTrue(line.is_manual)
        self.assertFalse(line.procedure_application_id)

    def test_finish_blocked_by_required_pending_line(self):
        version = self._make_version('TEST-FINISH', lines=[
            {'line_type': 'operation', 'name': 'Obligatoria', 'required': True},
        ])
        order = self.Order.create({'diagnosis': 'x'})
        order.action_start_diagnosis()
        order.action_send_quote()
        order.write({'accepted_by_name': 'Cliente', 'acceptance_channel': 'phone'})
        order.action_approve()
        self._apply(order, version)
        order.action_start_repair()
        with self.assertRaises(UserError):
            order.action_finish()
        order.line_ids.action_mark_done()
        order.action_finish()
        self.assertEqual(order.state, 'terminada')

    def test_lines_locked_after_finish(self):
        order = self.Order.create({'diagnosis': 'x'})
        order.action_start_diagnosis()
        order.action_send_quote()
        order.write({'accepted_by_name': 'Cliente', 'acceptance_channel': 'phone'})
        order.action_approve()
        order.action_start_repair()
        line = self.env['workshop.order.line'].create({
            'order_id': order.id, 'name': 'Extra',
        })
        order.action_finish()
        with self.assertRaises(UserError):
            line.write({'actual_quantity': 1})

    def test_not_applicable_requires_reason(self):
        order = self.Order.create({})
        line = self.env['workshop.order.line'].create({
            'order_id': order.id, 'name': 'Opcional',
        })
        with self.assertRaises(ValidationError):
            line.action_mark_not_applicable()
        line.not_applicable_reason = 'No corresponde'
        line.action_mark_not_applicable()
        self.assertEqual(line.state, 'not_applicable')

    def test_actual_quantity_may_exceed_planned(self):
        version = self._make_version('TEST-QTY', lines=[{
            'line_type': 'consumable', 'name': 'Grasa', 'quantity': 10,
            'product_uom_id': self.unit.id,
        }])
        order = self.Order.create({})
        self._apply(order, version)
        line = order.line_ids
        line.actual_quantity = 15
        self.assertEqual(line.planned_quantity, 10)
        self.assertEqual(line.actual_quantity, 15)
