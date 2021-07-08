# -*- coding: utf-8 -*-
"""replicate.py: Django data_replication"""

import logging

import sys

from django.core.management import BaseCommand, CommandError
from django.contrib.contenttypes.models import ContentType

from data_replication.models import ReplicationTracker, REPLICATION_TYPES

__author__ = 'Steven Klass'
__date__ = '9/25/17 13:08'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Replicate data to the different engines'
    
    def add_arguments(self, parser):
        parser.add_argument('-f', '--no-confirm', action='store_true', dest='no_confirm', help='Do not prompt for confirmation'),
        parser.add_argument('-a', '--app-name', action='store', dest='app', help='Provide the app to work on to replication'),
        parser.add_argument('-t', '--replication-type', action='store', dest='replication_type', choices=["mongo", "splunk"],
                    help='Provide the type of replication'),
        parser.add_argument('-R', '--replication_class_name', action='store', dest='replication_class_name', help='Replication Class Name'),
        parser.add_argument('-T', '--no_subtasks', default=False, action='store_true', dest='no_subtasks', help='Sub Tasks'),
        parser.add_argument('-m', '--max_count', action='store', dest='max_count', default=None, help='Max count -- DEV ONLY FOR TESTING'),
        parser.add_argument('--reset', action='store_true', dest='reset', default=None, help='Reset -- DEV ONLY FOR TESTING'),

    requires_system_checks = True

    def set_options(self, **options):

        self.verbosity = int(options.get('verbosity', 0))

        kwargs = {}
        self.app_name = options.get('app')
        if self.app_name:
            kwargs['content_type__in'] = ContentType.objects.filter(app_label=self.app_name)

        self.replication_class_name = options.get('replication_class_name')

        self.replication_type = options.get('replication_type')
        if options.get('replication_type') is not None:
            kwargs['replication_type'] = next(
                (x[0] for x in REPLICATION_TYPES if x[1].lower() == options.get('replication_type')))

        level_map = {0: logging.ERROR, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
        self.log_level = level_map.get(self.verbosity, 0)

        logging.basicConfig(
            format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            datefmt="%d/%b/%Y %H:%M:%S", level=self.log_level, stream=sys.stderr)

        self.replications = ReplicationTracker.objects.filter(**kwargs)

        if not self.replications.count():
            raise CommandError("No Replication Trackers are not present")
        self.no_subtasks = options.get('no_subtasks', False)
        self.max_count = int(options.get('max_count')) if options.get('max_count') else None
        self.reset = options.get('reset', False)

    def handle(self, **options):
        self.set_options(**options)

        total = self.replications.count()
        for idx, replication in enumerate(self.replications, start=1):
            log.info("Working on %d/%d %s", idx, total, replication)
            replicator = replication.get_replicator(
                replication_class_name=self.replication_class_name,
                use_subtasks=not self.no_subtasks,
                max_count=self.max_count,
                reset=self.reset,
                log_level=self.log_level,
            )
            replicator.analyze()
        print("Done!!")
        pass
