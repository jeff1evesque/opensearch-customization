import os
import json
import requests


def get_indices(
    endpoint,
    awsauth,
    filter_header='',
    headers=json.loads(os.getenv('Headers', '{"Content-Type": "application/json"}').strip())
):
    '''

    get list of indices in the opensearch cluster

    @filter_header, headers in the index (i.e. index,docs.count)

    '''

    if filter_header:
        filter_header = '?v&h={}'.format(filter_header)

    path = '_cat/indices{}'.format(filter_header)

    try:
        r = requests.get(
            '{}/{}'.format(endpoint, path),
            auth=awsauth,
            json={},
            headers=headers
        )

        print('Notice (get_indices): on {} returned {}'.format(
            path,
            r.status_code
        ))

        if r.ok:
            return r.content.splitlines()

    except Exception as e:
        print('Error (get_indices): {}'.format(e))
        return None


def get_document_count(endpoint, awsauth, index, filter_header=''):
    '''

    check opensearch index document count

    '''

    r = get_indices(endpoint, awsauth, filter_header)
    found_index = None

    try:
        for x in r:
            row = x.split()
            found_index = row[1] if row[0].decode('utf-8') == index else None
            if found_index:
                return found_index

    except TypeError as e:
        print('Error (get_document_count): get_indices not iterable -- {}'.format(e))

    return False


def get_alert_destination(
    endpoint,
    awsauth,
    sns_alert_name=None,
    headers=json.loads(os.getenv('Headers', '{"Content-Type": "application/json"}').strip())
):
    '''

    get sns alerting destination

    '''

    path = '_plugins/_alerting/destinations'

    try:
        r = requests.get(
            '{}/{}'.format(endpoint, path),
            auth=awsauth,
            json={},
            headers=headers
        )

        print('Notice (get_alert_destination): on {} returned {}'.format(
            path,
            r.status_code
        ))

    except Exception as e:
        print('Error (get_alert_destination): {}'.format(e))
        return None

    if r.ok and 'destinations' in r.json():
        destinations = r.json()['destinations']

        if sns_alert_name:
            id = next((x['id'] for x in destinations if x['name'] == sns_alert_name), None)

        else:
            print('Error: sns_alert_name not provided')
            return None

        if id:
            return id

    else:
        print('Notice: no destination found')

    return None


def get_index_pattern(
    endpoint,
    awsauth,
    index_id=None,
    title=None,
    headers=json.loads(os.getenv('Headers', '{"Content-Type": "application/json", "osd-xsrf": "true"}').strip())
):
    '''

    get index patterns

    '''

    if index_id and title:
        path = '_dashboards/api/saved_objects/index-pattern/{}'.format(index_id)

    else:
        print('Error (get_index_pattern): path not configured')
        return False

    try:
        r = requests.get(
            '{}/{}'.format(endpoint, path),
            auth=awsauth,
            headers=headers
        )

        print('Notice (get_index_pattern): on {} returned {}'.format(
            path,
            r.status_code
        ))

    except Exception as e:
        print('Error (get_index_pattern): {}'.format(e))
        return None

    if r.ok:
        return r.json()

    else:
        print('Notice: no index pattern found')

    return None


def get_dashboard(
    endpoint,
    awsauth,
    title=None,
    headers=json.loads(os.getenv('Headers', '{"Content-Type": "application/json", "osd-xsrf": "true"}').strip())
):
    '''

    get opensearch dashboard

    '''

    if title:
        path = '_dashboards/api/saved_objects/dashboard/{}'.format(title)

    else:
        print('Error (get_dashboard): path not configured')
        return False

    try:
        r = requests.get(
            '{}/{}'.format(endpoint, path),
            auth=awsauth,
            headers=headers
        )

        if r.ok:
            return r.json()

        print('Notice (get_dashboard): on {} returned {}'.format(
            path,
            r.status_code
        ))

    except Exception as e:
        print('Error (get_dashboard): {}'.format(e))
        return None

    if r.ok:
        return r.json()

    else:
        print('Notice: no dashboard found')

    return None


def get_monitor(
    endpoint,
    awsauth,
    monitor_name,
    headers=json.loads(os.getenv('Headers', '{"Content-Type": "application/json"}').strip())
):
    '''

    get monitor by name

    '''

    path = '_plugins/_alerting/monitors/_search'

    if monitor_name:
        try:
            r = requests.get(
                '{}/{}'.format(endpoint, path),
                auth=awsauth,
                json={ 'query': { 'match' : { 'monitor.name': monitor_name } } }
                headers=headers
            )

            if r.ok:
                return r.json()

            print('Notice (get_monitor): on {} returned {}'.format(
                path,
                r.status_code
            ))

        except Exception as e:
            print('Error (get_monitor): {}'.format(e))
            return None

    else:
        print('Error (get_monitor): monitor_name not provided')
        return None
