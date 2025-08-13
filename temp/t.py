import re
#from str to top left and down right corner
def cast_str_to_num(str):
    
    l = len(str)
    res = 0
    for i in range(l, -1, -1):
        char = str[i]
        n = ord(char) - ord("A")
        res += n * (26 ** (l - i - 1))
        
    return res


def parser(str):
    lst = str.split("(")[1]
    lst = lst.strip(")")
    lst = lst.split(",")
    
    res = []
    
    for coor in lst:
        coor = coor.split(":")
        if len(coor) == 1:
            c = coor[0]
            letters = re.findall(r"^([^\d]+) \d", c)
            number = re.findall(r"\d+$", c)
            col = cast_str_to_num(letters)
            row = int(number)
            res.append(((row, col), (row, col)))
        else:
            c1 = coor[0]
            c2 = coor[1]
            letters1 = re.findall(r"^([^\d]+) \d", c1)
            letters2 = re.findall(r"^([^\d]+) \d", c2)
            number1 = re.findall(r"\d+$", c1)
            number2 = re.findall(r"\d+$", c2)
            col1 = cast_str_to_num(letters1)
            col2 = cast_str_to_num(letters2)
            row1 = int(number1)
            row2 = int(number2)
            res.append(((row1, col1), (row2, col2)))
    return res
            
    


def excelSum(data, formula):
    
    lst_coord = parser(formula)
    sum = 0
    for coor in lst_coord:
        tl, dr = coor
        
        rt, ct = tl[0], tl[1]
        rd, cd = dr[0], dr[1]
        
        for i in range(rt, rd + 1):
            for j in range(ct, cd + 1):
                sum += data[i][j]
    
    return sum





# q2


def spiral(n):
    
    direction = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    d = 0
    step = 1
    changeCnt = 0
    res = [0, 0]
    lst = [(0, 0)]

    
    for i in range(n):
        curr_dir = direction[d]
        for s in range(step):
            res[0] += curr_dir[0]
            res[1] += curr_dir[1]
            lst.append((res[0], res[1]))
        if len(lst) >= n + 1:
            break
        changeCnt += 1
        d += 1
        d %= 4
        if changeCnt == 2:
            step += 1
            changeCnt = 0
        
    return lst[n]

if __name__ == "__main__":
    print(spiral(0))
    print(spiral(1))
    print(spiral(2))
    print(spiral(3))
    print(spiral(10))
    
    
    

WITH temp (SELECT u.name AS name, p.project_id AS project_id
FROM users AS u
JOIN permissions AS p ON u.id = p.user_id)

SELECT t.name
FROM temp AS t
JOIN projects AS p ON t.project_id = p.id
WHERE p.name = "Next-Gen Polymer"


ALTER TABLE user_groups
ADD FOREIGN KEY (PermissionID) REFERENCES permissions(id);