import copy
import serpapi
from config import config as cfg
params = cfg.serp
client = serpapi.Client(api_key=params.api_key)


def do_search(q):
    _params = copy.copy(params.to_dict())
    _params['q'] = q
    search = client.search(_params)
    results = search.as_dict()
    r = []
    for i in results['organic_results']:
        r.append(
            {'title': i['title'], 'content': i['snippet'], 'link': i['link']})
    return r


if __name__ == '__main__':
    print(do_search('python'))
