__version__ = "1.0.0"

import scrapy
from scrapy.crawler import CrawlerProcess

#Required Modules
##py -m pip install

#See: https://benbernardblog.com/web-scraping-and-crawling-are-perfectly-legal-right/#generaladviceforyourscrapingorcrawlingprojects
#See: http://doc.scrapy.org/en/1.0/topics/practices.html#bans

#Controllers
def build(*args, **kwargs):
	"""Starts the GUI making process."""

	return Spider(*args, **kwargs)

def runSpider(spiderClass):
	"""Runs the scrapy spider.
	See: https://doc.scrapy.org/en/latest/topics/commands.html
	Use: http://doc.scrapy.org/en/1.0/topics/practices.html#run-scrapy-from-a-script

	spiderClass (scrapy.Spider) - The spider to run

	Example Input: runSpider(__file__)
	"""

	process = CrawlerProcess({
		# 'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
	})

	process.crawl(spiderClass)
	process.start() # the script will block here until the crawling is finished

class Spider():
	def __init__(self, name = None):
		self.object = self.BaseSpider
		self.name = name

	class BaseSpider(scrapy.Spider):
		pass

		@classmethod
		def run(cls):
			runSpider(cls)



class ExampleSpider_1(scrapy.Spider):
	"""An example spider created using this tutorial: https://www.digitalocean.com/community/tutorials/how-to-crawl-a-web-page-with-scrapy-and-python-3 """

	#Use: https://www.digitalocean.com/community/tutorials/how-to-crawl-a-web-page-with-scrapy-and-python-3#step-1-%E2%80%94-creating-a-basic-scraper
	name = "brickset_spider"
	start_urls = ['http://brickset.com/sets/year-2016']

	def parse(self, response):
		"""Parses the data.

		See: http://doc.scrapy.org/en/1.0/topics/spiders.html#scrapy.spiders.Spider.parse
		Use: https://www.digitalocean.com/community/tutorials/how-to-crawl-a-web-page-with-scrapy-and-python-3#step-2-%E2%80%94-extracting-data-from-a-page
		"""

		#<article class='set'>
		SET_SELECTOR = ".set" #If you look at the HTML for the page, you'll see that each set is specified with the class *set*
		for brickset in response.css(SET_SELECTOR):
			#<h1>Brick Bank</h1>
			NAME_SELECTOR = "h1 ::text" #Another look at the source of the page we're parsing tells us that the name of each set is stored within an h1 tag for each set. We append ::text to our selector for the name. That's a CSS pseudo-selector that fetches the text inside of the a tag rather than the tag itself.
			
			#<img src="http://images.brickset.com/sets/small/10251-1.jpg?201510121127" title="10251-1: Brick Bank"></a>
			IMAGE_SELECTOR = "img ::attr(src)" #The image for the set is stored in the src attribute of an img tag inside an a tag at the start of the set. We can use another CSS selector to fetch this value just like we did when we grabbed the name of each set.
			
			# <dl>
			# 	<dt>Pieces</dt>
			# 	<dd><a class="plain" href="/inventories/10251-1">2380</a></dd>
			# 	<dt>Minifigs</dt>
			# 	<dd><a class="plain" href="/minifigs/inset-10251-1">5</a></dd>
			# 	...
			# </dl>
			PIECES_SELECTOR = ".//dl[dt/text() = 'Pieces']/dd/a/text()" #Getting the number of pieces is a little trickier. There's a dt tag that contains the text Pieces, and then a dd tag that follows it which contains the actual number of pieces. We'll use XPath, a query language for traversing XML, to grab this, because it's too complex to be represented using CSS selectors.
			MINIFIGS_SELECTOR = ".//dl[dt/text() = 'Minifigs']/dd[2]/a/text()" #Getting the number of minifigs in a set is similar to getting the number of pieces. There's a dt tag that contains the text Minifigs, followed by a dd tag right after that with the number.
			yield {
				"name": brickset.css(NAME_SELECTOR).extract_first(), #We call extract_first() on the object returned by brickset.css(NAME_SELECTOR) because we just want the first element that matches the selector. This gives us a string, rather than a list of elements.
				"pieces": brickset.xpath(PIECES_SELECTOR).extract_first(),
				"minifigs": brickset.xpath(MINIFIGS_SELECTOR).extract_first(),
				"image": brickset.css(IMAGE_SELECTOR).extract_first(),
			}

		# <li class="next">
		# 	<a href="http://brickset.com/sets/year-2017/page-2">&#8250;</a>
		# </li>
		NEXT_PAGE_SELECTOR = ".next a ::attr(href)" #There's an li tag with the class of next, and inside that tag, there's an a tag with a link to the next page.
		next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
		if (next_page): #All we have to do is tell the scraper to follow that link if it exists
			yield scrapy.Request( #The scrapy.Request is a value that we return saying "Hey, crawl this page"
				response.urljoin(next_page),
				callback = self.parse, #once you’ve gotten the HTML from this page, pass it back to this method so we can parse it, extract the data, and find the next page.
			) #This is the key piece of web scraping: finding and following links. In this example, it’s very linear; one page has a link to the next page until we’ve hit the last page, But you could follow links to tags, or other search results, or any other URL you’d like.

class ExampleSpider_2(scrapy.Spider):
	"""An example spider that logs in, then starts scraping.
	See: http://scrapingauthority.com/2016/11/22/scrapy-login/
	See: http://doc.scrapy.org/en/1.0/topics/request-response.html#topics-request-response-ref-request-userlogin
	See: https://stackoverflow.com/questions/20039643/how-to-scrape-a-website-that-requires-login-first-with-python/31585574#31585574
	See: https://web.archive.org/web/20110517140553/http://dev.scrapy.org/wiki/CommunitySpiders#SilverStripeCMSdemospiderwithloginhandling
	"""

	name = "LoginSpider"
	start_urls = ["http://testing-ground.scraping.pro/login"]

	def parse(self, response):


		# print("!!!!!!!!!!!!!!!!!!!!!!!!!")
		# #See: http://doc.scrapy.org/en/1.0/intro/tutorial.html#introduction-to-selectors
		# form = response.xpath("//form")[0]
		# print(form.xpath("//input"))

		# print("!!!!!!!!!!!!!!!!!!!!!!!!!")



		return scrapy.FormRequest.from_response(
				response,
				formdata = {"usr": "admin", "pwd": "12345"},
				callback = self.after_login,
			)

	def after_login(self, response):
		# check login succeed before going on
		if ("ACCESS DENIED!" in str(response.body)):
			self.logger.error("\nLogin failed\n")
			return

		self.logger.error("\nLogin successful\n")

def sandbox():
	# runSpider(ExampleSpider_1)
	runSpider(ExampleSpider_2)

