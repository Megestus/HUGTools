import os
import maya.cmds as cmds
import maya.mel as mel
from functools import partial

# 全局变量
favorites = []
MAX_FAVORITES = 15
ICON_SIZE = 50
COLUMNS = 15
ROWS = 10
WINDOW_NAME = "mayaIconViewer"
INITIAL_LOAD_COUNT = 20  # 初始加载数量
BATCH_SIZE = 50  # 每批加载数量
_script_jobs = []

class IconLoader:
    def __init__(self):
        self.all_icons = []
        self.current_index = 0
        self.is_loading = False
        self.search_term = ""

def create_icon_viewer():
    """创建并显示图标查看器窗口"""
    window_width = COLUMNS * ICON_SIZE

    # 如果窗口已存在，则删除
    if cmds.window(WINDOW_NAME, exists=True):
        cleanup_jobs()  # 清理旧的scriptJobs
        cmds.deleteUI(WINDOW_NAME)

    # 创建主窗口
    window = cmds.window(WINDOW_NAME, title="Maya 图标查看器", width=window_width)
    
    # 添加关闭事件
    cmds.scriptJob(uiDeleted=[window, cleanup_jobs], protected=True)
    
    main_layout = cmds.columnLayout(adjustableColumn=True)

    # 初始化图标加载器
    global icon_loader
    icon_loader = IconLoader()
    
    # 添加UI元素
    create_ui_elements(window_width)
    
    # 开始初始加载
    job_id = cmds.scriptJob(idleEvent=partial(load_more_icons, initial=True), protected=True)
    _script_jobs.append(job_id)  # 保存scriptJob ID
    
    cmds.showWindow(WINDOW_NAME)

def cleanup_jobs():
    """清理所有scriptJobs"""
    global _script_jobs
    for job_id in _script_jobs:
        if cmds.scriptJob(exists=job_id):
            try:
                cmds.scriptJob(kill=job_id, force=True)
            except:
                pass
    _script_jobs = []  # 清空列表

def create_ui_elements(width):
    """创建说明文字"""
    cmds.text(label="单击图标复制名称并添加到收藏夹 - 注意：图标正在逐步加载中...", 
              align="center", font="boldLabelFont", width=width)
    
    # 搜索框
    cmds.textFieldGrp("searchField", label="搜索:", 
                      columnWidth=[(1, 50), (2, width-70)], 
                      changeCommand=update_icons)
    
    # 创建状态栏布局
    status_layout = cmds.rowLayout(numberOfColumns=2, columnWidth2=[width//2, width//2], 
                                 columnAlign2=['left', 'right'])
    
    # 添加当前复制图标显示（改为文本输入框）
    cmds.textFieldGrp("copiedIconName", label="已复制:", 
                      columnWidth=[(1, 50), (2, width//2-70)],
                      text="",  # 初始为空
                      editable=True,  # 允许编辑
                      parent=status_layout)
    
    # 添加加载进度显示
    cmds.text("loadingStatus", label="正在加载初始图标...", align='right', 
             width=width//2, parent=status_layout)
    
    cmds.setParent('..')  # 返回父级布局
    
    create_favorites_area()
    create_icon_grid()

def load_more_icons(initial=False):
    """加载更多图标"""
    if not cmds.window(WINDOW_NAME, exists=True):
        cleanup_jobs()
        return
        
    if icon_loader.is_loading:
        return
        
    icon_loader.is_loading = True
    
    try:
        # 如果是首次加载，获取所有图标列表
        if not icon_loader.all_icons:
            icon_loader.all_icons = cmds.resourceManager(nameFilter="*.png")
            icon_loader.current_index = 0
            
        # 确定本次要加载的数量
        batch_size = INITIAL_LOAD_COUNT if initial else BATCH_SIZE
        end_index = min(icon_loader.current_index + batch_size, len(icon_loader.all_icons))
        
        # 获取当前搜索词
        if cmds.textFieldGrp("searchField", exists=True):
            search_term = cmds.textFieldGrp("searchField", query=True, text=True).lower()
        else:
            cleanup_jobs()
            return
        
        # 加载这一批图标
        icons_added = 0
        for i in range(icon_loader.current_index, end_index):
            icon = icon_loader.all_icons[i]
            if search_term in icon.lower():
                cmds.symbolButton(parent=grid_layout, image=icon, width=45, height=45,
                                command=lambda x, i=icon: handle_click(i), 
                                annotation=icon)
                icons_added += 1
        
        # 更新进度显示
        progress = int((end_index / len(icon_loader.all_icons)) * 100)
        cmds.text("loadingStatus", edit=True, 
                 label=f"已加载: {progress}% ({end_index}/{len(icon_loader.all_icons)})")
        
        # 更新索引
        icon_loader.current_index = end_index
        
        # 调整布局
        if icons_added > 0:
            adjust_layout()
        
        # 如果还有更多图标要加载，继续注册空闲事件
        if icon_loader.current_index < len(icon_loader.all_icons):
            job_id = cmds.scriptJob(idleEvent=load_more_icons, protected=True)
            _script_jobs.append(job_id)
            
    finally:
        icon_loader.is_loading = False

def update_icons(*args):
    """更新图标显示"""
    # 重置加载器状态
    icon_loader.current_index = 0
    icon_loader.search_term = cmds.textFieldGrp("searchField", query=True, text=True).lower()
    
    # 清除现有的图标
    for child in cmds.gridLayout(grid_layout, query=True, childArray=True) or []:
        cmds.deleteUI(child)
    
    # 重新开始加载
    cmds.scriptJob(idleEvent=partial(load_more_icons, initial=True), protected=True)

def create_favorites_area():
    """创建收藏夹区域"""
    cmds.separator(height=10, style='none')  # 添加一些间距
    cmds.text(label="收藏夹", align='left', font="boldLabelFont")
    cmds.separator(height=5, style='none')  # 再添加一些间距
    
    global favorites_layout
    favorites_layout = cmds.rowLayout(numberOfColumns=MAX_FAVORITES+1, 
                                      columnWidth1=45,
                                      adjustableColumn=2,
                                      columnAttach=[(1, 'left', 0), (2, 'left', 0)],
                                      height=50,
                                      backgroundColor=[0.2, 0.2, 0.2])
    
    # 添加星形图标（不可点击）
    cmds.symbolButton(image="SE_FavoriteStar.png", width=45, height=45, 
                      enable=False, annotation="收藏夹：单击图标可以快速复制名称")
    
    # 创建收藏夹图标位置
    for _ in range(MAX_FAVORITES):
        cmds.symbolButton(parent=favorites_layout, width=45, height=45, visible=False)

    cmds.setParent('..')
    cmds.separator(height=10, style='none')  # 添加底部间距

def create_icon_grid():
    """创建图标网格"""
    global scroll_layout, grid_layout
    scroll_layout = cmds.scrollLayout(horizontalScrollBarThickness=16, 
                                    verticalScrollBarThickness=16,
                                    height=ROWS * ICON_SIZE)  # 设置固定高度
    grid_layout = cmds.gridLayout(numberOfColumns=COLUMNS, 
                                 cellWidthHeight=(ICON_SIZE, ICON_SIZE))

def adjust_layout():
    """调整布局大小"""
    visible_icons = len(cmds.gridLayout(grid_layout, query=True, childArray=True) or [])
    total_rows = -(-visible_icons // COLUMNS)  # 向上取整
    scroll_height = min(total_rows * ICON_SIZE, ROWS * ICON_SIZE)
    
    # 设置最小高度
    min_height = 3 * ICON_SIZE  # 至少显示3行
    scroll_height = max(scroll_height, min_height)
    
    # 调整滚动区域高度
    cmds.scrollLayout(scroll_layout, edit=True, height=scroll_height)
    
    # 调整窗口总高度（包括其他UI元素的高度）
    total_height = scroll_height + 180  # 180是其他UI元素的总高度
    cmds.window(WINDOW_NAME, edit=True, height=total_height)

def handle_click(icon):
    """处理图标点击事件"""
    copy_to_clipboard(icon)
    add_to_favorites(icon)
    # 更新当前复制的图标名称显示
    cmds.textFieldGrp("copiedIconName", edit=True, text=icon)

def handle_favorite_click(icon):
    """处理收藏夹图标点击事件"""
    copy_to_clipboard(icon)
    # 更新当前复制的图标名称显示
    cmds.textFieldGrp("copiedIconName", edit=True, text=icon)

def copy_to_clipboard(icon):
    """复制图标名称到剪贴板"""
    os.popen(f'cmd /c echo {icon} | clip')

def add_to_favorites(icon):
    """添加图标到收藏夹"""
    global favorites
    if icon not in favorites:
        if len(favorites) >= MAX_FAVORITES:
            favorites.pop(0)  # 如果收藏夹已满，移除最旧的图标
        favorites.append(icon)
        update_favorites()

def update_favorites():
    """更新收藏夹显示"""
    children = cmds.layout(favorites_layout, query=True, childArray=True)
    for i, child in enumerate(children[1:], 1):  # 跳过第一个子元素（星形图标）
        if i <= len(favorites):
            cmds.symbolButton(child, edit=True, image=favorites[i-1], visible=True,
                              command=lambda x, icon=favorites[i-1]: copy_to_clipboard(icon))
        else:
            cmds.symbolButton(child, edit=True, visible=False)
