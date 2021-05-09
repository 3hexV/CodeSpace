0.简介：
	使用Flask作为后端，BootStrap3作为前端，使用REST架构，实现的本地代码仓库。
	使用tkinter实现GUI界面。
	代码上传后会被压缩，下载时，下载压缩后的压缩包。
	支持若GoogleHack搜索语法（非常简单的搜索，本地仓库，代码数不会很大）
1.环境：
	python 3.8.3
	MongoDB 3.6.19
2.依赖：
	在requirements.txt中
	使用下面命令安装CodeSpace所需要的依赖包
		pip install -r requirements.txt
3.运行：
	运行CodeSpace.exe即可
4.其他
	打开 http://127.0.0.1:5000/ 即可使用
	4.1使用Robomongo 可视化工具查看MongoDB
	4.2如果将MongoDB的服务，注册到系统服务中，可以使用脚本(管理员)启动:
		./mongodb_bat/MongoDB Service Manager.bat
	4.3各类.ini配置文件，见代码注释
	4.4./CodeSpace/uploads 内为上传的压缩后的文件的位置
5.使用：
	主界面，按下快捷键~添加条目，在按~退出（不清空），ESC清空并退出添加
	在搜索界面输入关键词（关键词检索位置在范围在<代码名，代码介绍>两个属性中）
	添加条目界面，Enter提交
	主界面（无添加条目界面），Enter查找
	主界面刷新按钮点击后，刷新仓库内的代码条目数
	
	
	