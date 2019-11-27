import requests

def info():
	libuary = ("requests")
	info = "Download HTTP Files"
	useable = "url,path"
	return(libuary,info,useable)

def run(**args):
	url = args['url']
	filename = url.split("/")[-1]
	path = "c:\\" if not args['path'] else args['path']
	r=requests.get(url).content
	with open(path+'/'+str(filename),'wb') as f:
		print('[*] Downloading File %s'%filename)
		f.write(r)
		f.close()

if __name__ == '__main__':
	run(url="https://img-blog.csdnimg.cn/20190927151132530.png",path="./")