def parse_book(self, selector):
    		book_metas = selector.css('#bookMeta > a::text').getall()
		
		# Notes (contenant `ratings`).
		num_ratings_idx = [i for i,s in enumerate(book_metas) if 'ratings' in s]
		num_ratings_idx = [i for i,s in enumerate(book_metas) if ('ratings' in s or 'rating' in s)]
		if len(num_ratings_idx):
			book_num_ratings = book_metas[num_ratings_idx[0]].replace('\n', '').replace(',', '').replace('ratings', '').strip()
			book_num_ratings = book_metas[num_ratings_idx[0]].replace('\n', '').replace(',', '').replace('ratings', '').replace('rating', '').strip()
		# Avis (contenant `reviews`).
		num_reviews_idx = [i for i,s in enumerate(book_metas) if 'reviews' in s]
		num_reviews_idx = [i for i,s in enumerate(book_metas) if ('reviews' in s or 'review' in s)]
		if len(num_reviews_idx):
			book_num_reviews = book_metas[num_reviews_idx[0]].replace('\n', '').replace(',', '').replace('reviews', '').strip()
			book_num_reviews = book_metas[num_reviews_idx[0]].replace('\n', '').replace(',', '').replace('reviews', '').replace('review', '').strip()
		