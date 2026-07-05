import numpy as np
import sys

def rotate_point_xy(point, ax, ay):
    """
    3次元座標を X軸 → Y軸 の順で回転する

    Parameters
    ----------
    point : array-like
        [x, y, z]
    angle_x_deg : float
        X軸回転角度 [deg]
    angle_y_deg : float
        Y軸回転角度 [deg]

    Returns
    -------
    np.ndarray
        回転後の座標
    """

    # X軸回転行列
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(ax), -np.sin(ax)],
        [0, np.sin(ax),  np.cos(ax)]
    ])

    # Y軸回転行列
    Ry = np.array([
        [ np.cos(ay), 0, np.sin(ay)],
        [0,           1, 0],
        [-np.sin(ay), 0, np.cos(ay)]
    ])

    # 点をベクトル化
    p = np.array(point)

    # X → Y の順で回転
    rotated = Ry @ (Rx @ p)

    return rotated

def sphere_circle_intersections(
    sphere_center,
    sphere_radius,
    circle_center,
    circle_radius
):
    """
    球面とXZ平面上の円の交点を求める

    Parameters
    ----------
    sphere_center : [x, y, z]
        球の中心
    sphere_radius : float
        球の半径
    circle_center : [x, y, z]
        円の中心（円はXZ平面）
    circle_radius : float
        円の半径

    Returns
    -------
    list of np.ndarray
        交点リスト（0個, 1個, 2個）
    """

    sx, sy, sz = sphere_center
    cx, cy, cz = circle_center

    # 円は y = cy の平面上
    # 球と平面の交線は円になる

    # 平面と球中心の距離
    dy = cy - sy

    # 球と平面が交差しない
    if abs(dy) > sphere_radius:
        return []

    # 球と平面の交円半径
    r_cross = np.sqrt(sphere_radius**2 - dy**2)

    # XZ平面上での2円交点問題に変換
    # 円1: 球との交円
    # 中心 = (sx, sz), 半径 = r_cross
    #
    # 円2: 元の円
    # 中心 = (cx, cz), 半径 = circle_radius

    p0 = np.array([sx, sz])
    p1 = np.array([cx, cz])

    d = np.linalg.norm(p1 - p0)

    # 交点なし
    if d > r_cross + circle_radius:
        return []

    # 一方が他方を内包
    if d < abs(r_cross - circle_radius):
        return []

    # 同心円
    if d == 0 and r_cross == circle_radius:
        raise ValueError("無限個の交点があります")

    # 円交点計算
    a = (r_cross**2 - circle_radius**2 + d**2) / (2 * d)
    h_sq = r_cross**2 - a**2

    # 数値誤差対策
    if h_sq < 0:
        h_sq = 0

    h = np.sqrt(h_sq)

    p2 = p0 + a * (p1 - p0) / d

    rx = -(p1[1] - p0[1]) * (h / d)
    rz =  (p1[0] - p0[0]) * (h / d)

    intersection1 = np.array([
        p2[0] + rx,
        cy,
        p2[1] + rz
    ])

    intersection2 = np.array([
        p2[0] - rx,
        cy,
        p2[1] - rz
    ])

    # 接する場合
    if np.allclose(intersection1, intersection2):
        return [intersection1]

    return [intersection1, intersection2]

def calc_ankle_angle(ax, ay):

    # inside_heel_point = [-0.058, -0.0285, -0.015]
    # outside_heel_point = [-0.058, 0.0285, -0.015]
    inside_heel_point = [0.0456, 0.0467, -0.008]    #front connector -- lower motor
    outside_heel_point = [-0.0456, 0.0467, -0.008]    #rear connector -- upper motor

    inside_rotated = rotate_point_xy(
        point = inside_heel_point,
        ax=ax,
        ay=ay
    )
    outside_rotated = rotate_point_xy(
        point = outside_heel_point,
        ax=ax,
        ay=ay
    )

    print("回転後:", inside_rotated, outside_rotated)

    #inside
    # sphere_radius = 0.102
    sphere_radius = 0.095    # short lod

    # circle_center = [-0.015, -0.0414, 0.0893]
    # circle_radius = 0.035
    circle_center = [-0.015, 0.0443, 0.0893]    # lower motor
    circle_radius = 0.040

    inside_points = sphere_circle_intersections(
        inside_rotated,
        sphere_radius,
        circle_center,
        circle_radius
    )

    # print("inside")
    # for i, p in enumerate(inside_points):
    #     print(f"交点{i+1}: {p}")
    #     print(np.arccos((circle_center[0] - p[0]) / circle_radius), np.arcsin((circle_center[2] - p[2]) / circle_radius))

    if len(inside_points) == 0:
        return []
    
    p = inside_points[1]
    inside_angle = -np.arcsin((p[2] - circle_center[2]) / circle_radius)
    # if inside_angle < np.pi * 0.5:
    #     inside_angle += np.pi
    # elif inside_angle > np.pi * 0.5:
    #     inside_angle -= np.pi

    #outside
    # sphere_radius = 0.172
    sphere_radius = 0.165     # long lod

    # circle_center = [-0.015, 0.0436, 0.1543]
    # circle_radius = 0.035
    circle_center = [-0.015, 0.0443, 0.1543]   # upper motor
    circle_radius = 0.040

    outside_points = sphere_circle_intersections(
        outside_rotated,
        sphere_radius,
        circle_center,
        circle_radius
    )

    # print("outside")
    # for i, p in enumerate(outside_points):
    #     print(f"交点{i+1}: {p}")
    #     print(np.arccos((circle_center[0] - p[0]) / circle_radius), np.arcsin((circle_center[2] - p[2]) / circle_radius))

    if len(outside_points) == 0:
        return []
    p = outside_points[0]
    outside_angle = np.arcsin((p[2] - circle_center[2]) / circle_radius)

    return inside_angle, outside_angle

def main():
    args = sys.argv
    ax = float(args[1]) #[rad]
    ay = float(args[2]) #[rad]
    inside_angle, outside_angle = calc_ankle_angle(ax, ay)

    print(inside_angle, outside_angle)

if __name__ == '__main__':
    main()
