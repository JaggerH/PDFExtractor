import hashlib
import json
from PDFExtractor import PDFExtractor
from elasticsearch import Elasticsearch

# 创建 Elasticsearch 实例
es = Elasticsearch(['http://localhost:9200'])

def generate_file_hash(filepath):
    with open(filepath, 'rb') as f:
        file_hash = hashlib.sha256()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()

# 将 PDF 内容写入 Elasticsearch
def index_pdf_content(index_name, file_path):
    # 生成doc_id
    doc_id = generate_file_hash(file_path)

    # 读取 PDF 内容
    instance = PDFExtractor()
    (titles, page_texts) = instance.extract(file_path)
    doc = {
        'doc_id': doc_id,
        'title': json.dumps(titles)
    }
    res = es.index(index="pdf_titles", document=doc)

    # print(titles)
    # for page_number, page_text in enumerate(page_texts, start=1):
    #     doc = {
    #         'doc_id': doc_id,
    #         'page_number': page_number,
    #         'page_text': page_text
    #     }
    #     # 索引文档到Elasticsearch
    #     res = es.index(index="pdf_documents", document=doc)

def read_index():
    res = es.search(index="pdf_titles", query={"match_all": {}})
    print("Got %d Hits:" % res['hits']['total']['value'])
    for hit in res['hits']['hits']:
        print("%(doc_id)s: %(title)s" % hit["_source"])

file_path = r'C:\Users\Administrator\Downloads\阿莱德 2022年年度报告摘要.pdf'

# index_pdf_content('index_name', file_path)
read_index()