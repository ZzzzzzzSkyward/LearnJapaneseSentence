'''
The server backend
'''

import os
import sl
from flask import Flask, send_from_directory, request, jsonify, render_template, redirect, url_for, Response
from flask_compress import Compress
from flask_caching import Cache
from serverutils import *
import webbrowser

app = Flask(__name__, static_folder=None)
app.json.ensure_ascii = False
app.config['COMPRESS_REGISTER'] = False
app.config['STATIC_FOLDER'] = None
compress = Compress(app)
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 3000  # 缓存时间（秒）
cache = Cache(app)
# 将 /api/xxx 重定向到 /xxx


@app.route('/api/<path:subpath>')
def api_redirect(subpath):
    return redirect(url_for(subpath, **request.args))


@app.route("/", defaults={'filename': 'index.html'})
@app.route("/<path:filename>")
def index(filename):
    d = os.getcwd()
    subd = "front/dist/"
    if os.path.exists(os.path.join(d, filename)):
        return send_from_directory(d, filename)
    subpath = os.path.join(d, subd, filename)
    if os.path.exists(subpath):
        return send_from_directory(os.path.join(d, subd), filename)
    return Response('', 404)


def open_browser():
    # 在启动脚本时打开index.html
    webbrowser.open("http://localhost:5009/")


def ValidFilter(response):
    if isinstance(response, tuple):
        response, code = response
    else:
        code = response.status_code
    if code != 200:
        return False
    return True


@app.route("/process", methods=["GET"])
def process():
    query = request.args.get("query", "")
    trans = request.args.get("trans", False)
    lookup = request.args.get("lookup", False)
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400
    result = process_query(query, trans, lookup)
    return jsonify(result)


@app.route("/lookup", methods=["GET"])
@cache.cached(timeout=300, query_string=True, response_filter=ValidFilter)
def lookup():
    query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400
    result = process_lookup(query)
    return jsonify(result)


@app.route("/translate", methods=["GET"])
@cache.cached(timeout=300, query_string=True, response_filter=ValidFilter)
def translate():
    query = request.args.get("query", "")
    web = request.args.get("web", "false")
    web = web == "true"
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400
    result = {"result": get_translation(query)}
    return jsonify(result)


@app.route("/explain", methods=["GET"])
@cache.cached(timeout=300, query_string=True, response_filter=ValidFilter)
def explain():
    query = request.args.get("query", "")
    web = request.args.get("web", "false")
    web = web == "true"
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400
    result = {"result": get_explanation(query, web)}
    return jsonify(result)


@app.route("/memorize", methods=["GET"])
@cache.cached(timeout=300, query_string=True, response_filter=ValidFilter)
def memorize():
    query = request.args.get("query", "")
    web = request.args.get("web", "false")
    web = web == "true"
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400
    result = {"result": get_memorization(query, web)}
    return jsonify(result)


@app.route("/search/<query>", methods=["GET"])
@cache.cached(timeout=300, query_string=True)
def search(query):
    '''jisho protocol
    /search/{word}
    '''
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400
    result = process_lookup(query)
    return jsonify(result)


@app.route("/jp_en_dict", methods=["GET"])
def jp_en_dict():
    '''get you a dictionary of japanese to english words
    '''
    jdict = sl.load_zip('front/public/jp_en.zip', 'jp_en.json')
    return jdict


@app.route("/lookuppinyin", methods=["GET"])
def lookuppinyin():
    query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400
    result = process_lookuppinyin(query)
    return jsonify(result)


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    debug = 'debug' in args
    port = 5009
    for i in args:
        if 'port' in i:
            port = int(i[i.find('=')+1:])
    app.run(host="localhost", port=port or 5009, debug=debug)
