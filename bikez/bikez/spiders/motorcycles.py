import scrapy

class MotorcyclesSpider(scrapy.Spider):
    name = "motorcycles"
    allowed_domains = ["bikez.com"]
    start_urls = ["https://bikez.com/brands/index.php"]

    def parse(self, response):
        all_brands_even = response.selector.xpath("//td[@class='even']//a/@href").getall()
        all_brands_odd = response.selector.xpath("//td[@class='odd']//a/@href").getall()
        all_brands = all_brands_even + all_brands_odd
        yield from response.follow_all(all_brands, self.parse_models)

    def parse_models(self, response):
        all_bikes_list_url = response.selector.xpath("//*[contains(text(), 'list all')]/@href").get()
        yield response.follow(all_bikes_list_url, self.parse_all_bikes)

    def parse_all_bikes(self, response):
        all_bikes_odd = response.selector.xpath("//table[@class='zebra']//tr[@class='odd']//a/@href").getall()[::2]
        all_bikes_even = response.selector.xpath("//table[@class='zebra']//tr[@class='even']//a/@href").getall()[::2]
        all_bikes = all_bikes_odd + all_bikes_even
        yield from response.follow_all(all_bikes, self.parse_bike)
        
        pagination_buttons = response.selector.xpath("//table[@class='zebra']//td[@colspan='3']//a").getall()
        if len(pagination_buttons) > 0:
            next_page_button_text = response.selector.xpath("//table[@class='zebra']//td[@colspan='3']//a/text()").getall()[-1]
            if 'next' in next_page_button_text.lower():
                next_page_url = response.selector.xpath("//table[@class='zebra']//td[@colspan='3']//a/@href").getall()[-1]
                yield response.follow(next_page_url, self.parse_all_bikes)

    def parse_bike(self, response):
        
        def normalize_spaces(text):
            text = text.replace("\n", "").replace("\t", "").replace("\r", "").strip()
            return text
        
        def join_text(text_list):
            return " ".join([normalize_spaces(text) for text in text_list]) 

        def extract_specs(table):
            specs = table.xpath(".//tr")
            specs_dict = {}
            for spec in specs:
                spec_name = join_text(spec.xpath(".//td[1]//b/text()").getall())
                spec_value = join_text(spec.xpath(".//td[2]//text()").getall())
                if type(spec_value) == list:
                    spec_value = " ".join(spec_value)
                
                specs_dict[spec_name] = spec_value
            return specs_dict
    
        print(response.url)
        bike_model = response.selector.xpath("//h1/text()").get()
        bike_brand = response.selector.xpath("//h1/a/text()").getall()[0]
        bike_year = response.selector.xpath("//h1/a/text()").getall()[-1]
        tables = response.selector.xpath("//table[@class='Grid']")
        specs_table = response.selector.xpath(
                "//table[@class='Grid']//div[@id='GENERAL']/../../.."
                )
    
        if len(tables) < 1:
            return
        elif len(tables) == 1:
            
            bike_specs_dict = extract_specs(specs_table)
            yield {
                'model': bike_model,
                'brand': bike_brand,
                'year': bike_year,
                'specs': bike_specs_dict
            }
        else:
            
            bike_specs_dict = extract_specs(specs_table)
            bike_profile = response.xpath("//*[contains(text(), 'profilation')]/../../..//tr[2]//text()").get()
            yield {
                'model': bike_model,
                'brand': bike_brand,
                'year': bike_year,
                'profile': bike_profile,
                'specs': bike_specs_dict
            }
