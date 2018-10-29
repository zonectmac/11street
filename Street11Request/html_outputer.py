class HtmlOutputer(object):
    def __init__(self):
        self.datas = []

    def collect_data(self, new_data):
        if new_data is None:
            return
        self.datas.append(new_data)

    def output_html(self):
        fout = open('putput.html', 'w', encoding="utf-8")
        fout.write("<html>")
        fout.write("<head><meta http-equiv=\"content-type\" content=\"text/html;charset=utf-8\"></head>")
        fout.write("<body>")
        fout.write("<table>")
        for data in self.datas:
            fout.write("<tr>")
            fout.write("<td>%s</td>" % data['link'])
            fout.write("<td>%s</td>" % data['title'])
            fout.write("<td>%s</td>" % data['sale_price'])
            fout.write("<td>%s</td>" % data['mark'])
            fout.write("<td>%s</td>" % data['describe_num'])
            fout.write("<td>%s</td>" % data['collection_num'])
            fout.write("<td>%s</td>" % data['qa_num'])
            fout.write("</tr>")
        fout.write("</table>")
        fout.write("</body>")
        fout.write("</html>")

    def write_txt(self, data):
        with open('output.txt', 'a', encoding='utf-8') as f:
            f.write(data + '\n')
