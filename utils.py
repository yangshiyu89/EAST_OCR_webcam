import numpy as np

def decode_predictions(scores, geometry):
    
    # 函数作用：将 EAST 网络提取到的文字框以及对应的 confidence score 解析出来。
    # 解析出来的检索框为水平矩形，为后续抑制非最大值框提取候选区域。
     
    # ------
    
    # 输入：
    # scores   -- EAST 网络 confidence score 
    # geometry -- 检索框几何信息
    
    # 输出：
    # (候选框, confidence scores)
    
    # ------
    
    # 根据网络结构提取最后的 scores 矩阵。
    # 网络结构为 （1, 1, rows, cols）其中 rows = cols 并且为输入图像的 1/4
    (numRows, numCols) = scores.shape[2:]
    
    rects = []
    confidences = []

    # 循环每一行
    for y in range(0, numRows):
        # 根据网络结构提取 confidence sore 以及几何位置信息。
        
        # confidence sore 只有一行信息。
        scoresData = scores[0, 0, y]
        
        # 几何信息有 5 行信息。其中，前 4 行为位置像素距离各边的距离，第 5 行为边框的旋转角度。
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        # 循环每一列
        for x in range(0, numCols):
            # 如果我们的 confidence sore 小于 0.5，那么跳过，说明这个像素并不会有检测框。
            if scoresData[x] < 0.5:
                continue

            # 计算补偿距离
            # feature map 映射到输入尺度应该 ×4。
            (offsetX, offsetY) = (x * 4.0, y * 4.0)

            # 提取矩形旋转角度并计算 cos 与 sin 值。
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)

            # 计算水平候选框的高度与宽度
            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            # 计算水平候选框的起点（左上角）以及终点（右下角）。
            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            # 加入到候选框列表中
            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])

    return (rects, confidences)
