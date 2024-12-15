from pandas import to_numeric
from prettytable import PrettyTable
from wcwidth import wcswidth  

def to_prettytable(objects, attributes):
    table = PrettyTable()
    table.field_names = attributes
    for obj in objects:
        table.add_row([getattr(obj, attr) for attr in attributes])    
    return table

def adjust_cell(cell, max_width):
    """
    셀의 내용을 max_width에 맞게 자르고, 폭이 초과하면 '…' 추가
    """
    cell_width = wcswidth(cell)  # 실제 출력 폭 계산
    if cell_width > max_width:
        # 문자열을 최대 너비에 맞게 정확히 자르기
        truncated = ""
        current_width = 0
        for char in cell:
            char_width = wcswidth(char)
            if current_width + char_width > max_width - 1:  # 마지막 1칸은 '…'에 사용
                break
            truncated += char
            current_width += char_width
        return truncated + "…"  # '…' 추가
    else:
        # 폭이 부족하면 공백으로 채우기
        return cell + " " * (max_width - cell_width)

def to_agent_table(objects, attributes):
    # object to prettytable
    table = to_prettytable(objects, attributes)
    rows = table.rows
    new_table = PrettyTable()

    # field name
    field_names = table.field_names[:]
    if "is_completed" in field_names:
        is_completed_idx = field_names.index("is_completed")
        field_names[is_completed_idx] = "-"
        for row in rows:
            row[is_completed_idx] = "O" if row[is_completed_idx] else "X"

    if "title" in field_names:
        title_width = 40
        title_idx = field_names.index("title")
        for row in rows:
            row[title_idx] = adjust_cell(row[title_idx], title_width)
        new_table.max_width["title"] = title_width + 3

    new_table.field_names = field_names   

    if "price" in field_names:
        new_table.align["price"] = "r"  # 오른쪽 정렬 (right)
        price_idx = field_names.index("price")
        for row in rows:
            row[price_idx] =  f"{to_numeric(row[price_idx]):,}"
        

    new_table.add_rows(rows)
    return new_table
    

