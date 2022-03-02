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
