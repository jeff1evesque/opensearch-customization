import os
import json
import requests


def set_new_index(
    endpoint,
    awsauth,
    index_name,
    shard_number=1,
    replica_number=1,
    mappings={},
    headers=json.loads(os.getenv('Headers', '{"Content-Type": "application/json"}').strip()),
    update=False
):
    '''

    create new index with specified mapping

    '''

    if not index_name:
        print('Error (set_new_index): index_name not provided')
        return False

    if not mappings:
        print('Notice (set_new_index): mappings not provided')

    payload = {
        'settings': {
            'index': {
                'number_of_shards': shard_number,
                'number_of_replicas': replica_number
            }
        },
        'mappings': mappings
    }

    try:
        r = requests.put(
            '{}/{}'.format(endpoint, index_name),
            auth=awsauth,
            json=payload,
            headers=headers
        )

        if r.ok:
            print('Notice: {} index created'.format(index_name))
            return True

        print('Notice (set_new_index): for {} returned {}'.format(
            index_name,
            r.status_code
        ))

    except Exception as e:
        print('Error (set_new_index): {}'.format(e))
        return False

    return False


def set_reindex(
    endpoint,
    awsauth,
    source_index,
    destination_index,
    headers=json.loads(os.getenv('Headers', '{"Content-Type": "application/json"}').strip())
):
    '''

    reindex old index into new index

    '''

    if source_index and destination_index:
        path = '_reindex'
        payload = {
          'source': {
            'index': source_index
          },
          'dest': {
            'index': destination_index
          }
        }

    else:
        print('Error (set_reindex): path and payload not configured')
        return False

    #
    # configure opensearch index pattern
    #
    try:
        r = requests.post(
            '{}/{}'.format(endpoint, path),
            auth=awsauth,
            json=payload,
            headers=headers
        )

        if r.ok:
            print('Notice: opensearch reindex from {} to {}'.format(
                source_index,
                destination_index
            ))
            return True

        print('Notice (set_reindex): on {} returned {}'.format(
            path,
            r.status_code
        ))

    except Exception as e:
        print('Error (set_reindex): {}'.format(e))
        return False

    return False


def set_index_pattern(
    endpoint,
    awsauth,
    index_id=None,
    title=None,
    headers=json.loads(os.getenv('Headers', '{"Content-Type": "application/json", "osd-xsrf": "true"}').strip()),
    update=False
):
    '''

    set opensearch index pattern

    '''

    if index_id and title:
        path = '_dashboards/api/saved_objects/index-pattern/{}'.format(index_id)
        payload = {
            'attributes': {'title': title}
        }

    else:
        print('Error (set_index_pattern): path and payload not configured')
        return False

    #
    # configure opensearch index pattern
    #
    try:
        if update:
            r = requests.put(
                '{}/{}'.format(endpoint, path),
                auth=awsauth,
                json=payload,
                headers=headers
            )

        else:
            r = requests.post(
                '{}/{}'.format(endpoint, path),
                auth=awsauth,
                json=payload,
                headers=headers
            )

        if r.ok:
            print('Notice: opensearch index pattern configured')
            return True

        print('Notice (set_index_pattern): on {} returned {}'.format(
            path,
            r.status_code
        ))

    except Exception as e:
        print('Error (set_index_pattern): {}'.format(e))
        return False

    return False


def set_alert_destination(
    endpoint,
    awsauth,
    sns_alert_name=None,
    sns_topic_arn=None,
    sns_role_arn=None,
    headers=json.loads(os.getenv('Headers', '{"Content-Type": "application/json"}').strip()),
    update=False,
):
    '''

    set sns alerting destination

    '''

    #
    # define payload and path
    #
    if sns_alert_name and sns_topic_arn and sns_role_arn:
        path = '_plugins/_alerting/destinations'
        payload = {
            'name': sns_alert_name,
            'type': 'sns',
            'sns': {
                'topic_arn': sns_topic_arn,
                'role_arn': sns_role_arn
            }
        }

    else:
        print('Error (set_alert_destination): path and payload not configured')
        return False

    #
    # configure opensearch domain
    #
    try:
        if update:
            r = requests.put(
                '{}/{}'.format(endpoint, path),
                auth=awsauth,
                json=payload,
                headers=headers
            )

        else:
            r = requests.post(
                '{}/{}'.format(endpoint, path),
                auth=awsauth,
                json=payload,
                headers=headers
            )

        if r.ok:
            print('Notice: sns destination configured')
            return True

        print('Notice (set_alert_destination): on {} returned {}'.format(
            path,
            r.status_code
        ))

    except Exception as e:
        print('Error (set_alert_destination): {}'.format(e))
        return False

    return False


def set_dashboard(
    endpoint,
    awsauth,
    title=None,
    headers=json.loads(os.getenv('Headers', '{"Content-Type": "application/json", "osd-xsrf": "true"}').strip()),
    update=False
):
    '''

    create opensearch dashboard

    '''

    if title:
        path = '_dashboards/api/saved_objects/dashboard/{}'.format(title)
        payload = {
            'attributes': {'title': title}
        }

    else:
        print('Error (set_dashboard): path and payload not configured')
        return False

    try:
        if update:
            r = requests.put(
                '{}/{}'.format(endpoint, path),
                auth=awsauth,
                json=payload,
                headers=headers
            )

        else:
            r = requests.post(
                '{}/{}'.format(endpoint, path),
                auth=awsauth,
                json=payload,
                headers=headers
            )

        if r.ok:
            print('Notice: dashboard created')
            return True

        print('Notice (set_dashboard): on {} returned {}'.format(
            path,
            r.status_code
        ))

    except Exception as e:
        print('Error (set_dashboard): {}'.format(e))
        return None

    return False


def set_monitor(
    endpoint,
    awsauth,
    monitor_name,
    destination_id=None,
    monitor_id='',
    indices=[],
    query_size=0,
    schedule_interval=5,
    schedule_unit='MINUTES',
    post_date_field='timestamp',
    post_date_from='now-1h',
    post_date_to='now',
    post_date_include_lower='true',
    post_date_include_upper='true',
    post_date_format='epoch_millis',
    adjust_pure_negative='true',
    monitor_query_terms={},
    aggregations={},
    trigger_name=None,
    trigger_severity='1',
    trigger_condition_source='ctx.results[0].hits.total.value > 5',
    trigger_action_name=None,
    trigger_action_subject='Monitor Triggered',
    trigger_action_message='Monitor detected {} satisfying {} within {}'.format(
        monitor_query_terms,
        trigger_condition_source,
        schedule_interval
    ),
    trigger_action_throttle_enabled='false',
    headers=json.loads(os.getenv('Headers', '{"Content-Type": "application/json"}').strip())
):
    '''

    set monitor to run query and check whether results should trigger any alerts

    @monitor_id, if provided update monitor by specified id
    @monitor_query_terms, has an object structure as follows, where 'status' is
        a field within the cluster index:

        {
            'status': ['fail'],
            'boost': 1
        }

    @trigger_condition_source, the condition will be applied to the ctx.results,
        which is a byproduct of the 'monitor_query_terms' (acting as a filter)

    '''

    if monitor_name and destination_id and indices:
        suffix = '/{}'.format(monitor_id) if monitor_id else ''
        path = '_plugins/_alerting/monitors{}'.format(suffix)
        payload = {
            'type': 'monitor',
            'name': monitor_name,
            'monitor_type': 'query_level_monitor',
            'enabled': 'true',
            'schedule': {
                'period': {
                    'interval': schedule_interval,
                    'unit': schedule_unit
                }
            },
            'inputs': [{
                'search': {
                    'indices': indices,
                    'query': {
                        'size': query_size,
                        'query': {
                            'bool': {
                                'filter': [{
                                    'range': {
                                        post_date_field: {
                                            'gte': post_date_from,
                                            'lt': post_date_to,
                                            'include_lower': post_date_include_lower,
                                            'include_upper': post_date_include_upper,
                                            'format': post_date_format
                                        }
                                    }
                                }, {
                                    'terms': monitor_query_terms
                                }]
                            }
                        },
                        'aggregations': aggregations
                    }
                }
            }],
            'triggers': [{
                'name': trigger_name if trigger_name else monitor_name,
                'severity': trigger_severity,
                'condition': {
                    'script': {
                        'source': trigger_condition_source,
                        'lang': 'painless'
                    }
                },
                'actions': [{
                    'name': trigger_action_name if trigger_action_name else monitor_name,
                    'destination_id': destination_id,
                    'message_template': {
                        'source': trigger_action_message
                    },
                    'throttle_enabled': trigger_action_throttle_enabled,
                    'subject_template': {
                        'source': trigger_action_subject
                    }
                }]
            }]
        }

    else:
        monitor_name and destination_id and indices
        print('Error (set_monitor): {}, {}, and {} must be provided'.format(
            'monitor_name ({})'.format(monitor_name),
            'destination_id ({})'.format(destination_id),
            'indices ({})'.format(indices)
        ))
        return False

    try:
        if monitor_id:
            r = requests.put(
                '{}/{}'.format(endpoint, path),
                auth=awsauth,
                json=payload,
                headers=headers
            )

        else:
            r = requests.post(
                '{}/{}'.format(endpoint, path),
                auth=awsauth,
                json=payload,
                headers=headers
            )

        if r.ok:
            print('Notice: monitor {}'.format(
                '{} updated'.format(monitor_id) if monitor_id else 'created'
            ))
            return True

        print('Notice (set_monitor): on {} returned {}'.format(
            path,
            r.status_code
        ))

    except Exception as e:
        print('Error (set_monitor): {}'.format(e))
        return None

    return False
