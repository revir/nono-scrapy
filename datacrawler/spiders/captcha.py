#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytesseract


def crack(image):
    data = image.load()
    width, height = image.size
    color_count = {}
    visited = []

    def bfs(x, y):
        total = [(x, y)]
        visited.append((x, y))

        def check_point(x, y):
            if x >= 0 and x < width and y >= 0 and y < height:
                if not (x, y) in visited:
                    if data[x, y]:
                        visited.append((x, y))
                        total.append((x, y))
                        return data[x, y]

        def search(x, y):
            check_point(x + 1, y)
            check_point(x + 1, y - 1)
            check_point(x, y - 1)
            check_point(x - 1, y - 1)
            check_point(x - 1, y)

            check_point(x - 1, y + 1)
            check_point(x, y + 1)
            check_point(x + 1, y + 1)

        idx = 0
        while True:
            if len(total) > idx:
                x, y = total[idx]
                search(x, y)
                idx += 1
            else:
                break

        if len(total) <= 3 and len(total) > 0:
            for x, y in total:
                c = data[x, y]
                if c not in color_count:
                    color_count[c] = 1
                else:
                    color_count[c] += 1
                data[x, y] = 0

    for y in range(height):
        for x in range(width):
            if data[x, y] and (x, y) not in visited:
                bfs(x, y)
    max_color_item = [0, 0]
    for c, count in color_count.items():
        if count > max_color_item[1] and count > 10:
            max_color_item[0] = c
            max_color_item[1] = count

    if max_color_item[0] and max_color_item[1]:
        for y in range(height):
            for x in range(width):
                if data[x, y] == max_color_item[0]:
                    data[x, y] = 0

    text = pytesseract.image_to_string(image)
    text = filter(str.isalnum, text)
    return text

if __name__ == '__main__':
    # test
    from PIL import Image
    img = Image.open('/Users/Revir/Temp/1.png')
    print crack(img)
