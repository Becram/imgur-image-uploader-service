import json




urls = '''
    {
    "urls": [
        "https://farm3.staticflickr.com/2879/11234651086_681b3c2c00_b_d.jpg",
        "https://farm4.staticflickr.com/3790/11244125445_3c2f32cd83_k_d.jpg"
        ]
    }

'''

def get_urllist(data):
    urls_json = json.loads(data)
    url_list = []
    for value in urls_json['urls']:
        url_list.append(value)
    return url_list



def get_url(x):
	group_urls = []
	url_list = get_urllist(x)
	for url in url_list:
		group_urls.append('upload_image({})'.format(url))
	return group_urls



print(get_url(urls))