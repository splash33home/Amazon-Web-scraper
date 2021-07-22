# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from priceSpyder.items import PricespyderItem
from scrapy_splash import SplashRequest
from scrapy.loader import ItemLoader


class AmazonpriceSpider(scrapy.Spider):
    name = 'amazonprice'
    allowed_domains = ['www.amazon.com','www.amazon.in']
    items = []
    
    script= '''
        function main(splash,args)
          splash.private_mode_enabled = false
          url = args.url
          assert(splash:go(url))
          assert(splash:wait(1))
          local other_SellerBox = splash:select(".olp-touch-link")
         	if other_SellerBox ~= nil then
            other_SellerBox:mouse_click()
            assert(splash:wait(5))
        	else
          	assert(splash:go(url))
          end
          splash:set_viewport_full()
          return splash:html()
        end
    '''
    def start_requests(self):
        yield SplashRequest(url="https://www.amazon.in/Redmi-Sky-Blue-64GB-Storage/dp/B08697N43N/ref=sr_1_1?dchild=1&keywords=redmi+phone&qid=1618298487&sr=8-1", callback=self.parse, endpoint="execute", args={
         'lua_source': self.script
        })
    
    def parse(self, response):
        #print(response.body)
        sel = Selector(response)
        prodName = ""
        
        #Extract data for product main page using xpath and loaderItem class
        prodName = response.css('#productTitle::text').extract()
        l= ItemLoader(item=PricespyderItem(), selector=sel)
        l.add_value('product_name', prodName)
        l.add_xpath('price', ".//span[@id='priceblock_ourprice']")
        l.add_xpath('company_name', ".//a[@id='sellerProfileTriggerId']")
        yield l.load_item()
        
        
        #Extract other seller if has data using xpath
        
        for othseller in response.xpath("//div[@id='aod-offer-list']/div[@id='aod-offer']"):
            l= ItemLoader(item=PricespyderItem(), selector=othseller)
            l.add_value('product_name', prodName)
            l.add_xpath('price',".//span[@class='a-price-whole']")
            l.add_xpath('company_name',".//div[@id='aod-offer-soldBy']/div[@class='a-fixed-left-grid']/div[@class='a-fixed-left-grid-inner']/div[@class='a-fixed-left-grid-col a-col-right']/a[@class='a-size-small a-link-normal']")
            yield l.load_item()
        
        #yield scraped_info    
