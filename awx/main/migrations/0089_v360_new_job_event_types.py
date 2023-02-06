# Generated by Django 2.2.4 on 2019-09-12 13:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0088_v360_dashboard_optimizations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobevent',
            name='event',
            field=models.CharField(
                choices=[
                    ('runner_on_failed', 'Host Failed'),
                    ('runner_on_start', 'Host Started'),
                    ('runner_on_ok', 'Host OK'),
                    ('runner_on_error', 'Host Failure'),
                    ('runner_on_skipped', 'Host Skipped'),
                    ('runner_on_unreachable', 'Host Unreachable'),
                    ('runner_on_no_hosts', 'No Hosts Remaining'),
                    ('runner_on_async_poll', 'Host Polling'),
                    ('runner_on_async_ok', 'Host Async OK'),
                    ('runner_on_async_failed', 'Host Async Failure'),
                    ('runner_item_on_ok', 'Item OK'),
                    ('runner_item_on_failed', 'Item Failed'),
                    ('runner_item_on_skipped', 'Item Skipped'),
                    ('runner_retry', 'Host Retry'),
                    ('runner_on_file_diff', 'File Difference'),
                    ('playbook_on_start', 'Playbook Started'),
                    ('playbook_on_notify', 'Running Handlers'),
                    ('playbook_on_include', 'Including File'),
                    ('playbook_on_no_hosts_matched', 'No Hosts Matched'),
                    ('playbook_on_no_hosts_remaining', 'No Hosts Remaining'),
                    ('playbook_on_task_start', 'Task Started'),
                    ('playbook_on_vars_prompt', 'Variables Prompted'),
                    ('playbook_on_setup', 'Gathering Facts'),
                    ('playbook_on_import_for_host', 'internal: on Import for Host'),
                    ('playbook_on_not_import_for_host', 'internal: on Not Import for Host'),
                    ('playbook_on_play_start', 'Play Started'),
                    ('playbook_on_stats', 'Playbook Complete'),
                    ('debug', 'Debug'),
                    ('verbose', 'Verbose'),
                    ('deprecated', 'Deprecated'),
                    ('warning', 'Warning'),
                    ('system_warning', 'System Warning'),
                    ('error', 'Error'),
                ],
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name='projectupdateevent',
            name='event',
            field=models.CharField(
                choices=[
                    ('runner_on_failed', 'Host Failed'),
                    ('runner_on_start', 'Host Started'),
                    ('runner_on_ok', 'Host OK'),
                    ('runner_on_error', 'Host Failure'),
                    ('runner_on_skipped', 'Host Skipped'),
                    ('runner_on_unreachable', 'Host Unreachable'),
                    ('runner_on_no_hosts', 'No Hosts Remaining'),
                    ('runner_on_async_poll', 'Host Polling'),
                    ('runner_on_async_ok', 'Host Async OK'),
                    ('runner_on_async_failed', 'Host Async Failure'),
                    ('runner_item_on_ok', 'Item OK'),
                    ('runner_item_on_failed', 'Item Failed'),
                    ('runner_item_on_skipped', 'Item Skipped'),
                    ('runner_retry', 'Host Retry'),
                    ('runner_on_file_diff', 'File Difference'),
                    ('playbook_on_start', 'Playbook Started'),
                    ('playbook_on_notify', 'Running Handlers'),
                    ('playbook_on_include', 'Including File'),
                    ('playbook_on_no_hosts_matched', 'No Hosts Matched'),
                    ('playbook_on_no_hosts_remaining', 'No Hosts Remaining'),
                    ('playbook_on_task_start', 'Task Started'),
                    ('playbook_on_vars_prompt', 'Variables Prompted'),
                    ('playbook_on_setup', 'Gathering Facts'),
                    ('playbook_on_import_for_host', 'internal: on Import for Host'),
                    ('playbook_on_not_import_for_host', 'internal: on Not Import for Host'),
                    ('playbook_on_play_start', 'Play Started'),
                    ('playbook_on_stats', 'Playbook Complete'),
                    ('debug', 'Debug'),
                    ('verbose', 'Verbose'),
                    ('deprecated', 'Deprecated'),
                    ('warning', 'Warning'),
                    ('system_warning', 'System Warning'),
                    ('error', 'Error'),
                ],
                max_length=100,
            ),
        ),
    ]
