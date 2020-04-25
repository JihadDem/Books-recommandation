import flask
from api import BookSimilarity

app = flask.Flask(__name__)
booksim = BookSimilarity()

@app.route('/')
def index():
	return flask.render_template('index.html')

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
	search = flask.request.args.get('q')
	books = ["The Canterbury Tales", "The Things They Carried", "Cloud Atlas", "The Eyre Affair", "The Corrections", "On Writing: A Memoir of the Craft", "The Tin Drum", "Where the Red Fern Grows", "Stones from the River", "Under the Never Sky", "The Warded Man", "The Sirens of Titan", "Lisey's Story", "The King of Attolia", "Nevermore", "London", "As You Like It", "I've Got Your Number", "Carpe Corpus", "The Runaway Bunny", "Wyrd Sisters"]
	filtered_books = [b for b in books if search in b.lower()]
	filtered_books = list(booksim.search(search)['title'].values)
	return flask.jsonify(matching_results=filtered_books)

@app.route('/recommend')
def recommend():
	# Dynamic page help:
	# https://stackoverflow.com/questions/40963401/flask-dynamic-data-update-without-reload-page/40964086

	searchText = flask.request.args.get('jsdata')

	output = []
	if searchText:
		print(f'Search text: {searchText}')
		results = booksim.recommend(searchText)
		if results is not None:
			output = results.title.values
			print(output)

	# TODO: Convert a fuller version to JSON rather than just an array (title, url, etc.) and render as a table instead.
	# https://stackoverflow.com/questions/48050769/pandas-dataframe-to-flask-template-as-a-json
	return flask.render_template('results.html', recommendations=output) 

def autocomplete():
    	search = flask.request.args.get('q')
	books = ["The Canterbury Tales", "The Things They Carried", "Cloud Atlas", "The Eyre Affair", "The Corrections", "On Writing: A Memoir of the Craft", "The Tin Drum", "Where the Red Fern Grows", "Stones from the River", "Under the Never Sky", "The Warded Man", "The Sirens of Titan", "Lisey's Story", "The King of Attolia", "Nevermore", "London", "As You Like It", "I've Got Your Number", "Carpe Corpus", "The Runaway Bunny", "Wyrd Sisters"]
	filtered_books = [b for b in books if search in b.lower()]
	filtered_books = [b for b in books if search.lower() in b.lower()]
	return flask.jsonify(matching_results=filtered_books) 