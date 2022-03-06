import os
import json
import requests


def delete_index(
    endpoint,
    awsauth,
    index_name,
    headers=json.loads(os.getenv('Headers', '{"Content-Type": "application/json"}').strip())
):
    '''

    delete specified index

    '''

    try:
        r = requests.delete(
            '{}/{}'.format(endpoint, index_name),
            auth=awsauth,
            headers=headers
        )

        if r.ok:
            print('Notice: {} index deleted'.format(index_name))
            return True

        print('Notice (delete_index): for {} returned {}'.format(
            index_name,
            r.status_code
        ))

    except Exception as e:
        print('Error (delete_index): {}'.format(e))
        return False

    return False


def delete_document(
    endpoint,
    awsauth,
    index_name,
    index_range,
    headers=json.loads(os.getenv('Headers', '{"Content-Type": "application/json"}').strip())
):
    '''

    delete index documents satisfying specified range

    @range, object with the following structure

        {
            "timestamp": {
                "lte": "now-5d"
            }
        }

    '''

    if index_name and index_range:
        path = '{}/_delete_by_query'.format(index_name)
        payload = { 'query': { 'range': index_range } }

    else:
        print('Error (delete_document): path and payload not configured')
        return False

    try:
        r = requests.post(
            '{}/{}'.format(endpoint, path),
            auth=awsauth,
            json=payload,
            headers=headers
        )

        if r.ok:
            print('Notice: documents in {} deleted satisfying {}'.format(
                index_name,
                index_range
            ))
            return True

        print('Notice (delete_document): for {} returned {}'.format(
            index_name,
            r.status_code
        ))

    except Exception as e:
        print('Error (delete_document): {}'.format(e))
        return False

    return False
