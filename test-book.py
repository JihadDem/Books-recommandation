import os
import re
import scrapy
import pandas as pd

def process_book_description(spans):
	
	texts = []

	for desc_span in spans:
		desc_text = desc_span.strip()
		
		desc_text = desc_text.replace('\n', '')
		
		desc_text = desc_text.replace('\t', ' ')
		
		desc_text = re.sub(r"<[^>]*>", '', desc_text)

		
		if len(desc_text):
			texts.append(desc_text)
	

	return texts


def parse_book(filename):
	with open(filename, 'r') as file:
		selector = scrapy.Selector(text=file.read())
	

	
	book_title = None
	book_orig_title = None 
	book_series = None
	book_language = None
	book_authors = []
	book_avg_rating = None
	book_num_ratings = None
	book_num_reviews = None
	book_genres = []
	book_description = ''

	
	book_title = selector.css('h1#bookTitle::text').get()
	book_title = None if book_title is None else book_title.strip()

	
	book_data = selector.css('#bookDataBox > div.clearFloats')
	for data in book_data:
		
		row_title = data.css('.infoBoxRowTitle::text').get()

		
		if 'Original Title' == row_title:
			book_orig_title = data.css('.infoBoxRowItem::text').get()
			book_orig_title = None if book_orig_title is None else book_orig_title.strip() # Cleanup.
	

		
		if 'Series' == row_title:
			book_series = data.css('.infoBoxRowItem > a::text').get()
			hash_idx = book_series.find('#')
			if hash_idx != -1:
				book_series = book_series[:hash_idx-1]
			
		

		
		if 'Edition Language' == row_title:
			book_language = data.css('.infoBoxRowItem::text').get()
		
	

	
	for author in selector.css('.authorName__container'):
		author_name = author.css('a > span::text').get()
		author_role = author.css('.role::text').get()
		
		book_authors.append(author_name if author_role is None else ' '.join([author_name, author_role]))
	

	
	book_avg_rating = selector.css('span[itemprop="ratingValue"]::text').get().strip()

	
	book_metas = selector.css('#bookMeta > a::text').getall()
	
	num_ratings_idx = [i for i,s in enumerate(book_metas) if 'ratings' in s]
	if len(num_ratings_idx):
		book_num_ratings = book_metas[num_ratings_idx[0]].replace('\n', '').replace(',', '').replace('ratings', '').strip()
	
	num_reviews_idx = [i for i,s in enumerate(book_metas) if 'reviews' in s]
	if len(num_reviews_idx):
		book_num_reviews = book_metas[num_reviews_idx[0]].replace('\n', '').replace(',', '').replace('reviews', '').strip()
	

	
	book_genres = selector.css('div.left > a.bookPageGenreLink::text').getall()

	
	desc_texts = process_book_description(selector.xpath('//*[@id="description"]/span[contains(@style, "display:none")]/node()').getall())
	book_description = ' '.join(desc_texts)
	
	if not len(book_description):
		desc_texts = process_book_description(selector.xpath('//*[@id="description"]/span/node()').getall())
		book_description = ' '.join(desc_texts)


	
	book_df = pd.DataFrame()
	book_df['title'] = [book_title]
	book_df['original_title'] = [book_orig_title]
	book_df['series'] = [book_series]
	book_df['language'] = [book_language]
	book_df['authors'] = ','.join(book_authors)
	book_df['avg_rating'] = book_avg_rating
	book_df['num_ratings'] = book_num_ratings
	book_df['num_reviews'] = book_num_reviews
	book_df['genres'] = ','.join(book_genres)
	book_df['description'] = book_description

	


	# Debug print.
	print(f'Title: {book_title}')
	print(f'Original title: {book_orig_title}')
	print(f'Series: {book_series}')
	print(f'Language: {book_language}')
	print(f'Authors: {book_authors}')
	print(f'Average rating: {book_avg_rating}')
	print(f'No. ratings: {book_num_ratings}')
	print(f'No. reviews: {book_num_reviews}')
	print(f'Genres: {book_genres}')
	print(f'Description: {book_description}')
	print()


# parse_book('./book_1.html')
# parse_book('./book_2.html')
# parse_book('./book_3.html')
# parse_book('./book_4.html')
# parse_book('./book_5.html')
# parse_book('./book_6.html')
parse_book('./book_7.html') 