import pdfplumber
import re

# 正则表达式匹配中文文本的标题
title_patterns = [
    r'^\d+\、.*$',  # 中文数字开头，后接顿号
    r'^[一二三四五六七八九十]+\、.*$',  # 中文数字开头，后接顿号
    r'^\d+\..*$',                      # 阿拉伯数字开头，后接点号
    r'^[\(\（][一二三四五六七八九十]+[\)\）]$',  # 中文括号包裹的中文数字
    r'^[\(\（]\d+[\)\）].*$',          # 中文括号包裹的阿拉伯数字
    r'^第[一二三四五六七八九十]+[章节条款] [\u4e00-\u9fa5]+'  # “第三节 管理层讨论与分析”格式
]

class PDFExtractor():
    def is_bold(self, text_line):
        first_char = text_line["chars"][0]
        fontname = first_char["fontname"]
        
        # 检查字体名称中是否包含 'Bold' 或类似的术语
        bold_terms = ['Bold', 'Bd', 'Heavy', 'Black']
        return any(bold_term in fontname for bold_term in bold_terms)

    def is_within_table(self, text_line, tables):
        """
        判断文本行是否在表格中。

        :param text_line: 由 page.extract_text_lines() 返回的文本行字典。
        :param tables: 由 page.find_tables() 返回的表格列表。
        :return: 如果文本行在任何表格中，则返回 True；否则返回 False。
        """
        line_bbox = (text_line['x0'], text_line['top'], text_line['x1'], text_line['bottom'])

        for table in tables:
            table_bbox = table.bbox  # 表格的边界框 (x0, top, x1, bottom)
            # 检查文本行和表格边界框是否重叠
            if (line_bbox[0] < table_bbox[2] and
                line_bbox[2] > table_bbox[0] and
                line_bbox[1] < table_bbox[3] and
                line_bbox[3] > table_bbox[1]):
                return True  # 文本行在表格中
                
        return False  # 文本行不在表格中

    def is_title(self, text_line, tables):
        # 检查文本行是否在表格中
        if self.is_within_table(text_line, tables):
            return False

        # 检查文本行是否符合标题模式
        for pattern in title_patterns:
            if re.match(pattern, text_line['text']):
                return True

        return False

    def extract_titles(self, text):
        """
            从多行文本中，正则匹配所有的符合title的标题
            缺陷：因为raw_text缺乏位置信息等，结果不如使用extract方法好
            当前仅用作验证title_patterns单元测试
        """
        # 合并所有模式为一个大模式，并捕获匹配的模式及其在文本中的位置
        combined_pattern = '|'.join(f'({p})' for p in title_patterns)
        matches = re.finditer(combined_pattern, text, re.MULTILINE)

        # 提取匹配的标题及其位置
        titles_with_pos = [(match.group(), match.start()) for match in matches]

        # 根据位置排序
        titles_with_pos.sort(key=lambda x: x[1])

        # 只返回标题
        return [title for title, pos in titles_with_pos]    

    def extract(self, pdf_path):
        pdf = pdfplumber.open(pdf_path) # pdfplumber 提取表格

        titles = []
        page_texts = []
        for page_num, page in enumerate(pdf.pages):
            text_lines = page.extract_text_lines() 
            tables = page.find_tables()
            
            for text_line in text_lines:
                if self.is_title(text_line, tables):
                    titles.append([text_line["text"], page_num + 1])

            page_texts.append(page.extract_text_simple())

        return (titles, page_texts)

if __name__ == "__main__":
    instance = PDFExtractor()
    pdf_path = r'C:\Users\Administrator\Downloads\阿莱德 2022年年度报告摘要.pdf'
    result = instance.extract(pdf_path)
    print(result)