import urllib.parse as ullp
class Some:
    def __init__(self):
        self.link = 'http://megamillions.com.ua/wp-content/plugins/youtube-embed-plus/styles/../images/arrow-left.svg'
        self.result_link = 'http://megamillions.com.ua/wp-content/plugins/youtube-embed-plus/images/arrow-left.svg'

    def rm_dot_in_link(self):
        path = ullp.urljoin('http://megamillions.com.ua/wp-content/plugins/youtube-embed-plus/styles/../images/arrow-left.svg', '.')
        file = self.link.split('/')[-1]

        print(path+''.join(file))


some_test = Some()

some_test.rm_dot_in_link()