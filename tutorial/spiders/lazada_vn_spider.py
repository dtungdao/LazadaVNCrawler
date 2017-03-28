# -*- coding: utf-8 -*-
import scrapy


class ToScrapeSpiderXPath(scrapy.Spider):
	name = 'lazada_vn_spider'
	
	#start_urls = ['http://www.lazada.vn/tui-tote-nu/?page=48&setLang=en']
	
	def __init__(self, url='', action='product', index='', *args, **kwargs):
		super(ToScrapeSpiderXPath, self).__init__(*args, **kwargs)
		
		if(url[-1] == '/'): url = url + "?setLang=en"
		else: url = url + "&setLang=en"
		self.start_urls = [url]
				
		self.action = action
		self.page_idx = index
		self.deep = 0
		
		self.out_file1 = None
		self.out_file2 = None
		
	def parse(self, response):	
		if(self.action == 'product'):
			if(self.out_file1 == None):
				self.out_file1 = open(r"C:\Users\ddtkh\Desktop\LazadaVN_Output\%s_%s_Product.csv" % (self.page_idx, response.url.split('/')[3].replace("-", "_")), "wt")
			self.out_file1.write("ID, Product Name, Rating, No of Review, Product Price, Product Old, Discount, Link To Product, %s\n" % (response.url))
		
			self.ProductParser(response, self.out_file1)
			
			next_page_url = response.xpath('//a[@title="next page"]/@href').extract_first()
			self.deep += 1
			if next_page_url is not None and self.deep <= 3:
				yield scrapy.Request(response.urljoin(next_page_url))
			else:
				self.out_file1.close()
		elif(self.action == 'pannel'):
			self.out_file2 = open(r"C:\Users\ddtkh\Desktop\LazadaVN_Output\%s_%s_Pannel.csv" % (self.page_idx, response.url.split('/')[3].replace("-", "_")), "wt")
			self.PannelParser(response, self.out_file2)
			self.out_file2.close()
		else:
			self.logger.info('Not recognize action: %s', self.action)
			
	def ProductParser(self, response, out_file):
		item_cnt = 0
		wrong_struct = True
	
		for quote in response.xpath('//div[contains(@class,"c-product-card c-product-list__item   c-product-card_view_grid")]'):
			name = quote.xpath('.//a[@class="c-product-card__name"]/text()').extract_first()
			name = name.strip().encode("utf-8").replace("\n", " ").replace("\r", " ") if name != None else None
			
			rating = quote.xpath('.//div[@class="c-rating-stars  c-product-card__rating-stars "]/@data-value').extract_first()
			rating = rating.strip().encode("utf-8") if rating != None else None
			
			review = quote.xpath('.//div[@class="c-product-card__review-num"]/text()').re_first('\d+')
			review = review.strip().encode("utf-8") if review != None else 0
			
			price_after = quote.xpath('.//span[@class="c-product-card__price-final"]/text()').extract_first()
			price_after = price_after.strip().encode("utf-8") if price_after != None else None
			
			price_before = quote.xpath('.//div[@class="c-product-card__old-price"]/text()').extract_first()
			price_before = price_before.strip().encode("utf-8") if price_before != None else None
			
			discount = quote.xpath('.//span[@class="c-product-card__discount"]/text()').extract_first()
			discount = discount.strip().encode("utf-8") if discount != None else "0%"
			
			link = quote.xpath('.//a[@class="c-product-card__name"]/@href').extract_first()
			link = "http://www.lazada.vn" + link.strip().encode("utf-8") if link != None else None
			
			item_cnt = item_cnt + 1
			
			out_file.write('"%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s"\n' % (item_cnt, name, rating, review, price_before, price_after, discount, link))
			#yield{'id' : item_cnt,'name' : name, 'price' : price, 'discount' : discount}
		
			wrong_struct = False
		
		if(wrong_struct):
			self.logger.info('Wrong struct foun in %s', response.url)
		
	def PannelParser(self, response, out_file):		
		for quote in response.xpath('//div[@class="c-sidebar"]/form/div[@class="c-sidebar__section"]'):
			section = quote.xpath('./div[contains(@class,"c-sidebar__title")]/text()').extract_first()
			section = section.strip().encode("utf-8") if section != None else None
			if(section != None and section != "Price (in VND)" and section != "Product rating"):
				out_file.write("\n### %s\n" % (section))
				
				# REFINE BY CATEGORY
				#def __loop(section):
				#	print(section)
				#	if((section) != 'list'): section = [section]
				#	for sub_section in section:
				#		temp1 = sub_section.xpath('.//a[@href]/text()').extract_first()
				#		temp1 = temp1.strip().encode("utf-8") if temp1 != None else None
				#		
				#		temp2 = sub_section.xpath('.//span[@class="c-catalog-nav__facet-counter"]/text()').extract_first()
				#		temp2 = temp2.strip().encode("utf-8").replace("(", "").replace(")", "")  if temp2 != None else None
				#		
				#		out_file.write("\"- %s: %s\"\n" % (temp1, temp2))
				#		
				#		if(len(sub_section.xpath("./ul")) == 0): return
				#		__loop(sub_section.xpath('./ul[@class="c-catalog-nav__list"]/li'))
				#		
				#__loop(quote.xpath('.//div[@class="c-catalog-nav "]/ul[@class="c-catalog-nav__list"]/li'))
				for sub_section in quote.xpath('.//ul[@class="c-catalog-nav__list"]/li'):
					if(len(sub_section.xpath("./ul")) == 0):
						temp1 = sub_section.xpath(".//a[@href]/text()").extract_first()
						temp1 = temp1.strip().encode("utf-8") if temp1 != None else None
						
						temp2 = sub_section.xpath('.//span[@class="c-catalog-nav__facet-counter"]/text()').extract_first()
						temp2 = temp2.strip().encode("utf-8").replace("(", "").replace(")", "")  if temp2 != None else None
						
						out_file.write("\"- %s: %s\"\n" % (temp1, temp2))
				
				# Normal ones
				for sub_section in quote.xpath('.//span[@class="c-form-control-checkbox__custom-label"]'):
					temp = sub_section.xpath('.//text()').extract()
					if(temp != None):
						temp[0] = temp[0].strip().encode("utf-8")
						temp[1] = temp[1].encode("utf-8").replace("(", "").replace(")", "")
					
					out_file.write("- %s: %s\n" % (temp[0], temp[1]))
					
				# COLOR
				for sub_section in quote.xpath('.//div[@data-qa-locator=""]'):
					temp1 = sub_section.xpath('.//span[@class="c-dropdown__caption"]/div/input/@value').extract_first()
					temp1 = temp1.strip().encode("utf-8") if temp1 != None else None
					
					temp2 = sub_section.xpath('.//div[@class="c-dropdown__popup"]/div/span/text()').extract_first()
					temp2 = temp2.strip().encode("utf-8").replace("(", "").replace(")", "") if temp2 != None else None
					
					out_file.write("- %s: %s\n" % (temp1, temp2))