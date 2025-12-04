from django.db import migrations


class RunSQL(migrations.operations.special.RunSQL):
    """
    Bit of a hack here. Django actually wants this decision made in the router
    and we can pass **hints.
    """

    def __init__(self, *args, **kwargs):
        if 'sqlite_sql' not in kwargs:
            raise ValueError("sqlite_sql parameter required")
        sqlite_sql = kwargs.pop('sqlite_sql')

        self.sqlite_sql = sqlite_sql
        self.sqlite_reverse_sql = kwargs.pop('sqlite_reverse_sql', None)
        super().__init__(*args, **kwargs)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if not schema_editor.connection.vendor.startswith('postgres'):
            self.sql = self.sqlite_sql or migrations.RunSQL.noop
        super().database_forwards(app_label, schema_editor, from_state, to_state)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if not schema_editor.connection.vendor.startswith('postgres'):
            self.reverse_sql = self.sqlite_reverse_sql or migrations.RunSQL.noop
        super().database_backwards(app_label, schema_editor, from_state, to_state)


class RunPython(migrations.operations.special.RunPython):
    """
    Bit of a hack here. Django actually wants this decision made in the router
    and we can pass **hints.
    """

    def __init__(self, *args, **kwargs):
        if 'sqlite_code' not in kwargs:
            raise ValueError("sqlite_code parameter required")
        sqlite_code = kwargs.pop('sqlite_code')

        self.sqlite_code = sqlite_code
        self.sqlite_reverse_code = kwargs.pop('sqlite_reverse_code', None)
        super().__init__(*args, **kwargs)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if not schema_editor.connection.vendor.startswith('postgres'):
            self.code = self.sqlite_code or migrations.RunPython.noop
        super().database_forwards(app_label, schema_editor, from_state, to_state)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if not schema_editor.connection.vendor.startswith('postgres'):
            self.reverse_code = self.sqlite_reverse_code or migrations.RunPython.noop
        super().database_backwards(app_label, schema_editor, from_state, to_state)


class AlterIndexTogether(migrations.operations.models.AlterIndexTogether):
    """
    A DB-aware AlterIndexTogether that skips execution on non-PostgreSQL databases.
    This is needed because event partitioning is PostgreSQL-only, and the
    index_together changes in migration 0144 are for partition-aware queries.
    On SQLite, the FakeAddField operations don't create real columns, so the
    AlterIndexTogether would fail trying to find/modify indexes.
    """

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if not schema_editor.connection.vendor.startswith('postgres'):
            return  # Skip on non-PostgreSQL databases
        super().database_forwards(app_label, schema_editor, from_state, to_state)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if not schema_editor.connection.vendor.startswith('postgres'):
            return  # Skip on non-PostgreSQL databases
        super().database_backwards(app_label, schema_editor, from_state, to_state)


class RenameIndex(migrations.operations.models.RenameIndex):
    """
    A DB-aware RenameIndex that skips execution on non-PostgreSQL databases.
    This is needed because the indexes being renamed (from index_together to
    named indexes) only exist on PostgreSQL where the event partitioning was
    applied. On SQLite, these indexes don't exist.
    """

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if not schema_editor.connection.vendor.startswith('postgres'):
            return  # Skip on non-PostgreSQL databases
        super().database_forwards(app_label, schema_editor, from_state, to_state)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if not schema_editor.connection.vendor.startswith('postgres'):
            return  # Skip on non-PostgreSQL databases
        super().database_backwards(app_label, schema_editor, from_state, to_state)


class _sqlitemigrations:
    RunPython = RunPython
    RunSQL = RunSQL
    AlterIndexTogether = AlterIndexTogether
    RenameIndex = RenameIndex


dbawaremigrations = _sqlitemigrations()
