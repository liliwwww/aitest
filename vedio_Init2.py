
import time
import numpy as np
import cv2
import numpy as np
from typing import Tuple, List, Dict, Any
from skimage.metrics import structural_similarity as ssim


def crop_image(image_path: str, coordinates: Tuple[int, int, int, int]) -> np.ndarray:
    """
    从指定路径的图片中截取指定区域
    
    参数:
        image_path: 图片路径
        coordinates: 截取区域坐标 (x1, y1, x2, y2)
    
    返回:
        截取的图像区域
    """
    x1, y1, x2, y2 = coordinates
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"无法读取图片: {image_path}")
    
    # 确保坐标有效
    if x1 >= x2 or y1 >= y2:
        raise ValueError(f"无效的坐标: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
    
    if x1 < 0: x1 = 0
    if y1 < 0: y1 = 0
    if x2 > image.shape[1]: x2 = image.shape[1]
    if y2 > image.shape[0]: y2 = image.shape[0]
    
    return image[y1:y2, x1:x2]

def compare_image_regions(
    image1_path: str, 
    image2_path: str, 
    coordinates: Tuple[int, int, int, int],
    method: str = "mse"
) -> Dict[str, Any]:
    """
    比较两张图片相同区域的差异度
    
    参数:
        image1_path: 第一张图片路径
        image2_path: 第二张图片路径
        coordinates: 截取区域坐标 (x1, y1, x2, y2)
        method: 比较方法，可选 'mse' (均方误差), 'ssim' (结构相似性), 'hist' (直方图比较)
    
    返回:
        包含不同比较方法结果的字典
    """
    path = fr"D:\Users\wdp\Pictures\\"
    # 截取区域
    region1 = crop_image(path+image1_path, coordinates)
    region2 = crop_image(path+image2_path, coordinates)
    
    # 确保两张图片尺寸一致
    if region1.shape != region2.shape:
        region2 = cv2.resize(region2, (region1.shape[1], region1.shape[0]))
    
    results = {}
    
    # 1. 计算均方误差 (MSE)
    # 值越小表示越相似，0表示完全相同
    err = np.sum((region1.astype("float") - region2.astype("float")) ** 2)
    err /= float(region1.shape[0] * region1.shape[1])
    results['mse'] = err
    
    # 2. 计算结构相似性指数 (SSIM)
    # 值范围从-1到1，1表示完全相同
    if method == "ssim" or method == "all":
        
        # 转换为灰度图计算SSIM
        gray1 = cv2.cvtColor(region1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(region2, cv2.COLOR_BGR2GRAY)
        ssim_score = ssim(gray1, gray2)
        results['ssim'] = ssim_score
    
    # 3. 计算直方图相似度
    # 值范围从0到1，1表示完全相同
    if method == "hist" or method == "all":
        hist1 = cv2.calcHist([region1], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist2 = cv2.calcHist([region2], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist1 = cv2.normalize(hist1, hist1).flatten()
        hist2 = cv2.normalize(hist2, hist2).flatten()
        hist_score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        results['hist'] = hist_score
    
    # 4. 生成差异图像
    diff_image = cv2.absdiff(region1, region2)
    
    return {
        'comparison_results': results,
        'region1': region1,
        'region2': region2,
        'diff_image': diff_image
    }

# 示例使用
if __name__ == "__main__":
    # 定义截取区域坐标 (x1, y1, x2, y2)
    coordinates = (561, 114, 581, 150)  # 例如：从(1034,100)到(300,300)的矩形区域
    

    # 比较两张图片的指定区域
    result = compare_image_regions(
        "vlcsnap1.png", 
        "vlcsnap2.png", 
        coordinates,
        method="all"
    )
    
    # 打印比较结果
    print("比较结果:")
    for method, score in result['comparison_results'].items():
        print(f"{method.upper()}: {score:.4f}")
    
    # 显示图像（可选）
    cv2.imshow("Region 1", result['region1'])
    cv2.imshow("Region 2", result['region2'])
    cv2.imshow("Difference", result['diff_image'])
    cv2.waitKey(0)
    cv2.destroyAllWindows()    