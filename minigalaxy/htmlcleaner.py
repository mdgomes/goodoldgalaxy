from html.parser import HTMLParser

class HTMLCleaner(HTMLParser):
    converted_tags = ("br","li","ol", "p", "h1", "h2", "h3", "h4", "h5")
    supported_tags = ("b","big","i","s","sub","sup","small","tt","u","span")
    supported_span_attrs = ("font_desc","font_family","face", "size", "style", "weight", "variant", "stretch", "foreground", "background", "underline", "rise", "strikethrough", "fallback", "lang")
    
    def __init__(self,html: str):
        HTMLParser.__init__(self)
        self.parsed_str = ""
        self.feed(html.replace("\n","").replace("<br></li>","</li>"))
        self.close()
        
    def handle_starttag(self, tag, attrs):
        aux = tag.lower()
        if tag in self.converted_tags:
            if aux == "br":
                self.parsed_str += '\n'
            elif aux == "li" or aux == "ol":
                self.parsed_str += "\t* "
        if tag not in self.supported_tags:
            return
        if tag.lower() == "span":
            self.parsed_str += "<span "
            for attr in attrs:
                if attr in self.supported_span_attrs:
                    self.parsed_str += attr[0] + "=\""+attr[1]+"\""
            self.parsed_str +=">"
        else:
            self.parsed_str+="<"+aux+">"

    def handle_endtag(self, tag):
        aux = tag.lower()
        if aux == "li" or aux == "ol" or aux == "p" or aux == "h1" or aux == "h2" or aux == "h3" or aux == "h4" or aux == "h5":
            self.parsed_str += "\n"
        if tag not in self.supported_tags:
            return
        self.parsed_str+="</"+aux+">"

    def handle_data(self, data):
        self.parsed_str += data
    
    def get(self) -> str:
        return self.parsed_str.strip().replace("\n\n","\n")
