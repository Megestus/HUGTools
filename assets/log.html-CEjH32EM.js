import{_ as e}from"./plugin-vue_export-helper-DlAUqK2U.js";import{c as i,a as o,o as a}from"./app-DUQ4LdGU.js";const t={};function n(s,l){return a(),i("div",null,l[0]||(l[0]=[o('<h3 id="版本-1-0-2" tabindex="-1"><a class="header-anchor" href="#版本-1-0-2"><span>版本 1.0.2</span></a></h3><ul><li>发布日期: 2024-10-23</li></ul><h4 id="新功能" tabindex="-1"><a class="header-anchor" href="#新功能"><span>新功能</span></a></h4><ol><li>工具箱增添&quot;更多&quot;按钮 <ul><li>打开独立窗口,展示3x3网格的额外工具</li><li>在新模块 <code>More_Tools_Module.py</code> 中实现</li></ul></li></ol><h4 id="功能改进" tabindex="-1"><a class="header-anchor" href="#功能改进"><span>功能改进</span></a></h4><ol><li>语言切换按钮优化,现可在中英文间切换显示 &quot;CN&quot; 和 &quot;EN&quot;</li><li>文件读取操作新增 CP437 编码支持</li><li>安装过程错误处理和日志记录得到改进</li></ol><h4 id="界面更新" tabindex="-1"><a class="header-anchor" href="#界面更新"><span>界面更新</span></a></h4><ol><li>主界面布局重组 <ul><li>&quot;选择控制&quot;功能独立成组</li><li>工具箱按钮重排为2x2网格布局</li></ul></li></ol><h4 id="代码优化" tabindex="-1"><a class="header-anchor" href="#代码优化"><span>代码优化</span></a></h4><ol><li>&quot;更多&quot;工具功能移至独立模块,提升可维护性</li><li>全面更新代码注释,提高可读性</li><li><code>Editor_Rename_Module.py</code> 中文注释全部翻译为英文</li></ol><h4 id="问题修复" tabindex="-1"><a class="header-anchor" href="#问题修复"><span>问题修复</span></a></h4><ol><li>解决语言切换未更新所有UI元素的问题</li><li>修复不同系统环境下的编码相关错误</li><li>修正选择硬边后无法复选的问题 (cm=0)</li></ol><h4 id="其他更新" tabindex="-1"><a class="header-anchor" href="#其他更新"><span>其他更新</span></a></h4><ol><li>升级安装脚本 (<code>install.py</code> 和 <code>install.mel</code>),优化各种编码处理</li></ol><h4 id="用户反馈与改进计划" tabindex="-1"><a class="header-anchor" href="#用户反馈与改进计划"><span>用户反馈与改进计划</span></a></h4><ul><li>折边工具改进建议: <ol><li>创建折边时自动添加硬边并生成新折边集</li><li>完成折边赋予后,清理当前对象的所有折边集</li><li>根据对象硬边重建新折边集</li><li>新增功能按钮: - &quot;添加折边并硬化边&quot; - &quot;根据硬边创建折边集&quot;</li></ol></li><li>UV工具优化: <ul><li>修复选中UV边界的剩余问题</li><li>考虑在执行前增加自动展开优化步骤</li></ul></li></ul><h4 id="未来规划" tabindex="-1"><a class="header-anchor" href="#未来规划"><span>未来规划</span></a></h4><ul><li>持续扩展&quot;更多工具&quot;模块,增添实用功能</li><li>根据用户反馈进行针对性改进</li><li>进一步优化代码结构,提升性能和可读性</li></ul><p> </p><h3 id="版本-1-0-1" tabindex="-1"><a class="header-anchor" href="#版本-1-0-1"><span>版本 1.0.1</span></a></h3><ul><li>发布日期: 2024-10-22</li></ul><h4 id="功能修复" tabindex="-1"><a class="header-anchor" href="#功能修复"><span>功能修复</span></a></h4><ul><li>解决Maya中UTF-8编码加载错误</li><li>优化rename和quickrename工具布局</li></ul><h4 id="hugtools安装脚本改进" tabindex="-1"><a class="header-anchor" href="#hugtools安装脚本改进"><span>HUGTools安装脚本改进</span></a></h4><ol><li><p>多语言支持</p><ul><li>新增中英文语言支持</li><li>根据系统设置自动选择显示语言</li></ul></li><li><p>Maya版本检测</p><ul><li>引入 <code>MayaVerObj</code> 类和 <code>get_maya_version()</code> 函数</li><li>新增 <code>check_maya_version()</code> 函数,确保兼容Maya 2022及以上版本</li></ul></li><li><p>安装流程优化</p><ul><li>增设重新安装选项</li><li>改进mod文件的创建和更新逻辑</li><li>强化安装、卸载和重装过程的错误处理和反馈机制</li></ul></li><li><p>兼容性提升</p><ul><li><code>install.mel</code> 中加入UTF-8编码检测,适应不同系统环境</li></ul></li></ol><p> </p><h3 id="版本-1-0-0" tabindex="-1"><a class="header-anchor" href="#版本-1-0-0"><span>版本 1.0.0</span></a></h3><ul><li>发布日期: 2024-10-21</li><li>正式发布HUGTools 1.0.0版本</li><li>完成初步文档部署</li></ul>',28)]))}const d=e(t,[["render",n],["__file","log.html.vue"]]),h=JSON.parse('{"path":"/Doc/log.html","title":"更新日志","lang":"zh-CN","frontmatter":{"title":"更新日志","icon":"fa-solid fa-file-lines","category":["日志"],"tags":["更新记录"],"article":false,"description":"版本 1.0.2 发布日期: 2024-10-23 新功能 工具箱增添\\"更多\\"按钮 打开独立窗口,展示3x3网格的额外工具 在新模块 More_Tools_Module.py 中实现 功能改进 语言切换按钮优化,现可在中英文间切换显示 \\"CN\\" 和 \\"EN\\" 文件读取操作新增 CP437 编码支持 安装过程错误处理和日志记录得到改进 界面更新 主界面布...","head":[["meta",{"property":"og:url","content":"https://megestus.github.io/HUGTools/Doc/log.html"}],["meta",{"property":"og:site_name","content":"HUGToolBox"}],["meta",{"property":"og:title","content":"更新日志"}],["meta",{"property":"og:description","content":"版本 1.0.2 发布日期: 2024-10-23 新功能 工具箱增添\\"更多\\"按钮 打开独立窗口,展示3x3网格的额外工具 在新模块 More_Tools_Module.py 中实现 功能改进 语言切换按钮优化,现可在中英文间切换显示 \\"CN\\" 和 \\"EN\\" 文件读取操作新增 CP437 编码支持 安装过程错误处理和日志记录得到改进 界面更新 主界面布..."}],["meta",{"property":"og:type","content":"website"}],["meta",{"property":"og:locale","content":"zh-CN"}],["meta",{"property":"og:updated_time","content":"2024-10-24T15:04:15.000Z"}],["meta",{"property":"article:tag","content":"更新记录"}],["meta",{"property":"article:modified_time","content":"2024-10-24T15:04:15.000Z"}],["script",{"type":"application/ld+json"},"{\\"@context\\":\\"https://schema.org\\",\\"@type\\":\\"WebPage\\",\\"name\\":\\"更新日志\\",\\"description\\":\\"版本 1.0.2 发布日期: 2024-10-23 新功能 工具箱增添\\\\\\"更多\\\\\\"按钮 打开独立窗口,展示3x3网格的额外工具 在新模块 More_Tools_Module.py 中实现 功能改进 语言切换按钮优化,现可在中英文间切换显示 \\\\\\"CN\\\\\\" 和 \\\\\\"EN\\\\\\" 文件读取操作新增 CP437 编码支持 安装过程错误处理和日志记录得到改进 界面更新 主界面布...\\"}"]]},"headers":[{"level":3,"title":"版本 1.0.2","slug":"版本-1-0-2","link":"#版本-1-0-2","children":[]},{"level":3,"title":"版本 1.0.1","slug":"版本-1-0-1","link":"#版本-1-0-1","children":[]},{"level":3,"title":"版本 1.0.0","slug":"版本-1-0-0","link":"#版本-1-0-0","children":[]}],"git":{"createdTime":1729608863000,"updatedTime":1729782255000,"contributors":[{"name":"Megestus","email":"75190962+Megestus@users.noreply.github.com","commits":4}]},"readingTime":{"minutes":2.23,"words":668},"filePathRelative":"Doc/log.md","localizedDate":"2024年10月22日","autoDesc":true,"excerpt":"<h3>版本 1.0.2</h3>\\n<ul>\\n<li>发布日期: 2024-10-23</li>\\n</ul>\\n<h4>新功能</h4>\\n<ol>\\n<li>工具箱增添\\"更多\\"按钮\\n<ul>\\n<li>打开独立窗口,展示3x3网格的额外工具</li>\\n<li>在新模块 <code>More_Tools_Module.py</code> 中实现</li>\\n</ul>\\n</li>\\n</ol>\\n<h4>功能改进</h4>\\n<ol>\\n<li>语言切换按钮优化,现可在中英文间切换显示 \\"CN\\" 和 \\"EN\\"</li>\\n<li>文件读取操作新增 CP437 编码支持</li>\\n<li>安装过程错误处理和日志记录得到改进</li>\\n</ol>"}');export{d as comp,h as data};