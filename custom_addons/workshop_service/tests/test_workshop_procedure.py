from psycopg2 import IntegrityError

from odoo.tests import TransactionCase


class TestWorkshopProcedure(TransactionCase):

    def test_procedure_code_must_be_unique(self):
        self.env['workshop.procedure'].create({
            'name': 'Procedimiento A',
            'code': 'TEST-UNIQUE-F21',
        })

        with self.assertRaises(IntegrityError):
            with self.cr.savepoint():
                self.env['workshop.procedure'].create({
                    'name': 'Procedimiento duplicado',
                    'code': 'TEST-UNIQUE-F21',
                })

    def test_versions_start_at_one_per_procedure(self):
        Procedure = self.env['workshop.procedure']
        Version = self.env['workshop.procedure.version']

        procedure_a = Procedure.create({
            'name': 'Procedimiento A',
            'code': 'TEST-SEQ-A',
        })
        procedure_b = Procedure.create({
            'name': 'Procedimiento B',
            'code': 'TEST-SEQ-B',
        })

        version_a = Version.create({
            'procedure_id': procedure_a.id,
        })
        version_b = Version.create({
            'procedure_id': procedure_b.id,
        })

        self.assertEqual(version_a.version_number, 1)
        self.assertEqual(version_b.version_number, 1)

    def test_batch_versions_are_sequential(self):
        procedure = self.env['workshop.procedure'].create({
            'name': 'Procedimiento por lotes',
            'code': 'TEST-BATCH-F21',
        })

        versions = self.env['workshop.procedure.version'].create([
            {'procedure_id': procedure.id},
            {'procedure_id': procedure.id},
            {'procedure_id': procedure.id},
        ])

        self.assertEqual(
            versions.mapped('version_number'),
            [1, 2, 3],
        )

    def test_version_audit_defaults(self):
        procedure = self.env['workshop.procedure'].create({
            'name': 'Procedimiento auditoría',
            'code': 'TEST-AUDIT-F21',
        })

        version = self.env['workshop.procedure.version'].create({
            'procedure_id': procedure.id,
        })

        self.assertEqual(version.state, 'preparation')
        self.assertEqual(version.created_by, self.env.user)
        self.assertTrue(version.created_at)

    def test_version_requires_existing_procedure(self):
        with self.assertRaises(IntegrityError):
            with self.cr.savepoint():
                self.env['workshop.procedure.version'].create({
                    'procedure_id': 999999999,
                })
