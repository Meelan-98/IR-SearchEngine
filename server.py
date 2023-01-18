from flask import Flask, render_template, request
from search import search
from type_resolver import query_type_resolver
app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def search_box():
    if request.method == 'POST':

        query = request.form['searchTerm']

        res = search(query,query_type_resolver([False,True,False]))

        hits = res['hits']['hits']
        aggs = res['aggregations']
        num_results = len(hits)
        
        return render_template('index.html',query=query,hits=hits,num_results=num_results,aggs=aggs)
    
    if request.method == 'GET':
        return render_template('index.html',init='True')

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=3000,debug=True)