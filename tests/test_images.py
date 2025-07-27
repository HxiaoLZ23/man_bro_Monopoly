import pygame
pygame.init()

from src.ui.map_view import MapView
from src.models.map import Map

# 创建测试地图
test_map = Map(5, 5)
map_view = MapView(test_map, 0, 0, 100)

print(f"建筑图片数量: {len(map_view.building_images)}")
print(f"玩家图片数量: {len(map_view.player_images)}")

print("\n已加载的建筑图片:")
for key in map_view.building_images.keys():
    print(f"  - {key}")

print("\n已加载的玩家图片:")
for key in map_view.player_images.keys():
    print(f"  - {key}")

pygame.quit() 