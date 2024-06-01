# -*- coding: utf-8 -*-
"""managers.py: Django """

from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json
import logging
from collections import OrderedDict, defaultdict

import pytz
from django.db import models
from django.db.models import Q
from django.utils import formats
from django.utils.timezone import now

__author__ = 'Steven Klass'
__date__ = '11/30/16 07:32'
__copyright__ = 'Copyright 2011-2022 IC Manage Inc IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)

KEY_ORDER = ['regression_tag', 'product', 'family_name', 'subfamily_name', 'project', 'sub_project',
             'suite_name', 'subsuite_name', 'test_case', 'test_instance']
KEY_NAMES = {
    'regression_tag': "Regression Tag",
    'product': "Product",
    'family_name': "Family",
    'subfamily_name': "Sub-Family",
    'project': "Project",
    'sub_project': "Sub-Project",
    'suite_name': "Suite",
    'subsuite_name': "Sub-Suite",
    'test_case': "Test Case",
    'test_instance': "Test Instance",
    'testcasename': "Test Interation Name",
    'test_run_iter': "Test Interation",
    'username': 'User',
    'change_number': 'ICM Change Number',
    'coe': 'COE',
    'coe_parent': 'COE Parent',
    'configuration': 'ICM Configuration',
    'device': 'Device Name',
    'elapsed_secs': 'Elapsed Seconds',
    'elapsed_secs_display': 'Elapsed Seconds',
    'end_time': 'End Time',
    'error_description': 'End Time',
    'error_summary': 'Error Summary OLD',
    'error_filename': 'Error Filename',
    'failing_count': 'Total Failing',
    'flow_name': 'CRF Name',
    'flow_version': 'CRF Version',
    'hostname': 'LSF Host',
    'http_rundir': 'URL',
    'icm_tag': 'ICM Tag',
    'is_complete': 'Complete',
    'launch_time': 'Launch Time',
    'lsf_job_id': 'LSF Job ID',
    'machine_os': 'LSF OS',
    'overall_status': 'Overall Status',
    'passing_count': 'Total Passing',
    'peak_memory_mb_usage': 'Peak Memory MB',
    'peakmemoryuse': 'Peak Memory MB (OLD)',
    'pk': 'ID',
    'product_version': 'Product Version',
    'runtime_secs': 'LSF Runtime Secs',
    'runtime_secs_display': 'LSF Runtime',
    'seedvalue': 'LSF Seed Value OLD',
    'seed_value': 'LSF Seed Value',
    'simulator': 'Simulator',
    'simulator_version': 'Simulator Version',
    'site': 'Site',
    'start_time': 'Start Time',
    'summary_pk': 'Summary ID',
    'test_config_notes': 'Test Config Notes',
    'test_status': 'Overall Test Status',
    'test_type': 'Test Type',
    'timestamp': 'Time Stamp',
    'total_count': 'Total Tests',
    'total_family_names': 'Total Family Names',
    'total_instances': 'Total Instances',
    'total_products': 'Total Products',
    'total_projects': 'Total Projects',
    'total_regression_tags': 'Total Regression tags',
    'total_sub_projects': 'Total Sub-projects',
    'total_sub_suites': 'Total Sub-suites',
    'total_subfamily_names': 'Total Sub-families',
    'total_suite_names': 'Total test Suite',
    'total_test_cases': 'Total Test cases',
    'total_test_instances': 'Total Test instances',
    'total_testcasenames': 'Total Test Run Inters',
    'unanalyzed_count': 'Total Unanalyzed',
    'unique_key': 'Unique Name',
    'unique_key_raw': 'Unique Name (Raw)',
    'unique_keys': 'Unique Keys',
    'untested_count': 'Total Untested',
    'user_notes': 'User Notes',
    'workspace': 'ICM Workspace',
    'workflow': 'Workflow',
    'XregDB': 'Register spec'
}

COVERAGE_KEY_NAMES = {
    'cond_expr': 'Cond Expression',
    'fsm': 'FSM'
}


def extract_time_from_json(date_str):
    if isinstance(date_str, (list, tuple)) and len(date_str) == 1:
        date_str = date_str[0]

    if isinstance(date_str, datetime.datetime):
        return date_str

    time_str = date_str
    tz = "+00:00" if date_str.endswith("Z") else None
    if date_str[-6] in ["+", "-"]:
        time_str = date_str[:-6]
        tz = date_str[-6:]

    datetime_obj = None
    for pattern in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d H:%M:%S.%f",
                    "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
        try:
            datetime_obj = datetime.datetime.strptime(time_str, pattern)
            break
        except ValueError:
            pass

    if datetime_obj is None:
        log.error("Unable to extract date from %s", date_str)

        return now()

    if tz:
        if tz[0] == '+':
            datetime_obj -= datetime.timedelta(hours=int(int(tz[1:3])), minutes=int(tz[4:]))
        elif tz[0] == '-':
            datetime_obj += datetime.timedelta(hours=int(int(tz[1:3])), minutes=int(tz[4:]))
        datetime_obj = datetime_obj.replace(tzinfo=pytz.UTC)
    return datetime_obj


class TestResultLinkQuerySet(models.query.QuerySet):
    # TODO go through this to search for connection and what it does
    # P: I think this may also be where query set consistency falters
    def _as_json(self, pretty=False, as_list=False):
        data = []
        _data = self.filter().values_list('pk', 'options', 'summary_id', 'last_used',
                                          'updated_status__name')
        for (pk, item, summary_id, last_used, updated_status) in _data:
            try:
                _json = item
                assert (len(item.keys()))
            except (AssertionError, AttributeError):
                # This is old style (Django < 1.11)
                try:
                    _json = json.loads(item)
                except:
                    log.exception("Unable to load %s %r", type(item), item)
                    _json = {}
            _json['pk'] = pk
            print('pk', pk)
            # P: this tells me it is happening after data is acquired
            _json['summary_pk'] = summary_id
            _json['timestamp'] = last_used
            print('last used', last_used)
            _json['updated_test_status'] = updated_status
            print('updated status:', updated_status)

            # P: Error here!
            # P: I actually don't think this is affecting since it never is triggered when running the test
            if _json.get('runtime') and _json.get('runtime_seconds') is None:
                from ip_verification.utils import get_compute_secs
                try:
                    _json['runtime_seconds'] = get_compute_secs(_json['runtime'], "0:0:0")
                except:
                    pass

            data.append(_json)
        if len(data) == 1 and as_list is False:
            data = data[0]
        if pretty:
            from .models import json_serial
            return json.dumps(data, sort_keys=False, default=json_serial,
                              indent=4 if pretty else None)
        return data

    def as_json(self, pretty=False, as_list=False, prune_empty=True):
        return self.filter()._as_json(pretty=pretty, as_list=as_list)

    def get_summary_data(self, data=None):
        if data is None:
            data = self.filter()._as_json(as_list=True)

        result = OrderedDict()

        try:
            launch_time = min([extract_time_from_json(x.get('launch_time')) for x in data if
                               x.get('launch_time')])
            result['launch_time'] = formats.date_format(launch_time, 'SHORT_DATETIME_FORMAT')
        except ValueError:
            launch_time = None

        try:
            end_time = max(
                [extract_time_from_json(x.get('end_time')) for x in data if x.get('end_time')])
            result['end_time'] = formats.date_format(end_time, 'SHORT_DATETIME_FORMAT')
        except ValueError:
            end_time = None

        total_time = sum([float(x) for x in filter(None, [x.get('runtime_seconds') for x in data])])

        if launch_time and end_time:
            if not launch_time.tzinfo:
                launch_time = pytz.utc.localize(launch_time)
            if not end_time.tzinfo:
                end_time = pytz.utc.localize(end_time)
            result['elapsed_secs'] = (end_time - launch_time).total_seconds()
            result['elapsed_secs_display'] = humanize_time((end_time - launch_time).total_seconds())

        result['runtime_secs'] = total_time
        result['runtime_secs_display'] = humanize_time(total_time)

        result['total_instances'] = len([x for x in data if x.get('test_status') != "COVERAGE"])

        common_keys, unique_keys = [], []
        for key in KEY_ORDER:
            label = "total_{}s".format(key)
            value = set()
            for item in data:
                value.add(item.get(key))
            result[label] = len(filter(None, list(value)))
            if result[label] == 1:
                common_keys.append(key)
            elif result[label] > 1:
                unique_keys.append(key)

        result['common_keys'] = common_keys
        result['unique_keys'] = unique_keys

        result['total_count'] = 0
        for status, label in [('UNTESTED', 'untested_count'), ('PASS', 'passing_count'),
                              ('FAIL', 'failing_count'),
                              ('UNANALYZED', 'unanalyzed_count'), ('ALERT', 'alert_count')]:
            value = 0
            for item in data:
                test_status = item.get('test_status')
                if item.get('updated_test_status') is not None:
                    test_status = item.get('updated_test_status')
                if test_status == status:
                    value += 1
                    result['total_count'] += 1
            result[label] = value
            log.debug('{}:{}'.format(label, value))

        result['is_complete'] = True if result['untested_count'] == 0 else False
        if not result['is_complete'] and launch_time:
            result['is_complete'] = launch_time + datetime.timedelta(days=14) < now()

        result['overall_status'] = "In-Progress"
        if result['is_complete']:
            result['overall_status'] = "Fail"
            if result['failing_count'] == 0:
                result['overall_status'] = "Pass"

        return result

    def get_common_data(self, data=None):
        if data is None:
            data = self.filter()._as_json(as_list=True)

        result = {}
        if len(data):
            # We only want to look at anything but lists and dicts
            _data = [{k: v for k, v in x.items() if not isinstance(v, (list, dict))} for x in data]
            result = dict(set.intersection(*(set(d.iteritems()) for d in _data)))

        objects = list(set(filter(None, [x.get('change_number') for x in data])))
        if len(objects):
            result['change_number'] = objects[0] if len(objects) == 1 else objects

        objects = list(set(filter(None, [x.get('workspace') for x in data])))
        if len(objects):
            result['workspace'] = objects[0] if len(objects) == 1 else objects

        objects = list(set(filter(None, [x.get('icm_tag') for x in data])))
        if len(objects):
            result['icm_tag'] = objects[0] if len(objects) == 1 else objects

        objects = list(set(filter(None, [x.get('product_version') for x in data])))
        if len(objects):
            result['product_version'] = objects[0] if len(objects) == 1 else objects

        objects = list(set(filter(None, [x.get('simulationcycle') for x in data])))
        if len(objects):
            try:
                result['total_simulation_cycles'] = sum([int(x) for x in objects])
            except ValueError:
                pass

        objects = list(set(filter(None, [x.get('runtime_seconds') for x in data])))
        if len(objects):
            result['total_runtime_secs'] = sum([float(x) for x in objects])

        return result

    def get_expanded_data(self, data=None, unique_keys=None):

        if data is None:
            data = self.filter()._as_json(as_list=True)

        # Note unique_names is terribly named;
        # it's actually non-unique names we keep it for historical reasons
        if unique_keys is None:
            unique_keys = self.get_summary_data(data)['unique_keys']

        non_unique_keys = [x for x in unique_keys if x not in ['test_case', 'test_instance', 'testcasename']]

        grouping = [x for x in non_unique_keys if x in ['sub_project', 'suite_name', 'subsuite_name']]
        if not grouping:
            grouping = ['suite_name']

        LEAST_KEY_MAP = {'subsuite_name': 'sub_suite', 'suite_name': 'test_suite'}

        object_data = {}
        for item in data:
            if item.get('test_status') == "COVERAGE":
                continue
            least_key, least_key_names = [], []
            if 'sub_project' in grouping:
                least_key.append(item.get('sub_project'))
            if 'suite_name' in grouping:
                least_key.append(item.get('suite_name'))
            if 'subsuite_name' in grouping:
                least_key.append(item.get('subsuite_name'))
            least_key = tuple(least_key)

            if not object_data.get(least_key):
                # Build up a composite search
                search = ['%s=%s' % (LEAST_KEY_MAP.get(key, key), least_key[idx]) for idx, key in enumerate(grouping)]

                object_data[least_key] = {
                    'ids': [], 'PASS': 0, 'FAIL': 0, 'UNTESTED': 0, 'total': 0,
                    'name': item.get(least_key),
                    'search': ' AND '.join(search)
                }
            object_data[least_key]['ids'].append(item.get('pk'))
            if item.get('test_status') not in object_data[least_key]:
                object_data[least_key][item.get('test_status')] = 0
            object_data[least_key][item.get('test_status')] += 1
            object_data[least_key]['total'] += 1

        result = {
            'key_name': [LEAST_KEY_MAP.get(x, x) for x in grouping],  # No longer needed here for legacy
            'key_label': ", ".join([KEY_NAMES.get(x, x) for x in grouping]),
            'ids': []
        }

        if len(result['key_name']) == 1:
            result['key_name'] = result['key_name'][0]

        for key, values in object_data.items():
            _values = sorted(values['ids'])
            result['ids'].append(_values[0])
            result["{}".format(_values[0])] = {k: v for k, v in object_data[key].items() if
                                               k != "ids"}

        return result

    def get_coverage_data(self, data=None, unique_keys=None):
        if data is None:
            data = self.filter()._as_json(as_list=True)

        results = OrderedDict()

        key_order = KEY_ORDER[:] + ['start_date']

        unique_keys = unique_keys[:] if unique_keys else []
        for key in ['regression_tag']:
            if key not in unique_keys:
                unique_keys.append(key)
        unique_keys = [x for x in key_order if x in unique_keys]

        for key in ['test_instance', 'testcasename']:
            if key in unique_keys:
                unique_keys.pop(unique_keys.index(key))

        def get_num_value(value):
            if value in [None, "-", "--"]:
                return None
            try:
                value = float(value)
            except ValueError:
                return None
            value = value / 100.0
            return value

        coverage_keys = []
        for item in data:

            if item.get('test_status') != "COVERAGE":
                continue

            key = tuple([item.get(x) for x in key_order if x in unique_keys])

            if key not in results.keys():
                data = [(x, item.get(x)) for x in KEY_ORDER if x in unique_keys]
                data += [
                    ('unique_keys', unique_keys),
                    ('coverage_keys', []),
                    ('http_rundir', item.get('http_rundir')),
                ]
                results[key] = OrderedDict(data)

            coverage = item.get('coverage', {})
            if not isinstance(coverage, dict):
                if coverage is not None:
                    log.info("Skipping coverage as its value is %r", coverage)
                continue
            for k, v in coverage.items():
                if k.endswith('_numerator') or k.endswith('_denominator') or k.endswith(
                        '_nume') or k.endswith('_deno'):
                    continue
                value = get_num_value(v)
                if value is None:
                    value_str = "--"
                else:
                    value_str = "{:.2%}".format(value)

                if coverage.get('{}_numerator'.format(k)) and \
                        coverage.get('{}_denominator'.format(k)):
                    # value = float(coverage.get('{}_numerator'.format(k))) / float(coverage.get('{}_denominator'.format(k)))
                    # value_str = "{:.2%}".format(value)
                    value_str += " ({}/{})".format(coverage.get('{}_numerator'.format(k)),
                                                   coverage.get('{}_denominator'.format(k)))
                    try:
                        results[key]['{}_numerator'.format(k.lower())] = int(
                            coverage.get('{}_numerator'.format(k)))
                    except:
                        pass
                    try:
                        results[key]['{}_denominator'.format(k.lower())] = int(
                            coverage.get('{}_denominator'.format(k)))
                    except:
                        pass
                elif coverage.get('{}_nume'.format(k)) and \
                        coverage.get('{}_deno'.format(k)):
                    # value = float(coverage.get('{}_nume'.format(k))) / float(coverage.get('{}_deno'.format(k)))
                    # value_str = "{:.2%}".format(value)
                    value_str += " ({}/{})".format(coverage.get('{}_nume'.format(k)),
                                                   coverage.get('{}_deno'.format(k)))
                    try:
                        results[key]['{}_numerator'.format(k.lower())] = coverage.get(
                            '{}_nume'.format(k))
                    except:
                        pass
                    try:
                        results[key]['{}_denominator'.format(k.lower())] = coverage.get(
                            '{}_deno'.format(k))
                    except:
                        pass
                results[key]['valid_coverage_results'] = True
                results[key][k.lower()] = value
                results[key]["{}_pretty".format(k.lower())] = value_str
                if k not in coverage_keys:
                    coverage_keys.append(k)

        keys = sorted(results.keys())
        results = [results[k] for k in keys]

        for item in results:
            item.update({'coverage_keys': coverage_keys})

        return results

    def get_failure_data(self, data=None, unique_keys=None):

        if data is None:
            data = self.filter()._as_json(as_list=True)

        summary = OrderedDict()
        for item in data:
            if item.get('test_status') != "FAIL":
                continue
            error = item.get('error_summary')
            if error not in summary:
                summary[error] = OrderedDict([('total_failures', 0), ('ids', [])])
            summary[error]['total_failures'] += 1
            summary[error]['ids'].append(item.get('pk'))

        return summary

    def get_planned_test_data(self, data=None):

        if data is None:
            data = self.filter()._as_json(as_list=True)

        from .models import PlannedTestCase

        accounted_for_pks = []

        group_counter = {}
        ptc_counter = {}
        prior_group_counter = {}
        prior_ptc_counter = {}

        for item in data:
            # We only want to consider tests which is in the list.
            if not item.get('summary_pk'):
                continue

            if item.get('test_status') == "COVERAGE":
                continue

            group_name = (item.get('regression_tag'), item.get('product'),
                          item.get('family_name'), item.get('subfamily_name'),)
            if group_name not in group_counter:
                group_counter[group_name] = set()

            test_label = (item.get('regression_tag'), item.get('product'), item.get('family_name'),
                          item.get('subfamily_name'), item.get('project'), item.get('sub_project'),
                          item.get('suite_name'), item.get('subsuite_name'), item.get('test_case'),
                          item.get('test_instance'))
            group_counter[group_name].add(test_label)

            if item.get('summary_pk') in accounted_for_pks:
                continue
            summary_id = item.get('summary_pk')
            accounted_for_pks.append(summary_id)

            ptcs = PlannedTestCase.objects.filter_by_summary_id(summary_id)
            ptcs = ptcs.values_list('pk', 'regression_tag__name', 'product__name', 'family__name',
                                    'sub_family__name', 'plan_date', 'plan_qty')
            for pk, regression_tag, product, family, subfamily, plan_date, plan_qty in ptcs:
                group_name = (regression_tag, product, family, subfamily)
                if group_name not in ptc_counter:
                    ptc_counter[group_name] = []
                ptc_counter[group_name].append(
                    {'pk': pk, 'plan_date': plan_date, 'plan_qty': plan_qty})

            prior_ptcs = PlannedTestCase.objects.filter_past_milestones_by_summary_id(summary_id)
            prior_ptcs = prior_ptcs.values_list('pk', 'regression_tag__name', 'product__name',
                                                'family__name', 'sub_family__name', 'plan_date',
                                                'plan_qty')
            for pk, regression_tag, product, family, subfamily, plan_date, plan_qty in prior_ptcs:
                group_name = (regression_tag, product, family, subfamily)
                if group_name not in prior_ptc_counter:
                    prior_ptc_counter[group_name] = []
                prior_ptc_counter[group_name].append(
                    {'pk': pk, 'plan_date': plan_date, 'plan_qty': plan_qty})

        for k, v in ptc_counter.items():
            total_tests = len(group_counter.get(k, []))
            for item in v:
                try:
                    pct_to_goal = total_tests / float(item.get('plan_qty', 0))
                except ZeroDivisionError:
                    pct_to_goal = 0.0
                item['tests'] = total_tests
                item['pct_to_goal'] = pct_to_goal
                item['pct_to_goal_pretty'] = "{:.1%}".format(pct_to_goal)
                item['regression_tag'] = k[0]
                item['product'] = k[1]
                item['family'] = k[2]
                item['sub_family'] = k[3]
            ptc_counter[k] = sorted(v, key=lambda k: k['plan_date'])

        current_plan = sorted([v[0] for v in ptc_counter.values()], key=lambda k: k['plan_date'])
        current_plan_pks = [x['pk'] for x in current_plan]

        for k, v in prior_ptc_counter.items():
            for item in v:
                item['tests'] = "N/A"
                item['pct_to_goal'] = None
                item['pct_to_goal_pretty'] = "N/A"
                item['regression_tag'] = k[0]
                item['product'] = k[1]
                item['family'] = k[2]
                item['sub_family'] = k[3]
            values = sorted(v, key=lambda k: k['plan_date'])
            values.reverse()
            prior_ptc_counter[k] = values

        return {
            'current_plan': current_plan,
            'planned_test_cases': [
                ptc for v in ptc_counter.values() for ptc in v[1:]],
            'prior_test_plans': [
                ptc for v in prior_ptc_counter.values() for ptc in v if
                ptc['pk'] not in current_plan_pks]
        }

    def get_rollup_data(self):

        raw_data = self.filter().as_json(as_list=True)

        result = self.get_summary_data(raw_data)

        common_keys = result.get('common_keys')
        unique_keys = result.get('unique_keys')

        common_data = self.get_common_data(raw_data)

        for k, v in result.items():
            common_data[k] = v

        coverage_data = self.get_coverage_data(raw_data, unique_keys=unique_keys)
        failure_data = self.get_failure_data(raw_data, unique_keys=unique_keys)
        planned_test_data = self.get_planned_test_data(raw_data)
        expanded_data = self.get_expanded_data(raw_data, unique_keys=unique_keys)

        result['has_coverage'] = False
        if len(coverage_data):
            result['has_coverage'] = coverage_data[0].get('valid_coverage_results', False)

        result['finalized'] = result.get('is_complete', False)
        result['rollup'] = {
            'common_data': common_data,
            'expanded_data': expanded_data,
            'coverage_data': coverage_data,
            'failure_data': failure_data,
            'planned_test_data': planned_test_data,
        }
        return result


class TestResultLinkManager(models.Manager):

    def get_queryset(self):
        return TestResultLinkQuerySet(self.model, using=self._db)

    def as_json(self, pretty=False, as_list=False):
        return self.get_queryset().as_json(pretty=pretty, as_list=as_list)

    def filter_latest_results_for_run(self, regression_tag, user, run, summary=None):

        data = self.filter(regression_tag=regression_tag, user=user, run=run, deleted=False)

        _values = ("id", "product", "family", "sub_family", "project", "sub_project",
                   "suite", "sub_suite", "case", "instance", "summary")
        data_values = data.values_list(*_values).order_by('id')

        # Per Kalyan only look at the last run
        valid = defaultdict()
        current_active_ids = []
        for _id, product, family, sub_family, project, sub_project, suite, \
                sub_suite, case, instance, _summary in data_values:
            label = (
                product, family, sub_family, project, sub_project, suite,
                sub_suite, case, instance)
            valid[label] = (_id, _summary)
            if _summary:
                current_active_ids.append(_id)

        active_ids = [x[0] for x in valid.values()]
        current = set(active_ids) == set(current_active_ids)

        if not current and not summary:
            log.debug("Invalid Summary listing for  Regression ID: %r  Run ID: %r",
                      regression_tag.id, run.id)

        if not summary:
            return self.filter(id__in=active_ids)

        stale = list(set(current_active_ids) - set(active_ids))
        if stale:
            self.filter(id__in=stale).update(summary=None)
            log.debug("Removed %d stale summary data for Regression ID: %r  Run ID: %r", len(stale),
                      regression_tag.id, run.id)

        missing = list(set(active_ids) - set(current_active_ids))
        if missing:
            self.filter(id__in=missing).update(summary=summary)
            log.debug("Added %d missing summary data for Regression ID: %r  Run ID: %r",
                      len(missing), regression_tag.id, run.id)

        return self.filter(id__in=active_ids)

    def get_summary_data(self, data=None):
        return self.get_queryset().get_summary_data(data=data)

    def get_common_data(self, data=None):
        return self.get_queryset().get_common_data(data=data)

    def get_coverage_data(self, data=None):
        return self.get_queryset().get_coverage_data(data=data)

    def get_failure_data(self, data=None):
        return self.get_queryset().get_failure_data(data=data)

    def get_expanded_data(self, data=None):
        return self.get_queryset().get_expanded_data(data=data)

    def get_rollup_data(self):
        return self.get_queryset().get_rollup_data()


class RegressionTagSummaryQuerySet(models.query.QuerySet):

    def filter_by_user(self, user):
        if user.is_superuser:
            return self.filter(available=True)
        return self.filter(
            Q(user_deleted=False) | Q(user__name=user.username),
            available=True
        )

    def complete_jobs(self):
        prior_date = now() - datetime.timedelta(days=14)
        return self.filter(Q(finalized=True) |
                           Q(Q(passing_count__gt=0) | Q(failing_count__gt=0), finalized=False,
                             untested_count=0) |
                           Q(last_updated__lte=prior_date), available=True)

    def incomplete_jobs(self, days_ago=14):
        # Complete Job = Finalized = True OR finalized = False untested_count == 0 and at least one passing or failing
        return self.exclude(id__in=self.complete_jobs().values_list('id'))


class RegressionTagSummaryManager(models.Manager):

    def get_queryset(self):
        return RegressionTagSummaryQuerySet(self.model, using=self._db)

    def complete_jobs(self):
        return self.get_queryset().complete_jobs()

    def incomplete_jobs(self):
        return self.get_queryset().incomplete_jobs()
