'''
The server backend
'''

import sl
from flask import Flask, send_from_directory, request, jsonify, render_template
from flask_compress import Compress
from flask_caching import Cache
from serverutils import *
import webbrowser

app = Flask(__name__)
app.json.ensure_ascii = False
app.config['COMPRESS_REGISTER'] = False
compress = Compress(app)
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 3000  # 缓存时间（秒）
cache = Cache(app)


@app.route("/<path:filename>")
def index(filename):
    if not filename:
        filename = "index.html"
    return send_from_directory("./", filename)


def open_browser():
    # 在启动脚本时打开index.html
    webbrowser.open("http://localhost:5009/")


def ValidFilter(response):
    if response.status_code != 200:
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
    app.run(host="localhost", port=5009, debug=debug)
