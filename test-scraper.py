import os
import re
import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess

class GoodReadsSpider(scrapy.Spider):
	name = 'goodreads_spider'
	download_delay = 0.25 

	def start_requests(self):
		for page_id in range(START_PAGE, END_PAGE+1):
			page_url = f'https://www.goodreads.com/list/show/1.Best_Books_Ever?page={page_id}'
			yield scrapy.Request(url=page_url, callback=self.parse_page)
		
	

	def parse_page(self, selector):
		# extraire toutes les `bookTitle`, qui sont les titres/liens des livres de la liste.
		all_book_titles = selector.css('a.bookTitle')
		for curr_book in all_book_titles:
			book_link = curr_book.attrib['href']
			book_url = f'https://www.goodreads.com{book_link}'
			yield selector.follow(url=book_url, callback=self.parse_book)
		
	

	def parse_book(self, selector):
		# Valeur à remplir.
		book_title = None
		book_orig_title = None # titre du livre dans sa langue originale.
		book_series = None
		book_language = None
		book_authors = []
		book_avg_rating = None
		book_num_ratings = None
		book_num_reviews = None
		book_genres = []
		book_description = ''

		# titre livre.
		book_title = selector.css('h1#bookTitle::text').get()
		book_title = None if book_title is None else book_title.strip()

		# chaqude livre à sa metadat.
		book_data = selector.css('#bookDataBox > div.clearFloats')
		for data in book_data:
			
			row_title = data.css('.infoBoxRowTitle::text').get()

			# titre livre langue orginial.
			if 'Original Title' == row_title:
				book_orig_title = data.css('.infoBoxRowItem::text').get()
				book_orig_title = None if book_orig_title is None else book_orig_title.strip() # Cleanup.
			

			# Series.
			if 'Series' == row_title:
				book_series = data.css('.infoBoxRowItem > a::text').get()
				hash_idx = book_series.find('#')
				if hash_idx != -1:
					book_series = book_series[:hash_idx-1]
				
			

			# Language.
			if 'Edition Language' == row_title:
				book_language = data.css('.infoBoxRowItem::text').get()
				book_language = None if book_language is None else book_language.strip()
			#end
		#end

		# Author(s).  plusieurs peubent etre listé.
		for author in selector.css('.authorName__container'):
			author_name = author.css('a > span::text').get()
			author_role = author.css('.role::text').get()
			# ajouter l'auteur ou bien son role aussi.
			book_authors.append(author_name if author_role is None else ' '.join([author_name, author_role]))
		

		# note sur ?/5.
		book_avg_rating = selector.css('span[itemprop="ratingValue"]::text').get()
		if book_avg_rating != None:
			book_avg_rating = book_avg_rating.strip()

		
		# la seule solution ici est de récupérer tous les enfants et de trouver ceux qui contiennent des `ratings` et des `reviews` 
		book_metas = selector.css('#bookMeta > a::text').getall()
		
		# Notes (contenant `ratings`).
		num_ratings_idx = [i for i,s in enumerate(book_metas) if 'ratings' in s]
		if len(num_ratings_idx):
			book_num_ratings = book_metas[num_ratings_idx[0]].replace('\n', '').replace(',', '').replace('ratings', '').strip()
		# Avis (contenant `reviews`).
		num_reviews_idx = [i for i,s in enumerate(book_metas) if 'reviews' in s]
		if len(num_reviews_idx):
			book_num_reviews = book_metas[num_reviews_idx[0]].replace('\n', '').replace(',', '').replace('reviews', '').strip()
		

		# Genre(s).
		book_genres = selector.css('div.left > a.bookPageGenreLink::text').getall()

		# Description
		desc_texts = self.process_book_description(selector.xpath('//*[@id="description"]/span[contains(@style, "display:none")]/node()').getall())
		book_description = ' '.join(desc_texts)
		# `display:none` n'est présent que lorsque l'aperçu doit être rallongé.
		if not len(book_description):
			desc_texts = self.process_book_description(selector.xpath('//*[@id="description"]/span/node()').getall())
			book_description = ' '.join(desc_texts)


		## Verif des erreus.
		# Oubli title.
		if None == book_title:
			print(f'Error: Missing book title ({selector.url}).')
			return
		# Titre original.
		if None == book_orig_title:
			print(f'Warning: Missing book original title ({selector.url}).')
		# Series.
		if None == book_series:
			print(f'Warning: Book missing series ({selector.url}).')
		# Language.
		if None == book_language:
			print(f'Warning: Book missing language ({selector.url}).')
		# Authors.
		if not len(book_authors):
			print(f'Warning: Book missing authors ({selector.url}).')
		# Average rating.
		if None == book_avg_rating:
			print(f'Warning: Book missing average rating ({selector.url}).')
		# Nombre de notes.
		if None == book_num_ratings:
			print(f'Warning: Book missing number of ratings ({selector.url}).')
		# Nombre d'avis.
		if None == book_num_reviews:
			print(f'Warning: Book missing number of reviews ({selector.url}).')
		# Genres.
		if not len(book_genres):
			print(f'Warning: Book missing genres ({selector.url}).')
		# Description.
		if not len(book_description):
			print(f'Warning: Book missing description ({selector.url}).')

		# remplir.
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
		book_df['url'] = selector.url .

		
		global all_books_df
		all_books_df = pd.concat([all_books_df, book_df], sort=False)
	

	def process_book_description(self, spans):
		
		texts = []

		for desc_span in spans:
			desc_text = desc_span.strip()
			# enelever les new lignes.
			desc_text = desc_text.replace('\n', '')
			# enelver les tabs si je les met dans TSV.
			desc_text = desc_text.replace('\t', ' ')
			
			desc_text = re.sub(r"<[^>]*>", '', desc_text)

			
			if len(desc_text):
				texts.append(desc_text)
		

		return texts
	


# choix de la page
START_PAGE = 1
END_PAGE = 100

all_books_df = pd.DataFrame()

process = CrawlerProcess()
process.crawl(GoodReadsSpider)
process.start()

# TSV.
output_tsv = f'./output/pages-{START_PAGE}-{END_PAGE}.tsv'
all_books_df.to_csv(output_tsv, index=False, sep='\t')

# CSV.
output_csv = f'./output/pages-{START_PAGE}-{END_PAGE}.csv'
all_books_df.to_csv(output_csv, index=False)


